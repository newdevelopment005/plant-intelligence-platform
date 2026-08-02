from abc import ABC, abstractmethod

from app.modules.auth.domain.password_reset_model import PasswordResetTokenModel
from app.modules.auth.domain.token_model import RefreshTokenModel


class TokenRepositoryInterface(ABC):
    @abstractmethod
    async def save_refresh_token(self, token: RefreshTokenModel) -> RefreshTokenModel:
        pass

    @abstractmethod
    async def get_refresh_token(self, token_hash: str) -> RefreshTokenModel | None:
        pass

    @abstractmethod
    async def revoke_refresh_token(self, token_hash: str) -> bool:
        pass

    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: str) -> int:
        pass

    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        pass


class PasswordResetRepositoryInterface(ABC):
    @abstractmethod
    async def save_token(self, token: PasswordResetTokenModel) -> PasswordResetTokenModel:
        pass

    @abstractmethod
    async def get_valid_token(self, token_hash: str) -> PasswordResetTokenModel | None:
        pass

    @abstractmethod
    async def mark_used(self, token_id: str) -> bool:
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        pass
