import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from app.core.exceptions import AppException
from app.core.security import get_password_hash, verify_password
from app.modules.auth.domain.interfaces import UserRepositoryInterface
from app.modules.auth.domain.password_reset_model import PasswordResetTokenModel
from app.modules.auth.domain.token_interfaces import PasswordResetRepositoryInterface


class ForgotPasswordUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        reset_repo: PasswordResetRepositoryInterface,
    ):
        self.user_repo = user_repo
        self.reset_repo = reset_repo

    async def execute(self, email: str) -> dict:
        from app.core.email import resolve_smtp_for_user, send_password_reset

        user = await self.user_repo.get_by_email(email.lower().strip())

        if user:
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            reset_token = PasswordResetTokenModel(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=datetime.now(UTC) + timedelta(hours=1),
            )
            await self.reset_repo.save_token(reset_token)
            from app.database import async_session_factory

            async with async_session_factory() as db:
                smtp = await resolve_smtp_for_user(db, str(user.id))
            send_password_reset(
                to_email=user.email,
                reset_token=token,
                base_url="https://plant-intelligence-platform.vercel.app",
                smtp=smtp,
            )

        return {"message": "If the email exists, a password reset link has been sent"}


class ResetPasswordUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        reset_repo: PasswordResetRepositoryInterface,
    ):
        self.user_repo = user_repo
        self.reset_repo = reset_repo

    async def execute(self, token: str, new_password: str) -> dict:
        if not new_password or len(new_password) < 8:
            raise AppException(
                status_code=400,
                detail="Password must be at least 8 characters",
                error_code="WEAK_PASSWORD",
            )

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        reset_token = await self.reset_repo.get_valid_token(token_hash)

        if not reset_token or reset_token.used:
            raise AppException(
                status_code=400,
                detail="Invalid or expired reset token",
                error_code="INVALID_TOKEN",
            )

        if reset_token.expires_at < datetime.now(UTC):
            raise AppException(
                status_code=400,
                detail="Reset token has expired",
                error_code="TOKEN_EXPIRED",
            )

        user = await self.user_repo.get_by_id(str(reset_token.user_id))
        if not user:
            raise AppException(
                status_code=404, detail="User not found", error_code="NOT_FOUND"
            )

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.now(UTC)
        await self.user_repo.update(user)

        await self.reset_repo.mark_used(str(reset_token.id))

        return {"message": "Password has been reset successfully"}


class ChangePasswordUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    async def execute(
        self, user_id: str, current_password: str, new_password: str
    ) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                status_code=404, detail="User not found", error_code="NOT_FOUND"
            )

        if not verify_password(current_password, user.hashed_password):
            raise AppException(
                status_code=400,
                detail="Current password is incorrect",
                error_code="INVALID_PASSWORD",
            )

        if not new_password or len(new_password) < 8:
            raise AppException(
                status_code=400,
                detail="Password must be at least 8 characters",
                error_code="WEAK_PASSWORD",
            )

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.now(UTC)
        await self.user_repo.update(user)

        return {"message": "Password changed successfully"}
