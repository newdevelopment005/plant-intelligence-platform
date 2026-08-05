import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.team.api.schemas import (
    AddTeamMemberRequest,
    CreateTeamRequest,
)
from app.modules.team.domain.use_cases import (
    AddTeamMemberUseCase,
    CreateTeamUseCase,
    DeleteTeamUseCase,
    GetTeamUseCase,
    ListTeamsUseCase,
    RemoveTeamMemberUseCase,
)
from app.modules.team.infrastructure.member_repository import TeamMemberRepository
from app.modules.team.infrastructure.repositories import TeamRepository

logger = structlog.get_logger()
router = APIRouter(redirect_slashes=False)


def _get_team_repo(db: AsyncSession) -> TeamRepository:
    return TeamRepository(db)


def _get_member_repo(db: AsyncSession) -> TeamMemberRepository:
    return TeamMemberRepository(db)


def _team_to_dict(team) -> dict:
    return {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "owner_id": str(team.owner_id),
        "created_at": team.created_at.isoformat(),
        "updated_at": team.updated_at.isoformat(),
    }


def _member_to_dict(member) -> dict:
    return {
        "id": str(member.id),
        "user_id": str(member.user_id),
        "role": member.role,
        "joined_at": member.joined_at.isoformat(),
    }


@router.get("/", response_model=None)
async def list_teams(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    team_repo = _get_team_repo(db)
    member_repo = _get_member_repo(db)
    use_case = ListTeamsUseCase(team_repo, member_repo)

    return await use_case.execute(
        user_id=current_user["id"],
        skip=skip,
        limit=limit,
    )


@router.post("/", status_code=201)
async def create_team(
    body: CreateTeamRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    team_repo = _get_team_repo(db)
    member_repo = _get_member_repo(db)
    use_case = CreateTeamUseCase(team_repo, member_repo)

    team = await use_case.execute(
        name=body.name,
        owner_id=current_user["id"],
        description=body.description,
    )

    logger.info(
        "team_created",
        team_id=str(team.id),
        user_id=current_user["id"],
    )

    return _team_to_dict(team)


@router.get("/{team_id}")
async def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    team_repo = _get_team_repo(db)
    member_repo = _get_member_repo(db)
    use_case = GetTeamUseCase(team_repo, member_repo)

    return await use_case.execute(
        team_id=team_id,
        user_id=current_user["id"],
    )


@router.post("/{team_id}/members", status_code=201)
async def add_member(
    team_id: str,
    body: AddTeamMemberRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    team_repo = _get_team_repo(db)
    member_repo = _get_member_repo(db)
    use_case = AddTeamMemberUseCase(team_repo, member_repo)

    member = await use_case.execute(
        team_id=team_id,
        user_id=current_user["id"],
        target_user_id=body.user_id,
        role=body.role,
    )

    return _member_to_dict(member)


@router.delete("/{team_id}/members/{target_user_id}")
async def remove_member(
    team_id: str,
    target_user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    team_repo = _get_team_repo(db)
    member_repo = _get_member_repo(db)
    use_case = RemoveTeamMemberUseCase(team_repo, member_repo)

    return await use_case.execute(
        team_id=team_id,
        user_id=current_user["id"],
        target_user_id=target_user_id,
    )


@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    team_repo = _get_team_repo(db)
    member_repo = _get_member_repo(db)
    use_case = DeleteTeamUseCase(team_repo, member_repo)

    return await use_case.execute(
        team_id=team_id,
        user_id=current_user["id"],
    )
