from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.password_reset_model import PasswordResetTokenModel
from app.modules.auth.domain.token_interfaces import PasswordResetRepositoryInterface


class PasswordResetRepository(PasswordResetRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_token(self, token: PasswordResetTokenModel) -> PasswordResetTokenModel:
        self.db.add(token)
        await self.db.flush()
        await self.db.refresh(token)
        return token

    async def get_valid_token(self, token_hash: str) -> PasswordResetTokenModel | None:
        result = await self.db.execute(
            select(PasswordResetTokenModel).where(
                PasswordResetTokenModel.token_hash == token_hash,
                ~PasswordResetTokenModel.used,
            )
        )
        return result.scalar_one_or_none()

    async def mark_used(self, token_id: str) -> bool:
        result = await self.db.execute(
            update(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.id == token_id)
            .values(used=True)
        )
        return result.rowcount > 0

    async def cleanup_expired(self) -> int:
        result = await self.db.execute(
            update(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.expires_at < datetime.now(UTC))
            .values(used=True)
        )
        return result.rowcount
