import uuid as _uuid
from datetime import UTC, datetime

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.meeting.domain.interfaces import (
    MeetingAttendeeRepositoryInterface,
    MeetingRepositoryInterface,
)
from app.modules.meeting.domain.models import (
    MeetingAttendeeModel,
    MeetingModel,
)

VALID_REMINDER_OPTIONS = (
    "at_time", "5m", "10m", "15m", "30m", "1h", "1d",
)

VALID_ATTENDEE_STATUS = ("pending", "accepted", "declined")


def _reminder_minutes(option: str | None) -> int:
    if not option or option == "at_time":
        return 0
    if option == "5m":
        return 5
    if option == "10m":
        return 10
    if option == "15m":
        return 15
    if option == "30m":
        return 30
    if option == "1h":
        return 60
    if option == "1d":
        return 1440
    raise ValidationException(f"Invalid reminder option: {option}")


class CreateMeetingUseCase:
    def __init__(
        self,
        meeting_repo: MeetingRepositoryInterface,
        attendee_repo: MeetingAttendeeRepositoryInterface,
    ):
        self.meeting_repo = meeting_repo
        self.attendee_repo = attendee_repo

    async def execute(
        self,
        title: str,
        creator_id: str,
        starts_at: datetime,
        ends_at: datetime | None = None,
        description: str | None = None,
        location: str | None = None,
        meeting_link: str | None = None,
        reminder_option: str | None = None,
        attendee_emails: list[str] | None = None,
    ) -> dict:
        self._validate_title(title)
        if not starts_at:
            raise ValidationException("Meeting start time is required")

        if reminder_option and reminder_option not in VALID_REMINDER_OPTIONS:
            raise ValidationException(
                f"Invalid reminder option. Must be one of: {', '.join(VALID_REMINDER_OPTIONS)}"
            )

        meeting = MeetingModel(
            id=_uuid.uuid4(),
            title=title.strip(),
            description=description.strip() if description else None,
            starts_at=starts_at,
            ends_at=ends_at,
            location=location.strip() if location else None,
            meeting_link=meeting_link.strip() if meeting_link else None,
            reminder_minutes_before=_reminder_minutes(reminder_option),
            reminder_sent=False,
            created_by=creator_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        meeting = await self.meeting_repo.create(meeting)

        attendees = []
        if attendee_emails:
            attendees = await self._add_attendees(meeting.id, attendee_emails)

        return {"id": str(meeting.id), "attendees": attendees}

    async def _add_attendees(self, meeting_id, emails) -> list[MeetingAttendeeModel]:
        from app.modules.auth.infrastructure.repositories import UserRepository

        attendees = []
        for email in emails:
            email = email.strip().lower()
            if not email:
                continue
            attendee = MeetingAttendeeModel(
                id=_uuid.uuid4(),
                meeting_id=meeting_id,
                user_id=None,
                email=email,
                status="pending",
                invited_at=datetime.now(UTC),
            )
            attendees.append(attendee)
        if not attendees:
            return []
        return await self.attendee_repo.create_many(attendees)

    def _validate_title(self, title: str) -> None:
        if not title or not title.strip():
            raise ValidationException("Meeting title is required")
        if len(title.strip()) < 3:
            raise ValidationException("Meeting title must be at least 3 characters")
        if len(title.strip()) > 255:
            raise ValidationException("Meeting title must be less than 255 characters")


class UpdateMeetingUseCase:
    def __init__(
        self,
        meeting_repo: MeetingRepositoryInterface,
        attendee_repo: MeetingAttendeeRepositoryInterface,
    ):
        self.meeting_repo = meeting_repo
        self.attendee_repo = attendee_repo

    async def execute(
        self,
        meeting_id: str,
        user_id: str,
        title: str | None = None,
        starts_at: datetime | None = None,
        ends_at: datetime | None = None,
        description: str | None = None,
        location: str | None = None,
        meeting_link: str | None = None,
        reminder_option: str | None = None,
    ) -> dict:
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise NotFoundException("Meeting", meeting_id)
        if str(meeting.created_by) != user_id:
            raise ValidationException("Only the meeting organizer can update it")

        if title is not None:
            self._validate_title(title)
            meeting.title = title.strip()
        if starts_at is not None:
            meeting.starts_at = starts_at
        if ends_at is not None:
            meeting.ends_at = ends_at
        if description is not None:
            meeting.description = description.strip() if description.strip() else None
        if location is not None:
            meeting.location = location.strip() if location.strip() else None
        if meeting_link is not None:
            meeting.meeting_link = meeting_link.strip() if meeting_link.strip() else None
        if reminder_option is not None:
            if reminder_option not in VALID_REMINDER_OPTIONS:
                raise ValidationException(
                    f"Invalid reminder option. Must be one of: {', '.join(VALID_REMINDER_OPTIONS)}"
                )
            meeting.reminder_minutes_before = _reminder_minutes(reminder_option)
            meeting.reminder_sent = False

        return await self.meeting_repo.update(meeting)

    def _validate_title(self, title: str) -> None:
        if not title or not title.strip():
            raise ValidationException("Meeting title is required")
        if len(title.strip()) < 3:
            raise ValidationException("Meeting title must be at least 3 characters")
        if len(title.strip()) > 255:
            raise ValidationException("Meeting title must be less than 255 characters")


class DeleteMeetingUseCase:
    def __init__(
        self,
        meeting_repo: MeetingRepositoryInterface,
        attendee_repo: MeetingAttendeeRepositoryInterface,
    ):
        self.meeting_repo = meeting_repo
        self.attendee_repo = attendee_repo

    async def execute(self, meeting_id: str, user_id: str) -> dict:
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise NotFoundException("Meeting", meeting_id)
        if str(meeting.created_by) != user_id:
            raise ValidationException("Only the meeting organizer can delete it")
        await self.attendee_repo.delete_by_meeting(meeting_id)
        await self.meeting_repo.delete(meeting_id)
        return {"message": "Meeting deleted"}


class ListMeetingsUseCase:
    def __init__(
        self,
        meeting_repo: MeetingRepositoryInterface,
        attendee_repo: MeetingAttendeeRepositoryInterface,
    ):
        self.meeting_repo = meeting_repo
        self.attendee_repo = attendee_repo

    async def execute(
        self,
        user_id: str,
        upcoming_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        meetings = await self.meeting_repo.list_for_user(
            user_id, upcoming_only=upcoming_only, skip=skip, limit=limit
        )
        total = len(meetings)

        items = []
        for meeting in meetings:
            items.append(await self._to_dict(meeting))

        return {"items": items, "total": total, "skip": skip, "limit": limit}

    async def _to_dict(self, meeting: MeetingModel) -> dict:
        return {
            "id": str(meeting.id),
            "title": meeting.title,
            "description": meeting.description,
            "starts_at": meeting.starts_at.isoformat(),
            "ends_at": meeting.ends_at.isoformat() if meeting.ends_at else None,
            "location": meeting.location,
            "meeting_link": meeting.meeting_link,
            "reminder_minutes_before": meeting.reminder_minutes_before,
            "created_by": str(meeting.created_by),
            "created_at": meeting.created_at.isoformat(),
            "updated_at": meeting.updated_at.isoformat(),
        }


class GetMeetingUseCase:
    def __init__(
        self,
        meeting_repo: MeetingRepositoryInterface,
        attendee_repo: MeetingAttendeeRepositoryInterface,
    ):
        self.meeting_repo = meeting_repo
        self.attendee_repo = attendee_repo

    async def execute(self, meeting_id: str, user_id: str) -> dict:
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise NotFoundException("Meeting", meeting_id)

        is_creator = str(meeting.created_by) == user_id
        attendance = await self.attendee_repo.list_by_user_for_meeting(meeting_id, user_id)
        is_invited = attendance is not None
        if not is_creator and not is_invited:
            raise NotFoundException("Meeting", meeting_id)

        attendees = await self.attendee_repo.list_by_meeting(meeting_id)
        return {
            "id": str(meeting.id),
            "title": meeting.title,
            "description": meeting.description,
            "starts_at": meeting.starts_at.isoformat(),
            "ends_at": meeting.ends_at.isoformat() if meeting.ends_at else None,
            "location": meeting.location,
            "meeting_link": meeting.meeting_link,
            "reminder_minutes_before": meeting.reminder_minutes_before,
            "created_by": str(meeting.created_by),
            "created_at": meeting.created_at.isoformat(),
            "updated_at": meeting.updated_at.isoformat(),
            "attendees": [
                {
                    "id": str(a.id),
                    "user_id": str(a.user_id) if a.user_id else None,
                    "email": a.email,
                    "status": a.status,
                    "invited_at": a.invited_at.isoformat(),
                }
                for a in attendees
            ],
        }


class UpdateAttendeeStatusUseCase:
    def __init__(
        self,
        meeting_repo: MeetingRepositoryInterface,
        attendee_repo: MeetingAttendeeRepositoryInterface,
    ):
        self.meeting_repo = meeting_repo
        self.attendee_repo = attendee_repo

    async def execute(
        self, meeting_id: str, attendee_id: str, user_id: str, status: str
    ) -> dict:
        if status not in VALID_ATTENDEE_STATUS:
            raise ValidationException(
                f"Invalid status. Must be one of: {', '.join(VALID_ATTENDEE_STATUS)}"
            )

        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise NotFoundException("Meeting", meeting_id)

        attendee = await self.attendee_repo.update_status(attendee_id, status, user_id)
        if not attendee:
            raise NotFoundException("Invitation", attendee_id)

        return {"message": f"Invitation {status}"}