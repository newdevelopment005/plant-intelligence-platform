from pydantic import BaseModel, Field


class CreateTeamRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: str | None = Field(None, max_length=5000)


class AddTeamMemberRequest(BaseModel):
    user_id: str
    role: str = Field(default="member", pattern="^(admin|member)$")


class TeamResponse(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str
    member_count: int
    created_at: str
    updated_at: str


class TeamDetailResponse(TeamResponse):
    members: list[dict] = []


class TeamMemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    joined_at: str
