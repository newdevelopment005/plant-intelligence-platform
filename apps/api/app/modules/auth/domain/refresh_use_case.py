import hashlib
from datetime import UTC, datetime, timedelta

from app.config import settings
from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.modules.auth.domain.interfaces import UserRepositoryInterface
from app.modules.auth.domain.token_interfaces import TokenRepositoryInterface


class RefreshTokenUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        token_repo: TokenRepositoryInterface,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def execute(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AppException(
                status_code=401, detail="Invalid refresh token", error_code="INVALID_TOKEN"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise AppException(
                status_code=401, detail="Invalid token payload", error_code="INVALID_TOKEN"
            )

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stored_token = await self.token_repo.get_refresh_token(token_hash)

        if not stored_token or stored_token.revoked:
            raise AppException(
                status_code=401,
                detail="Refresh token has been revoked",
                error_code="TOKEN_REVOKED",
            )

        if stored_token.expires_at < datetime.now(UTC):
            raise AppException(
                status_code=401, detail="Refresh token has expired", error_code="TOKEN_EXPIRED"
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AppException(
                status_code=401, detail="User not found or inactive", error_code="USER_INACTIVE"
            )

        await self.token_repo.revoke_refresh_token(token_hash)

        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        from app.modules.auth.domain.token_model import RefreshTokenModel

        new_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
        new_stored_token = RefreshTokenModel(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.token_repo.save_refresh_token(new_stored_token)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
