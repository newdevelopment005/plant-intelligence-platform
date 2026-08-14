import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.meeting.api.schemas import (
    AttendeeResponse,
    CreateMeetingRequest,
    MeetingListItemResponse,
    MeetingResponse,
    PaginatedMeetingsResponse,
    UpdateAttendeeStatusRequest,
    UpdateMeetingRequest,
)
from app.modules.meeting.domain.use_cases import (
    CreateMeetingUseCase,
    DeleteMeetingUseCase,
    GetMeetingUseCase,
    ListMeetingsUseCase,
    UpdateAttendeeStatusUseCase,
    UpdateMeetingUseCase,
)
from app.modules.meeting.infrastructure.repositories import (
    MeetingAttendeeRepository,
    MeetingRepository,
)

logger = structlog.get_logger()
router = APIRouter(redirect_slashes=False)


def _get_meeting_repo(db: AsyncSession) -> MeetingRepository:
    return MeetingRepository(db)


def _get_attendee_repo(db: AsyncSession) -> MeetingAttendeeRepository:
    return MeetingAttendeeRepository(db)


async def _notify_attendees(db: AsyncSession, meeting_id: str, meeting_title: str, starts_at: str, location: str | None, invite: bool = False, inviter_name: str = "") -> None:
    from app.core.email import resolve_smtp_for_user, send_meeting_invite, send_meeting_reminder
    from app.modules.auth.infrastructure.repositories import UserRepository

    attendee_repo = _get_attendee_repo(db)
    attendees = await attendee_repo.list_by_meeting(meeting_id)

    recipients: dict[str, dict | None] = {}
    for a in attendees:
        if a and a.email:
            recipients[a.email] = None
        if a.user_id:
            smtp = await resolve_smtp_for_user(db, str(a.user_id))
            user = None
            if a.email is None:
                user = await UserRepository(db).get_by_id(str(a.user_id))
                email = user.email if user else None
                if email:
                    recipients[email] = smtp
            else:
                recipients[a.email] = smtp or recipients.get(a.email)

    deliver = send_meeting_invite if invite else send_meeting_reminder
    for email, smtp in recipients.items():
        if invite:
            deliver(
                to_email=email,
                inviter_name=inviter_name,
                meeting_title=meeting_title,
                starts_at_iso=starts_at,
                location=location,
                base_url="https://plant-intelligence-platform.vercel.app",
                smtp=smtp,
            )
        else:
            deliver(
                to_email=email,
                meeting_title=meeting_title,
                starts_at_iso=starts_at,
                location=location,
                base_url="https://plant-intelligence-platform.vercel.app",
                smtp=smtp,
            )


@router.get("", response_model=PaginatedMeetingsResponse)
async def list_meetings(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    upcoming_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    use_case = ListMeetingsUseCase(_get_meeting_repo(db), _get_attendee_repo(db))
    return await use_case.execute(
        user_id=current_user["id"],
        upcoming_only=upcoming_only,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=MeetingResponse, status_code=201)
async def create_meeting(
    body: CreateMeetingRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = CreateMeetingUseCase(_get_meeting_repo(db), _get_attendee_repo(db))
    result = await use_case.execute(
        title=body.title,
        creator_id=current_user["id"],
        starts_at=body.starts_at,
        ends_at=body.ends_at,
        description=body.description,
        location=body.location,
        meeting_link=body.meeting_link,
        reminder_option=body.reminder_option,
        attendee_emails=[str(e) for e in body.attendee_emails] if body.attendee_emails else None,
    )
    logger.info(
        "meeting_created",
        meeting_id=result["id"],
        user_id=current_user["id"],
    )
    get_use_case = GetMeetingUseCase(_get_meeting_repo(db), _get_attendee_repo(db))
    result = await get_use_case.execute(meeting_id=result["id"], user_id=current_user["id"])

    await _notify_attendees(
        db,
        meeting_id=result["id"],
        meeting_title=result["title"],
        starts_at=result["starts_at"],
        location=result.get("location"),
        invite=True,
        inviter_name=current_user.get("full_name") or current_user.get("email") or "The organizer",
    )
    return result


@router.post("/{meeting_id}/send-reminders")
async def send_reminders(
    meeting_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.meeting.domain.models import MeetingModel

    meeting_repo = _get_meeting_repo(db)
    meeting = await meeting_repo.get_by_id(meeting_id)
    if not meeting:
        from app.core.exceptions import NotFoundException

        raise NotFoundException("Meeting", meeting_id)
    if str(meeting.created_by) != current_user["id"]:
        from app.core.exceptions import ValidationException

        raise ValidationException("Only the organizer can send reminders")

    await _notify_attendees(
        db,
        meeting_id=meeting_id,
        meeting_title=meeting.title,
        starts_at=meeting.starts_at.isoformat(),
        location=meeting.location,
    )
    meeting.reminder_sent = True
    await meeting_repo.update(meeting)
    return {"message": "Reminders sent"}


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetMeetingUseCase(_get_meeting_repo(db), _get_attendee_repo(db))
    return await use_case.execute(meeting_id=meeting_id, user_id=current_user["id"])


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    body: UpdateMeetingRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UpdateMeetingUseCase(_get_meeting_repo(db), _get_attendee_repo(db))
    await use_case.execute(
        meeting_id=meeting_id,
        user_id=current_user["id"],
        title=body.title,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
        description=body.description,
        location=body.location,
        meeting_link=body.meeting_link,
        reminder_option=body.reminder_option,
    )
    get_use_case = GetMeetingUseCase(_get_meeting_repo(db), _get_attendee_repo(db))
    return await get_use_case.execute(meeting_id=meeting_id, user_id=current_user["id"])


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = DeleteMeetingUseCase(_get_meeting_repo(db), _get_attendee_repo(db))
    await use_case.execute(meeting_id=meeting_id, user_id=current_user["id"])


@router.put("/{meeting_id}/attendees/{attendee_id}", response_model=AttendeeResponse)
async def update_attendee_status(
    meeting_id: str,
    attendee_id: str,
    body: UpdateAttendeeStatusRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UpdateAttendeeStatusUseCase(_get_meeting_repo(db), _get_attendee_repo(db))
    return await use_case.execute(
        meeting_id=meeting_id,
        attendee_id=attendee_id,
        user_id=current_user["id"],
        status=body.status,
        user_email=current_user.get("email"),
    )