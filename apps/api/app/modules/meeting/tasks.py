from datetime import UTC, datetime, timedelta

from app.core.celery import celery_app
from app.core.email import send_meeting_reminder
from app.database import async_session_factory
from app.modules.meeting.infrastructure.repositories import (
    MeetingAttendeeRepository,
    MeetingRepository,
)

BASE_URL = "https://plant-intelligence-platform.vercel.app"


@celery_app.task(name="app.modules.meeting.tasks.send_meeting_reminders")
def send_meeting_reminders():
    """Send reminder emails for meetings starting within their reminder window.

    Runs every minute via Celery beat. Only meetings whose reminder has not yet
    been sent and whose start time falls inside the configured
    ``reminder_minutes_before`` window are notified.
    """
    import asyncio

    async def _run():
        async with async_session_factory() as db:
            meeting_repo = MeetingRepository(db)
            attendee_repo = MeetingAttendeeRepository(db)

            now = datetime.now(UTC)
            due = await meeting_repo.list_meetings_needing_reminders()

            notified = 0
            for meeting in due:
                if meeting.reminder_sent:
                    continue
                reminder_at = meeting.starts_at - timedelta(
                    minutes=meeting.reminder_minutes_before
                )
                if not (reminder_at <= now <= meeting.starts_at):
                    continue

                attendees = await attendee_repo.list_by_meeting(str(meeting.id))
                emails = {a.email for a in attendees if a and a.email}

                for attendee in attendees:
                    if attendee.user_id:
                        from app.modules.auth.infrastructure.repositories import UserRepository

                        user = await UserRepository(db).get_by_id(str(attendee.user_id))
                        if user and user.email:
                            emails.add(user.email)

                for email in emails:
                    send_meeting_reminder(
                        to_email=email,
                        meeting_title=meeting.title,
                        starts_at_iso=meeting.starts_at.isoformat(),
                        location=meeting.location,
                        base_url=BASE_URL,
                    )

                meeting.reminder_sent = True
                await meeting_repo.update(meeting)
                notified += 1

            await db.commit()
            return {"meetings_notified": notified}

    return asyncio.run(_run())
