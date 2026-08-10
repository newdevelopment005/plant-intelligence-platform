import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.team.api.schemas import (
    AddTeamMemberRequest,
    CreateTeamRequest,
    InviteTeamMemberByEmailRequest,
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


def _member_to_dict(member, user=None) -> dict:
    result = {
        "id": str(member.id),
        "user_id": str(member.user_id),
        "role": member.role,
        "joined_at": member.joined_at.isoformat(),
    }
    if user:
        import uuid as _uuid

        user_id = (
            user.get("id") or user.get("user_id")
            if isinstance(user, dict)
            else str(user.id) if getattr(user, "id", None) else str(member.user_id)
        )
        if isinstance(user_id, _uuid.UUID):
            user_id = str(user_id)
        if isinstance(user, dict):
            full_name = user.get("full_name")
            email = user.get("email")
        else:
            full_name = getattr(user, "full_name", None)
            email = getattr(user, "email", None)
        result["user"] = {
            "id": user_id,
            "full_name": full_name,
            "email": email,
        }
    return result


async def _user_summary(db: AsyncSession, user_id: str) -> dict | None:
    from app.modules.auth.infrastructure.repositories import UserRepository

    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        return None
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
    }


async def _members_with_user_dicts(db: AsyncSession, members) -> list[dict]:
    from app.modules.auth.infrastructure.repositories import UserRepository

    user_ids = [str(m.user_id) for m in members]
    users = await UserRepository(db).get_by_ids(user_ids)
    by_id = {str(u.id): u for u in users}
    return [_member_to_dict(m, by_id.get(str(m.user_id))) for m in members]


@router.get("", response_model=None)
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


@router.post("", status_code=201)
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

    result = await use_case.execute(
        team_id=team_id,
        user_id=current_user["id"],
    )
    members = await member_repo.list_members(team_id)
    result["members"] = await _members_with_user_dicts(db, members)
    if result.get("owner_id"):
        owner = await _user_summary(db, result["owner_id"])
        if owner:
            result["owner"] = owner
    return result


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

    return _member_to_dict(member, await _user_summary(db, str(member.user_id)))


@router.post("/{team_id}/invite-by-email", status_code=201)
async def invite_member_by_email(
    team_id: str,
    body: InviteTeamMemberByEmailRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.email import send_team_invite_email
    from app.modules.auth.infrastructure.repositories import UserRepository

    email = body.email.lower().strip()
    user = await UserRepository(db).get_by_email(email)

    team_repo = _get_team_repo(db)
    member_repo = _get_member_repo(db)
    team = await team_repo.get_by_id(team_id)
    if not team:
        from app.core.exceptions import NotFoundException

        raise NotFoundException("Team", team_id)

    added = False
    target_user_id = None
    if user:
        user_id_str = str(user.id)
        existing = await member_repo.get_by_team_and_user(team_id, user_id_str)
        if existing:
            target_user_id = user_id_str
        else:
            member = await AddTeamMemberUseCase(team_repo, member_repo).execute(
                team_id=team_id,
                user_id=current_user["id"],
                target_user_id=user_id_str,
                role=body.role,
            )
            target_user_id = str(member.user_id)
            added = True

    send_team_invite_email(
        to_email=email,
        inviter_name=current_user.get("full_name") or current_user.get("email") or "A colleague",
        team_name=team.name,
        role=body.role,
        base_url="https://plant-intelligence-platform.vercel.app",
    )

    return {
        "message": f"Invitation sent to {email}",
        "email": email,
        "matched_user": added,
        "user_id": target_user_id,
        "role": body.role,
    }


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
