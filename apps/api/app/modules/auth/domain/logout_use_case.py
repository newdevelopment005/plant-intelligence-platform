import hashlib

from app.modules.auth.domain.interfaces import UserRepositoryInterface
from app.modules.auth.domain.token_interfaces import TokenRepositoryInterface


class LogoutUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        token_repo: TokenRepositoryInterface,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def execute(self, refresh_token: str | None = None) -> dict:
        if refresh_token:
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            await self.token_repo.revoke_refresh_token(token_hash)

        return {"message": "Successfully logged out"}
