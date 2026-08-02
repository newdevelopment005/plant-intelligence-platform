import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.project.api.schemas import (
    AddMemberRequest,
    CreateProjectRequest,
    UpdateMemberRoleRequest,
    UpdateProjectRequest,
)
from app.modules.project.domain.use_cases import (
    AddMemberUseCase,
    CreateProjectUseCase,
    DeleteProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    RemoveMemberUseCase,
    UpdateMemberRoleUseCase,
    UpdateProjectUseCase,
)
from app.modules.project.infrastructure.member_repository import ProjectMemberRepository
from app.modules.project.infrastructure.repositories import ProjectRepository

logger = structlog.get_logger()
router = APIRouter()


def _get_project_repo(db: AsyncSession) -> ProjectRepository:
    return ProjectRepository(db)


def _get_member_repo(db: AsyncSession) -> ProjectMemberRepository:
    return ProjectMemberRepository(db)


@router.get("/", response_model=None)
async def list_projects(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, pattern="^(active|archived|deleted)$"),
    search: str | None = Query(None, max_length=255),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)
    use_case = ListProjectsUseCase(project_repo, member_repo)

    return await use_case.execute(
        user_id=current_user["id"],
        skip=skip,
        limit=limit,
        status=status,
        search=search,
    )


@router.post("/", status_code=201)
async def create_project(
    body: CreateProjectRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)
    use_case = CreateProjectUseCase(project_repo, member_repo)

    project = await use_case.execute(
        name=body.name,
        owner_id=current_user["id"],
        description=body.description,
        start_date=body.start_date,
        end_date=body.end_date,
        tags=body.tags,
    )

    logger.info(
        "project_created",
        project_id=str(project.id),
        user_id=current_user["id"],
    )

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "owner_id": str(project.owner_id),
        "created_at": project.created_at.isoformat(),
    }


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)
    use_case = GetProjectUseCase(project_repo, member_repo)

    return await use_case.execute(
        project_id=project_id,
        user_id=current_user["id"],
    )


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    body: UpdateProjectRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)
    use_case = UpdateProjectUseCase(project_repo, member_repo)

    project = await use_case.execute(
        project_id=project_id,
        user_id=current_user["id"],
        name=body.name,
        description=body.description,
        status=body.status,
        start_date=body.start_date,
        end_date=body.end_date,
        tags=body.tags,
    )

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "owner_id": str(project.owner_id),
        "start_date": project.start_date.isoformat() if project.start_date else None,
        "end_date": project.end_date.isoformat() if project.end_date else None,
        "tags": project.tags,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)
    use_case = DeleteProjectUseCase(project_repo, member_repo)

    return await use_case.execute(
        project_id=project_id,
        user_id=current_user["id"],
    )


@router.get("/{project_id}/members")
async def list_members(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)

    from app.core.exceptions import NotFoundException, ValidationException

    project = await project_repo.get_by_id(project_id)
    if not project:
        raise NotFoundException("Project", project_id)

    membership = await member_repo.get_by_project_and_user(
        project_id, current_user["id"]
    )
    if not membership:
        raise ValidationException("You are not a member of this project")

    members = await member_repo.list_members(project_id)
    return {
        "items": [
            {
                "id": str(m.id),
                "user_id": str(m.user_id),
                "role": m.role,
                "joined_at": m.joined_at.isoformat(),
            }
            for m in members
        ],
        "total": len(members),
    }


@router.post("/{project_id}/members", status_code=201)
async def add_member(
    project_id: str,
    body: AddMemberRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)
    use_case = AddMemberUseCase(project_repo, member_repo)

    member = await use_case.execute(
        project_id=project_id,
        user_id=current_user["id"],
        new_user_id=body.user_id,
        role=body.role,
    )

    return {
        "id": str(member.id),
        "user_id": str(member.user_id),
        "role": member.role,
        "joined_at": member.joined_at.isoformat(),
    }


@router.put("/{project_id}/members/{user_id}")
async def update_member_role(
    project_id: str,
    user_id: str,
    body: UpdateMemberRoleRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)
    use_case = UpdateMemberRoleUseCase(project_repo, member_repo)

    member = await use_case.execute(
        project_id=project_id,
        user_id=current_user["id"],
        target_user_id=user_id,
        new_role=body.role,
    )

    return {
        "id": str(member.id),
        "user_id": str(member.user_id),
        "role": member.role,
        "joined_at": member.joined_at.isoformat(),
    }


@router.delete("/{project_id}/members/{user_id}")
async def remove_member(
    project_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    project_repo = _get_project_repo(db)
    member_repo = _get_member_repo(db)
    use_case = RemoveMemberUseCase(project_repo, member_repo)

    return await use_case.execute(
        project_id=project_id,
        user_id=current_user["id"],
        target_user_id=user_id,
    )
