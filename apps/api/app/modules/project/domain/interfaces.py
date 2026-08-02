from abc import ABC, abstractmethod

from app.modules.project.domain.models import ProjectMemberModel, ProjectModel


class ProjectRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: str) -> ProjectModel | None:
        pass

    @abstractmethod
    async def create(self, project: ProjectModel) -> ProjectModel:
        pass

    @abstractmethod
    async def update(self, project: ProjectModel) -> ProjectModel:
        pass

    @abstractmethod
    async def delete(self, project_id: str) -> bool:
        pass

    @abstractmethod
    async def list_by_owner(
        self, owner_id: str, skip: int = 0, limit: int = 100
    ) -> list[ProjectModel]:
        pass

    @abstractmethod
    async def list_by_member(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[ProjectModel]:
        pass

    @abstractmethod
    async def list_all(
        self, skip: int = 0, limit: int = 100, status: str | None = None
    ) -> list[ProjectModel]:
        pass

    @abstractmethod
    async def count_by_owner(self, owner_id: str) -> int:
        pass

    @abstractmethod
    async def count_by_member(self, user_id: str) -> int:
        pass

    @abstractmethod
    async def count_all(self, status: str | None = None) -> int:
        pass

    @abstractmethod
    async def search(
        self, query: str, user_id: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[ProjectModel]:
        pass


class ProjectMemberRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_project_and_user(
        self, project_id: str, user_id: str
    ) -> ProjectMemberModel | None:
        pass

    @abstractmethod
    async def add_member(self, member: ProjectMemberModel) -> ProjectMemberModel:
        pass

    @abstractmethod
    async def update_member_role(
        self, project_id: str, user_id: str, role: str
    ) -> ProjectMemberModel | None:
        pass

    @abstractmethod
    async def remove_member(self, project_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def list_members(self, project_id: str) -> list[ProjectMemberModel]:
        pass

    @abstractmethod
    async def count_members(self, project_id: str) -> int:
        pass
