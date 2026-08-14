from abc import ABC, abstractmethod

from app.modules.sharing.domain.models import ShareModel, ShareRecipientModel


class ShareRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, share: ShareModel) -> ShareModel: ...

    @abstractmethod
    async def get_by_id(self, share_id: str) -> ShareModel | None: ...

    @abstractmethod
    async def get_by_token(self, token: str) -> ShareModel | None: ...

    @abstractmethod
    async def list_my_shares(self, owner_id: str) -> list[ShareModel]: ...

    @abstractmethod
    async def delete(self, share_id: str) -> bool: ...


class ShareRecipientRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, recipient: ShareRecipientModel) -> ShareRecipientModel: ...

    @abstractmethod
    async def create_many(self, recipients: list[ShareRecipientModel]) -> list[ShareRecipientModel]: ...

    @abstractmethod
    async def list_by_share(self, share_id: str) -> list[ShareRecipientModel]: ...

    @abstractmethod
    async def list_shared_with_user(
        self,
        user_id: str,
        team_ids: list[str] | None = None,
        department_ids: list[str] | None = None,
    ) -> list[ShareRecipientModel]: ...

    @abstractmethod
    async def list_user_memberships(self, user_id: str) -> dict: ...

    @abstractmethod
    async def delete_by_share(self, share_id: str) -> bool: ...

    @abstractmethod
    async def delete_for_user(self, share_id: str, user_id: str) -> bool: ...
