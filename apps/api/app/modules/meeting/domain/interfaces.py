from abc import ABC, abstractmethod

from app.modules.meeting.domain.models import (
    MeetingAttendeeModel,
    MeetingModel,
)


class MeetingRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, meeting_id: str) -> MeetingModel | None:
        pass

    @abstractmethod
    async def list_for_user(
        self, user_id: str, upcoming_only: bool = False, skip: int = 0, limit: int = 100
    ) -> list[MeetingModel]:
        pass

    @abstractmethod
    async def create(self, meeting: MeetingModel) -> MeetingModel:
        pass

    @abstractmethod
    async def update(self, meeting: MeetingModel) -> MeetingModel:
        pass

    @abstractmethod
    async def delete(self, meeting_id: str) -> bool:
        pass

    @abstractmethod
    async def list_meetings_needing_reminders(self) -> list[MeetingModel]:
        pass


class MeetingAttendeeRepositoryInterface(ABC):
    @abstractmethod
    async def list_by_meeting(self, meeting_id: str) -> list[MeetingAttendeeModel]:
        pass

    @abstractmethod
    async def create_many(
        self, attendees: list[MeetingAttendeeModel]
    ) -> list[MeetingAttendeeModel]:
        pass

    @abstractmethod
    async def update_status(
        self, attendee_id: str, status: str, user_id: str
    ) -> MeetingAttendeeModel | None:
        pass

    @abstractmethod
    async def delete_by_meeting(self, meeting_id: str) -> bool:
        pass

    @abstractmethod
    async def list_by_user_for_meeting(
        self, meeting_id: str, user_id: str
    ) -> MeetingAttendeeModel | None:
        pass