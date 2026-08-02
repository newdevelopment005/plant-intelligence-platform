from abc import ABC, abstractmethod

from app.modules.auth.domain.models import UserModel


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserModel | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserModel | None:
        pass

    @abstractmethod
    async def create(self, user: UserModel) -> UserModel:
        pass

    @abstractmethod
    async def update(self, user: UserModel) -> UserModel:
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        pass

    @abstractmethod
    async def list_users(
        self, skip: int = 0, limit: int = 100, role: str | None = None
    ) -> list[UserModel]:
        pass

    @abstractmethod
    async def count_users(self) -> int:
        pass
