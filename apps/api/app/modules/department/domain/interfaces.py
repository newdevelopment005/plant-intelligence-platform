from abc import ABC, abstractmethod

from app.modules.department.domain.models import DepartmentMemberModel, DepartmentModel


class DepartmentRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, department_id: str) -> DepartmentModel | None:
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        include_inactive: bool = False,
    ) -> list[DepartmentModel]:
        pass

    @abstractmethod
    async def count_all(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def create(self, department: DepartmentModel) -> DepartmentModel:
        pass

    @abstractmethod
    async def update(self, department: DepartmentModel) -> DepartmentModel:
        pass

    @abstractmethod
    async def delete(self, department_id: str) -> bool:
        pass


class DepartmentMemberRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_department_and_user(
        self, department_id: str, user_id: str
    ) -> DepartmentMemberModel | None:
        pass

    @abstractmethod
    async def add_member(self, member: DepartmentMemberModel) -> DepartmentMemberModel:
        pass

    @abstractmethod
    async def update_role(
        self, department_id: str, user_id: str, role: str
    ) -> DepartmentMemberModel | None:
        pass

    @abstractmethod
    async def remove_member(self, department_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def list_members(self, department_id: str) -> list[DepartmentMemberModel]:
        pass