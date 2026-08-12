import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_active_user,
    require_admin,
    require_admin_or_department_head,
)
from app.database import get_db
from app.modules.department.api.schemas import (
    AddDepartmentMemberRequest,
    CreateDepartmentRequest,
    DepartmentMemberResponse,
    DepartmentResponse,
    PaginatedDepartmentsResponse,
    UpdateDepartmentMemberRoleRequest,
    UpdateDepartmentRequest,
)
from app.modules.department.domain.use_cases import (
    AddDepartmentMemberUseCase,
    CreateDepartmentUseCase,
    DeleteDepartmentUseCase,
    ListDepartmentsUseCase,
    RemoveDepartmentMemberUseCase,
    UpdateDepartmentMemberRoleUseCase,
    UpdateDepartmentUseCase,
)
from app.modules.department.infrastructure.repositories import (
    DepartmentMemberRepository,
    DepartmentRepository,
)

logger = structlog.get_logger()
router = APIRouter(redirect_slashes=False)


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


async def _members_with_users(db: AsyncSession, members) -> list[dict]:
    from app.modules.auth.infrastructure.repositories import UserRepository

    user_ids = [str(m.user_id) for m in members]
    users = await UserRepository(db).get_by_ids(user_ids)
    by_id = {str(u.id): u for u in users}
    return [
        _member_to_dict(m, by_id.get(str(m.user_id)))
        for m in members
    ]


def _get_department_repo(db: AsyncSession) -> DepartmentRepository:
    return DepartmentRepository(db)


def _get_member_repo(db: AsyncSession) -> DepartmentMemberRepository:
    return DepartmentMemberRepository(db)


def _department_to_dict(dep) -> dict:
    return {
        "id": str(dep.id),
        "name": dep.name,
        "code": dep.code,
        "description": dep.description,
        "head_user_id": str(dep.head_user_id) if dep.head_user_id else None,
        "is_active": bool(dep.is_active),
        "created_at": dep.created_at.isoformat(),
        "updated_at": dep.updated_at.isoformat(),
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


def _head_user_dict(dep) -> dict | None:
    if not dep or not dep.head_user_id:
        return None
    return {
        "id": str(dep.head_user_id),
        "full_name": None,
        "email": None,
    }


@router.get("", response_model=PaginatedDepartmentsResponse)
async def list_departments(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str | None = Query(None, max_length=255),
):
    repo = _get_department_repo(db)
    member_repo = _get_member_repo(db)
    use_case = ListDepartmentsUseCase(repo, member_repo)
    return await use_case.execute(skip=skip, limit=limit, search=search)


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    body: CreateDepartmentRequest,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.auth.domain.models import UserModel
    from sqlalchemy import select as _select

    repo = _get_department_repo(db)
    member_repo = _get_member_repo(db)
    use_case = CreateDepartmentUseCase(repo, member_repo)
    department = await use_case.execute(
        name=body.name,
        created_by=current_user["id"],
        code=body.code,
        description=body.description,
        head_user_id=body.head_user_id,
    )
    if body.head_user_id:
        user_result = await db.execute(
            _select(UserModel).where(UserModel.id == body.head_user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.department_id = department.id
            if not user.department:
                user.department = department.name
            await db.flush()
    logger.info("department_created", department_id=str(department.id), user_id=current_user["id"])
    result = _department_to_dict(department)
    members = await member_repo.list_members(str(department.id))
    result["member_count"] = len(members)
    return result


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    body: UpdateDepartmentRequest,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.auth.domain.models import UserModel
    from sqlalchemy import select as _select

    repo = _get_department_repo(db)
    member_repo = _get_member_repo(db)
    use_case = UpdateDepartmentUseCase(repo, member_repo)
    department = await use_case.execute(
        department_id=department_id,
        name=body.name,
        code=body.code,
        description=body.description,
        head_user_id=body.head_user_id,
        is_active=body.is_active,
    )
    if body.head_user_id is not None and body.head_user_id:
        user_result = await db.execute(
            _select(UserModel).where(UserModel.id == body.head_user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.department_id = department_id
            if not user.department:
                user.department = department.name
            await db.flush()
    result = _department_to_dict(department)
    members = await member_repo.list_members(department_id)
    result["member_count"] = len(members)
    return result


@router.delete("/{department_id}", status_code=204)
async def delete_department(
    department_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repo = _get_department_repo(db)
    member_repo = _get_member_repo(db)
    use_case = DeleteDepartmentUseCase(repo, member_repo)
    await use_case.execute(department_id=department_id)


@router.get("/{department_id}")
async def get_department(
    department_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.exceptions import NotFoundException

    repo = _get_department_repo(db)
    member_repo = _get_member_repo(db)
    department = await repo.get_by_id(department_id)
    if not department:
        raise NotFoundException("Department", department_id)

    members = await member_repo.list_members(department_id)
    result = _department_to_dict(department)
    result["member_count"] = len(members)
    result["members"] = await _members_with_users(db, members)
    result["head_user"] = _head_user_dict(department)
    if department.head_user_id:
        head = await _user_summary(db, str(department.head_user_id))
        if head:
            result["head_user"] = head
    return result


@router.post("/{department_id}/members", response_model=DepartmentMemberResponse, status_code=201)
async def add_member(
    department_id: str,
    body: AddDepartmentMemberRequest,
    current_user: dict = Depends(require_admin_or_department_head),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.auth.domain.models import UserModel
    from sqlalchemy import select as _select

    repo = _get_department_repo(db)
    member_repo = _get_member_repo(db)
    use_case = AddDepartmentMemberUseCase(repo, member_repo)
    member = await use_case.execute(
        department_id=department_id,
        target_user_id=body.user_id,
        role=body.role,
    )
    user_result = await db.execute(
        _select(UserModel).where(UserModel.id == body.user_id)
    )
    user = user_result.scalar_one_or_none()
    if user:
        user.department_id = department_id
        if not user.department:
            user.department = (await repo.get_by_id(department_id)).name
        await db.flush()
    return _member_to_dict(member, await _user_summary(db, str(member.user_id)))


@router.put("/{department_id}/members/{target_user_id}", response_model=DepartmentMemberResponse)
async def update_member_role(
    department_id: str,
    target_user_id: str,
    body: UpdateDepartmentMemberRoleRequest,
    current_user: dict = Depends(require_admin_or_department_head),
    db: AsyncSession = Depends(get_db),
):
    repo = _get_department_repo(db)
    member_repo = _get_member_repo(db)
    use_case = UpdateDepartmentMemberRoleUseCase(repo, member_repo)
    member = await use_case.execute(
        department_id=department_id,
        target_user_id=target_user_id,
        role=body.role,
    )
    return _member_to_dict(member, await _user_summary(db, str(member.user_id)))


@router.delete("/{department_id}/members/{target_user_id}")
async def remove_member(
    department_id: str,
    target_user_id: str,
    current_user: dict = Depends(require_admin_or_department_head),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.auth.domain.models import UserModel
    from sqlalchemy import select as _select

    repo = _get_department_repo(db)
    member_repo = _get_member_repo(db)
    use_case = RemoveDepartmentMemberUseCase(repo, member_repo)
    result = await use_case.execute(
        department_id=department_id,
        target_user_id=target_user_id,
    )
    user_result = await db.execute(
        _select(UserModel).where(UserModel.id == target_user_id)
    )
    user = user_result.scalar_one_or_none()
    if user and str(user.department_id) == department_id:
        user.department_id = None
        await db.flush()
    return result