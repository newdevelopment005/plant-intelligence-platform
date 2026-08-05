from abc import ABC, abstractmethod

from app.modules.team.domain.models import TeamMemberModel, TeamModel


class TeamRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, team_id: str) -> TeamModel | None:
        pass

    @abstractmethod
    async def create(self, team: TeamModel) -> TeamModel:
        pass

    @abstractmethod
    async def delete(self, team_id: str) -> bool:
        pass

    @abstractmethod
    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[TeamModel]:
        pass


class TeamMemberRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_team_and_user(
        self, team_id: str, user_id: str
    ) -> TeamMemberModel | None:
        pass

    @abstractmethod
    async def add_member(self, member: TeamMemberModel) -> TeamMemberModel:
        pass

    @abstractmethod
    async def remove_member(self, team_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def list_members(self, team_id: str) -> list[TeamMemberModel]:
        pass
