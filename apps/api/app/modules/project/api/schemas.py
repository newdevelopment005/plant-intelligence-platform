from datetime import date

from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: str | None = Field(None, max_length=5000)
    start_date: date | None = None
    end_date: date | None = None
    tags: list[str] | None = Field(None, max_length=20)


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = Field(None, max_length=5000)
    status: str | None = Field(None, pattern="^(active|archived|deleted)$")
    start_date: date | None = None
    end_date: date | None = None
    tags: list[str] | None = Field(None, max_length=20)


class AddMemberRequest(BaseModel):
    user_id: str
    role: str = Field(default="member", pattern="^(admin|member|readonly)$")


class UpdateMemberRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(admin|member|readonly)$")


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    status: str
    owner_id: str
    start_date: str | None
    end_date: str | None
    tags: list[str] | None
    member_count: int
    created_at: str
    updated_at: str


class ProjectDetailResponse(ProjectResponse):
    metadata: dict | None = None
    members: list[dict] = []


class MemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    joined_at: str


class PaginatedProjectsResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    skip: int
    limit: int


class ProjectStatsResponse(BaseModel):
    total_projects: int
    active_projects: int
    archived_projects: int
    total_members: int
