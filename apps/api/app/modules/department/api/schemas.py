from pydantic import BaseModel, Field


class CreateDepartmentRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=5000)
    head_user_id: str | None = None


class UpdateDepartmentRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    code: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=5000)
    head_user_id: str | None = None
    is_active: bool | None = None


class AddDepartmentMemberRequest(BaseModel):
    user_id: str
    role: str = Field(default="member", pattern="^(head|member)$")


class UpdateDepartmentMemberRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(head|member)$")


class DepartmentResponse(BaseModel):
    id: str
    name: str
    code: str | None
    description: str | None
    head_user_id: str | None
    is_active: bool
    member_count: int
    created_at: str
    updated_at: str


class PaginatedDepartmentsResponse(BaseModel):
    items: list[DepartmentResponse]
    total: int
    skip: int
    limit: int


class UserBrief(BaseModel):
    id: str
    full_name: str | None = None
    email: str | None = None


class DepartmentMemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    joined_at: str
    user: UserBrief | None = None