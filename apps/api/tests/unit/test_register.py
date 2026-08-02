
import pytest

from app.core.exceptions import ConflictException, ValidationException
from app.modules.auth.domain.models import UserModel
from app.modules.auth.domain.use_cases import RegisterUserUseCase


class FakeUserRepo:
    def __init__(self):
        self.users = {}

    async def get_by_id(self, user_id):
        return self.users.get(user_id)

    async def get_by_email(self, email):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def create(self, user):
        self.users[str(user.id)] = user
        return user

    async def update(self, user):
        self.users[str(user.id)] = user
        return user


class TestRegisterUserUseCase:
    @pytest.mark.asyncio
    async def test_register_success(self):
        repo = FakeUserRepo()
        use_case = RegisterUserUseCase(repo)

        user = await use_case.execute(
            email="test@example.com",
            password="TestPassword123!",
            full_name="Test User",
            institution="Test University",
        )

        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.institution == "Test University"
        assert user.role == "researcher"
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        repo = FakeUserRepo()
        existing = UserModel(
            email="test@example.com",
            hashed_password="hashed",
            full_name="Existing User",
        )
        repo.users["1"] = existing

        use_case = RegisterUserUseCase(repo)

        with pytest.raises(ConflictException):
            await use_case.execute(
                email="test@example.com",
                password="TestPassword123!",
                full_name="New User",
            )

    @pytest.mark.asyncio
    async def test_register_invalid_email(self):
        repo = FakeUserRepo()
        use_case = RegisterUserUseCase(repo)

        with pytest.raises(ValidationException):
            await use_case.execute(
                email="not-an-email",
                password="TestPassword123!",
                full_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_register_weak_password_no_uppercase(self):
        repo = FakeUserRepo()
        use_case = RegisterUserUseCase(repo)

        with pytest.raises(ValidationException):
            await use_case.execute(
                email="test@example.com",
                password="testpassword1!",
                full_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_register_weak_password_no_digit(self):
        repo = FakeUserRepo()
        use_case = RegisterUserUseCase(repo)

        with pytest.raises(ValidationException):
            await use_case.execute(
                email="test@example.com",
                password="TestPassword!",
                full_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_register_weak_password_too_short(self):
        repo = FakeUserRepo()
        use_case = RegisterUserUseCase(repo)

        with pytest.raises(ValidationException):
            await use_case.execute(
                email="test@example.com",
                password="Ab1!",
                full_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_register_empty_name(self):
        repo = FakeUserRepo()
        use_case = RegisterUserUseCase(repo)

        with pytest.raises(ValidationException):
            await use_case.execute(
                email="test@example.com",
                password="TestPassword123!",
                full_name="",
            )

    @pytest.mark.asyncio
    async def test_register_email_normalized(self):
        repo = FakeUserRepo()
        use_case = RegisterUserUseCase(repo)

        user = await use_case.execute(
            email="  TEST@Example.COM  ",
            password="TestPassword123!",
            full_name="Test User",
        )

        assert user.email == "test@example.com"
