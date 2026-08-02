
import pytest

from app.core.exceptions import AppException
from app.core.security import get_password_hash
from app.modules.auth.domain.login_use_case import LoginUseCase
from app.modules.auth.domain.models import UserModel


class FakeUserRepo:
    def __init__(self, user=None):
        self.user = user

    async def get_by_id(self, user_id):
        return self.user

    async def get_by_email(self, email):
        if self.user and self.user.email == email:
            return self.user
        return None

    async def update(self, user):
        return user


class FakeTokenRepo:
    def __init__(self):
        self.tokens = []

    async def save_refresh_token(self, token):
        self.tokens.append(token)
        return token


class TestLoginUseCase:
    def _make_user(self, email="test@example.com", password="TestPassword123!", active=True):
        user = UserModel(
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Test User",
            role="researcher",
            is_active=active,
        )
        user.id = "test-user-id"
        return user

    @pytest.mark.asyncio
    async def test_login_success(self):
        user = self._make_user()
        user_repo = FakeUserRepo(user)
        token_repo = FakeTokenRepo()

        use_case = LoginUseCase(user_repo, token_repo)
        result = await use_case.execute(email="test@example.com", password="TestPassword123!")

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["user"]["email"] == "test@example.com"
        assert len(token_repo.tokens) == 1

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        user = self._make_user()
        user_repo = FakeUserRepo(user)
        token_repo = FakeTokenRepo()

        use_case = LoginUseCase(user_repo, token_repo)

        with pytest.raises(AppException) as exc_info:
            await use_case.execute(email="test@example.com", password="WrongPassword")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        user_repo = FakeUserRepo(None)
        token_repo = FakeTokenRepo()

        use_case = LoginUseCase(user_repo, token_repo)

        with pytest.raises(AppException) as exc_info:
            await use_case.execute(email="nonexistent@example.com", password="TestPassword123!")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self):
        user = self._make_user(active=False)
        user_repo = FakeUserRepo(user)
        token_repo = FakeTokenRepo()

        use_case = LoginUseCase(user_repo, token_repo)

        with pytest.raises(AppException) as exc_info:
            await use_case.execute(email="test@example.com", password="TestPassword123!")

        assert exc_info.value.status_code == 403
