import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.meeting.domain.interfaces import (
    MeetingAttendeeRepositoryInterface,
    MeetingRepositoryInterface,
)
from app.modules.meeting.domain.models import (
    MeetingAttendeeModel,
    MeetingModel,
)


class MeetingRepository(MeetingRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, meeting_id: str) -> MeetingModel | None:
        result = await self.db.execute(
            select(MeetingModel).where(MeetingModel.id == meeting_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: str,
        upcoming_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MeetingModel]:
        from app.modules.auth.domain.models import UserModel

        stmt = (
            select(MeetingModel)
            .where(
                or_(
                    MeetingModel.created_by == user_id,
                    MeetingModel.id.in_(
                        select(MeetingAttendeeModel.meeting_id).where(
                            MeetingAttendeeModel.user_id == user_id
                        )
                    ),
                )
            )
            .order_by(MeetingModel.starts_at.asc())
            .offset(skip)
            .limit(limit)
        )
        if upcoming_only:
            stmt = stmt.where(MeetingModel.starts_at >= datetime.now(UTC))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, meeting: MeetingModel) -> MeetingModel:
        self.db.add(meeting)
        await self.db.flush()
        await self.db.refresh(meeting)
        return meeting

    async def update(self, meeting: MeetingModel) -> MeetingModel:
        meeting.updated_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(meeting)
        return meeting

    async def delete(self, meeting_id: str) -> bool:
        meeting = await self.get_by_id(meeting_id)
        if not meeting:
            return False
        await self.db.delete(meeting)
        await self.db.flush()
        return True

    async def list_meetings_needing_reminders(self) -> list[MeetingModel]:
        now = datetime.now(UTC)
        window_end = now + timedelta(minutes=24 * 60)
        result = await self.db.execute(
            select(MeetingModel).where(
                MeetingModel.reminder_sent.is_(False),
                MeetingModel.starts_at >= now,
                MeetingModel.starts_at <= window_end,
            )
        )
        return list(result.scalars().all())


class MeetingAttendeeRepository(MeetingAttendeeRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_meeting(self, meeting_id: str) -> list[MeetingAttendeeModel]:
        result = await self.db.execute(
            select(MeetingAttendeeModel)
            .where(MeetingAttendeeModel.meeting_id == meeting_id)
            .order_by(MeetingAttendeeModel.invited_at)
        )
        return list(result.scalars().all())

    async def create_many(
        self, attendees: list[MeetingAttendeeModel]
    ) -> list[MeetingAttendeeModel]:
        if not attendees:
            return []
        for a in attendees:
            self.db.add(a)
        await self.db.flush()
        for a in attendees:
            await self.db.refresh(a)
        return attendees

    async def update_status(
        self, attendee_id: str, status: str, user_id: str
    ) -> MeetingAttendeeModel | None:
        result = await self.db.execute(
            select(MeetingAttendeeModel).where(
                MeetingAttendeeModel.id == attendee_id,
                MeetingAttendeeModel.user_id == user_id,
            )
        )
        attendee = result.scalar_one_or_none()
        if not attendee:
            return None
        attendee.status = status
        attendee.acknowledged_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(attendee)
        return attendee

    async def delete_by_meeting(self, meeting_id: str) -> bool:
        result = await self.db.execute(
            select(MeetingAttendeeModel).where(
                MeetingAttendeeModel.meeting_id == meeting_id
            )
        )
        attendees = list(result.scalars().all())
        for a in attendees:
            await self.db.delete(a)
        await self.db.flush()
        return True

    async def list_by_user_for_meeting(
        self, meeting_id: str, user_id: str
    ) -> MeetingAttendeeModel | None:
        result = await self.db.execute(
            select(MeetingAttendeeModel).where(
                MeetingAttendeeModel.meeting_id == meeting_id,
                MeetingAttendeeModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()