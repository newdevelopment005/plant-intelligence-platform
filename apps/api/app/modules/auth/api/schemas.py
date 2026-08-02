from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    institution: str | None = Field(None, max_length=255)
    department: str | None = Field(None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    institution: str | None = None
    department: str | None = None
    is_active: bool
    is_verified: bool
    orcid_id: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    created_at: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=255)
    institution: str | None = Field(None, max_length=255)
    department: str | None = Field(None, max_length=255)
    bio: str | None = Field(None, max_length=2000)
    orcid_id: str | None = Field(None, max_length=50)


class MessageResponse(BaseModel):
    message: str
