import re
from datetime import UTC, datetime

from app.core.exceptions import ConflictException, ValidationException
from app.core.security import get_password_hash
from app.modules.auth.domain.interfaces import UserRepositoryInterface
from app.modules.auth.domain.models import UserModel


class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    async def execute(
        self,
        email: str,
        password: str,
        full_name: str,
        institution: str | None = None,
        department: str | None = None,
    ) -> UserModel:
        self._validate_email(email)
        self._validate_password(password)
        self._validate_name(full_name)

        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictException("A user with this email already exists")

        user = UserModel(
            email=email.lower().strip(),
            hashed_password=get_password_hash(password),
            full_name=full_name.strip(),
            institution=institution.strip() if institution else None,
            department=department.strip() if department else None,
            role="researcher",
            is_active=True,
            is_verified=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.user_repo.create(user)

    def _validate_email(self, email: str) -> None:
        if not email or not email.strip():
            raise ValidationException("Email is required")
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email.strip()):
            raise ValidationException("Invalid email format")

    def _validate_password(self, password: str) -> None:
        if not password:
            raise ValidationException("Password is required")
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValidationException("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValidationException("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValidationException("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationException("Password must contain at least one special character")

    def _validate_name(self, name: str) -> None:
        if not name or not name.strip():
            raise ValidationException("Full name is required")
        if len(name.strip()) < 2:
            raise ValidationException("Full name must be at least 2 characters long")
