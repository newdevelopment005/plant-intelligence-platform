
import structlog
from datetime import UTC, datetime
from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.auth.api.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    UpdateProfileRequest,
    VerifyEmailRequest,
)
from app.modules.auth.domain.login_use_case import LoginUseCase
from app.modules.auth.domain.logout_use_case import LogoutUseCase
from app.modules.auth.domain.password_use_cases import (
    ChangePasswordUseCase,
    ForgotPasswordUseCase,
    ResetPasswordUseCase,
)
from app.modules.auth.domain.profile_use_cases import (
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
)
from app.modules.auth.domain.refresh_use_case import RefreshTokenUseCase
from app.modules.auth.domain.use_cases import RegisterUserUseCase
from app.modules.auth.infrastructure.audit_repository import AuditLogRepository
from app.modules.auth.infrastructure.password_reset_repository import PasswordResetRepository
from app.modules.auth.infrastructure.repositories import UserRepository
from app.modules.auth.infrastructure.token_repository import TokenRepository
from app.core.security import create_verification_token

logger = structlog.get_logger()
router = APIRouter()


def _get_user_repo(db: AsyncSession) -> UserRepository:
    return UserRepository(db)


def _get_token_repo(db: AsyncSession) -> TokenRepository:
    return TokenRepository(db)


def _get_reset_repo(db: AsyncSession) -> PasswordResetRepository:
    return PasswordResetRepository(db)


def _get_audit_repo(db: AsyncSession) -> AuditLogRepository:
    return AuditLogRepository(db)


@router.post("/register", status_code=201)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    from app.core.email import send_verification_email

    user_repo = _get_user_repo(db)
    use_case = RegisterUserUseCase(user_repo)

    user = await use_case.execute(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        institution=request.institution,
        department=request.department,
    )

    logger.info("user_registered", user_id=str(user.id), email=user.email)

    verify_token = create_verification_token(str(user.id))
    send_verification_email(
        to_email=user.email,
        user_name=user.full_name,
        verify_token=verify_token,
        base_url="https://plant-intelligence-platform.vercel.app",
    )

    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        },
    }


@router.post("/resend-verification")
async def resend_verification(
    body: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    from app.core.email import send_verification_email

    user_repo = _get_user_repo(db)
    user = await user_repo.get_by_email(body.email)
    if user and not user.is_verified:
        verify_token = create_verification_token(str(user.id))
        send_verification_email(
            to_email=user.email,
            user_name=user.full_name,
            verify_token=verify_token,
            base_url="https://plant-intelligence-platform.vercel.app",
        )
    return {"message": "If the email is registered, a verification link has been sent"}


@router.post("/verify-email")
async def verify_email(
    body: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    from app.core.security import decode_verification_token

    user_repo = _get_user_repo(db)

    user_id = decode_verification_token(body.token)
    user = await user_repo.get_by_id(user_id) if user_id else None
    if not user:
        from app.core.exceptions import ValidationException
        raise ValidationException("Invalid or expired verification link")

    if not user.is_verified:
        user.is_verified = True
        user.updated_at = datetime.now(UTC)
        await user_repo.update(user)
        logger.info("email_verified", user_id=str(user.id))

    return {"message": "Email verified successfully"}


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user_repo = _get_user_repo(db)
    token_repo = _get_token_repo(db)
    audit_repo = _get_audit_repo(db)

    use_case = LoginUseCase(user_repo, token_repo)
    ip_address = request.client.host if request.client else None

    result = await use_case.execute(
        email=body.email, password=body.password, ip_address=ip_address
    )

    await audit_repo.log(
        user_id=result["user"]["id"],
        action="login",
        resource_type="user",
        resource_id=result["user"]["id"],
        ip_address=ip_address,
    )

    logger.info("user_logged_in", user_id=result["user"]["id"])

    return result


@router.post("/refresh")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    user_repo = _get_user_repo(db)
    token_repo = _get_token_repo(db)

    use_case = RefreshTokenUseCase(user_repo, token_repo)
    result = await use_case.execute(refresh_token=body.refresh_token)

    return result


@router.post("/logout")
async def logout(
    body: RefreshRequest | None = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = _get_user_repo(db)
    token_repo = _get_token_repo(db)

    use_case = LogoutUseCase(user_repo, token_repo)
    refresh_token = body.refresh_token if body else None
    result = await use_case.execute(refresh_token=refresh_token)

    logger.info("user_logged_out", user_id=current_user["id"])

    return result


@router.get("/me")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = _get_user_repo(db)
    use_case = GetUserProfileUseCase(user_repo)

    user = await use_case.execute(current_user["id"])

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "institution": user.institution,
        "department": user.department,
        "department_id": str(user.department_id) if user.department_id else None,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "orcid_id": user.orcid_id,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat(),
    }


@router.put("/me")
async def update_current_user_profile(
    body: UpdateProfileRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = _get_user_repo(db)
    use_case = UpdateUserProfileUseCase(user_repo)

    user = await use_case.execute(
        user_id=current_user["id"],
        full_name=body.full_name,
        institution=body.institution,
        department=body.department,
        bio=body.bio,
        orcid_id=body.orcid_id,
    )

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "institution": user.institution,
        "department": user.department,
        "department_id": str(user.department_id) if user.department_id else None,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "orcid_id": user.orcid_id,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat(),
    }


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user_repo = _get_user_repo(db)
    reset_repo = _get_reset_repo(db)

    use_case = ForgotPasswordUseCase(user_repo, reset_repo)
    result = await use_case.execute(email=body.email)

    return result


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user_repo = _get_user_repo(db)
    reset_repo = _get_reset_repo(db)

    use_case = ResetPasswordUseCase(user_repo, reset_repo)
    result = await use_case.execute(token=body.token, new_password=body.new_password)

    return result


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = _get_user_repo(db)
    use_case = ChangePasswordUseCase(user_repo)

    result = await use_case.execute(
        user_id=current_user["id"],
        current_password=body.current_password,
        new_password=body.new_password,
    )

    return result


@router.get("/users/search")
async def search_users(
    q: str = Query(..., min_length=1, description="Search query (email or name)"),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = _get_user_repo(db)
    users = await user_repo.search_by_email_or_name(q, limit=limit)
    return {
        "items": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
            }
            for u in users
        ]
    }
