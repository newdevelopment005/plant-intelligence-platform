import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import UTC, datetime

from app.core.exceptions import AppException, ConflictException, ValidationException
from app.modules.auth.domain.use_cases import RegisterUserUseCase
from app.modules.auth.domain.login_use_case import LoginUseCase


class TestRegisterUserUseCase:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.use_case = RegisterUserUseCase(self.user_repo)

    @pytest.mark.asyncio
    async def test_register_success(self):
        mock_user = MagicMock(
            id="user-123",
            email="test@example.com",
            full_name="Test User",
        )
        self.user_repo.get_by_email = AsyncMock(return_value=None)
        self.user_repo.create = AsyncMock(return_value=mock_user)
        result = await self.use_case.execute(
            email="test@example.com",
            password="StrongPass1!",
            full_name="Test User",
        )
        assert result.email == "test@example.com"
        self.user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        existing_user = MagicMock(email="test@example.com")
        self.user_repo.get_by_email = AsyncMock(return_value=existing_user)
        with pytest.raises(ConflictException):
            await self.use_case.execute(
                email="test@example.com",
                password="StrongPass1!",
                full_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_register_invalid_email(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                email="not-an-email",
                password="StrongPass1!",
                full_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_register_weak_password(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                email="test@example.com",
                password="weak",
                full_name="Test User",
            )


class TestLoginUseCase:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.token_repo = MagicMock()
        self.use_case = LoginUseCase(self.user_repo, self.token_repo)

    @pytest.mark.asyncio
    async def test_login_success(self):
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash("StrongPass1!")

        mock_user = MagicMock(
            id="user-123",
            email="test@example.com",
            full_name="Test User",
            hashed_password=hashed,
            role="researcher",
            institution="MIT",
            is_active=True,
        )
        self.user_repo.get_by_email = AsyncMock(return_value=mock_user)
        self.user_repo.update = AsyncMock(return_value=mock_user)
        self.token_repo.save_refresh_token = AsyncMock()

        result = await self.use_case.execute(
            email="test@example.com",
            password="StrongPass1!",
        )
        assert result["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash("CorrectPassword1!")

        mock_user = MagicMock(
            id="user-123",
            email="test@example.com",
            hashed_password=hashed,
            is_active=True,
        )
        self.user_repo.get_by_email = AsyncMock(return_value=mock_user)
        with pytest.raises(AppException):
            await self.use_case.execute(
                email="test@example.com",
                password="WrongPassword1!",
            )

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        self.user_repo.get_by_email = AsyncMock(return_value=None)
        with pytest.raises(AppException):
            await self.use_case.execute(
                email="nonexistent@example.com",
                password="AnyPassword1!",
            )

    @pytest.mark.asyncio
    async def test_login_inactive_user(self):
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash("StrongPass1!")

        mock_user = MagicMock(
            id="user-123",
            email="test@example.com",
            hashed_password=hashed,
            is_active=False,
        )
        self.user_repo.get_by_email = AsyncMock(return_value=mock_user)
        with pytest.raises(AppException):
            await self.use_case.execute(
                email="test@example.com",
                password="StrongPass1!",
            )
