from datetime import UTC, datetime, timedelta

from app.core.email import resolve_smtp_for_user, send_meeting_reminder
from app.database import async_session_factory
from app.modules.meeting.infrastructure.repositories import (
    MeetingAttendeeRepository,
    MeetingRepository,
)

BASE_URL = "https://plant-intelligence-platform.vercel.app"


async def _attendee_emails(db, attendees) -> list[tuple[str, dict | None]]:
    """Return (email, smtp_override) tuples for every attendee."""
    from app.modules.auth.infrastructure.repositories import UserRepository

    result: list[tuple[str, dict | None]] = []
    for attendee in attendees:
        if not attendee.email and not attendee.user_id:
            continue
        email = attendee.email
        smtp = None
        if attendee.user_id:
            smtp = await resolve_smtp_for_user(db, str(attendee.user_id))
            if not email:
                user = await UserRepository(db).get_by_id(str(attendee.user_id))
                email = user.email if user else None
        if email:
            result.append((email, smtp))
    return result


async def send_due_meeting_reminders() -> dict:
    """Send reminder emails for meetings inside their reminder window.

    Reusable core used by both the Celery beat task and the in-process
    scheduler. Runs once per minute. Reminders that were missed while the
    scheduler was down are caught up within the query's look-back window.
    """
    async with async_session_factory() as db:
        meeting_repo = MeetingRepository(db)
        attendee_repo = MeetingAttendeeRepository(db)

        now = datetime.now(UTC)
        due = await meeting_repo.list_meetings_needing_reminders()

        notified = 0
        for meeting in due:
            if meeting.reminder_sent:
                continue
            minutes = meeting.reminder_minutes_before or 0
            starts_at = meeting.starts_at

            if minutes == 0:
                # "at_time": remind exactly as the meeting starts. Use a
                # one-minute lead-in window so a single beat tick lands.
                if not (
                    starts_at - timedelta(minutes=1)
                    <= now
                    <= starts_at + timedelta(minutes=30)
                ):
                    continue
            else:
                reminder_at = starts_at - timedelta(minutes=minutes)
                if not (reminder_at <= now <= starts_at):
                    continue

            attendees = await attendee_repo.list_by_meeting(str(meeting.id))
            recipients = await _attendee_emails(db, attendees)

            for email, smtp in recipients:
                send_meeting_reminder(
                    to_email=email,
                    meeting_title=meeting.title,
                    starts_at_iso=starts_at.isoformat(),
                    location=meeting.location,
                    base_url=BASE_URL,
                    smtp=smtp,
                )

            meeting.reminder_sent = True
            await meeting_repo.update(meeting)
            notified += 1

        await db.commit()
        return {"meetings_notified": notified}


def send_meeting_reminders():
    """Celery beat entry point that wraps the async reminder core."""
    import asyncio

    return asyncio.run(send_due_meeting_reminders())