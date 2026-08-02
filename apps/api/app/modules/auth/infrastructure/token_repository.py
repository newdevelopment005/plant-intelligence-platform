from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.token_interfaces import TokenRepositoryInterface
from app.modules.auth.domain.token_model import RefreshTokenModel


class TokenRepository(TokenRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_refresh_token(self, token: RefreshTokenModel) -> RefreshTokenModel:
        self.db.add(token)
        await self.db.flush()
        await self.db.refresh(token)
        return token

    async def get_refresh_token(self, token_hash: str) -> RefreshTokenModel | None:
        result = await self.db.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token_hash == token_hash,
                ~RefreshTokenModel.revoked,
            )
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_hash: str) -> bool:
        result = await self.db.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .values(revoked=True)
        )
        return result.rowcount > 0

    async def revoke_all_user_tokens(self, user_id: str) -> int:
        result = await self.db.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                ~RefreshTokenModel.revoked,
            )
            .values(revoked=True)
        )
        return result.rowcount

    async def cleanup_expired_tokens(self) -> int:
        result = await self.db.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.expires_at < datetime.now(UTC))
            .values(revoked=True)
        )
        return result.rowcount
