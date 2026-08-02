# Authentication Module - Phase 3

## Overview

The authentication module provides secure JWT-based authentication with role-based access control (RBAC) for the Plant Intelligence Platform.

## Features

- **JWT Authentication**: Short-lived access tokens (30 min) with refresh token rotation (7 days)
- **Registration**: Email + password with strong password validation
- **Login**: Email/password login with audit logging
- **Role-Based Access Control**: admin, principal_investigator, researcher, technician, readonly
- **Password Management**: Forgot password, reset password, change password
- **User Profiles**: View and update profile information
- **Session Management**: Refresh token storage, revocation, and cleanup

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password with token |

### Protected Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout (revoke refresh token) |
| GET | `/api/v1/auth/me` | Get current user profile |
| PUT | `/api/v1/auth/me` | Update profile |
| POST | `/api/v1/auth/change-password` | Change password |

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

## Roles

| Role | Description |
|------|-------------|
| `admin` | Full system access |
| `principal_investigator` | Project management, user oversight |
| `researcher` | Standard research operations |
| `technician` | Lab operations, data entry |
| `readonly` | View-only access |

## Architecture

```
Domain Layer (use_cases.py)
├── RegisterUserUseCase
├── LoginUseCase
├── LogoutUseCase
├── RefreshTokenUseCase
├── ForgotPasswordUseCase
├── ResetPasswordUseCase
├── ChangePasswordUseCase
├── GetUserProfileUseCase
└── UpdateUserProfileUseCase

Infrastructure Layer
├── UserRepository (SQLAlchemy)
├── TokenRepository (SQLAlchemy)
├── PasswordResetRepository (SQLAlchemy)
└── AuditLogRepository (SQLAlchemy)

API Layer
├── router.py (FastAPI endpoints)
└── schemas.py (Pydantic models)
```

## Testing

```bash
# Unit tests
pytest tests/unit/test_security.py -v
pytest tests/unit/test_register.py -v
pytest tests/unit/test_login.py -v
pytest tests/unit/test_validation.py -v

# Integration tests
pytest tests/integration/test_auth.py -v

# All auth tests
pytest tests/ -k "auth or security or login or register or validation" -v
```
