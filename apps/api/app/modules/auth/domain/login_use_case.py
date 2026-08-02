import hashlib
from datetime import UTC, datetime

from app.config import settings
from app.core.exceptions import AppException
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.modules.auth.domain.interfaces import UserRepositoryInterface
from app.modules.auth.domain.token_interfaces import TokenRepositoryInterface
from app.modules.auth.domain.token_model import RefreshTokenModel


class LoginUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        token_repo: TokenRepositoryInterface,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def execute(
        self, email: str, password: str, ip_address: str | None = None
    ) -> dict:
        user = await self.user_repo.get_by_email(email.lower().strip())
        if not user:
            raise AppException(
                status_code=401, detail="Invalid email or password", error_code="INVALID_CREDENTIALS"
            )

        if not user.is_active:
            raise AppException(
                status_code=403, detail="Account is deactivated", error_code="ACCOUNT_DEACTIVATED"
            )

        if not verify_password(password, user.hashed_password):
            raise AppException(
                status_code=401, detail="Invalid email or password", error_code="INVALID_CREDENTIALS"
            )

        user.last_login = datetime.now(UTC)
        await self.user_repo.update(user)

        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        refresh_token_model = RefreshTokenModel(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(UTC)
            + __import__("datetime").timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.token_repo.save_refresh_token(refresh_token_model)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "institution": user.institution,
            },
        }
