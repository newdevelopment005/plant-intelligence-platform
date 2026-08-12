from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.database import get_db
from app.modules.auth.domain.models import UserModel

router = APIRouter()


@router.get("/users")
async def list_users(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserModel).order_by(UserModel.created_at.desc()))
    users = result.scalars().all()

    count_result = await db.execute(select(func.count()).select_from(UserModel))
    total = count_result.scalar() or 0

    return {
        "items": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "institution": u.institution,
                "department": u.department,
                "department_id": str(u.department_id) if u.department_id else None,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
        "total": total,
    }


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    body: dict,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return {"message": "User not found"}

    role = body.get("role", user.role)
    allowed_roles = ("researcher", "technician", "principal_investigator", "admin", "readonly")
    if role not in allowed_roles:
        return {"message": "Invalid role. Must be one of: " + ", ".join(allowed_roles)}

    user.role = role
    await db.commit()
    return {"message": "Role updated", "id": user_id, "role": user.role}


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    body: dict,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return {"message": "User not found"}

    if user_id == current_user["id"]:
        return {"message": "You cannot deactivate your own account"}

    user.is_active = bool(body.get("is_active", user.is_active))
    await db.commit()
    return {"message": "Status updated", "id": user_id, "is_active": user.is_active}


@router.get("/audit-log")
async def get_audit_log(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: str | None = Query(None),
    action: str | None = Query(None),
):
    from app.modules.auth.infrastructure.audit_repository import AuditLogRepository

    items, total = await AuditLogRepository(db).list(
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
    )

    def _serialize(item: dict) -> dict:
        meta = item.get("metadata")
        return {
            "id": str(item.get("id")),
            "user_id": str(item.get("user_id")) if item.get("user_id") else None,
            "action": item.get("action"),
            "resource_type": item.get("resource_type"),
            "resource_id": item.get("resource_id"),
            "ip_address": item.get("ip_address"),
            "metadata": meta,
            "created_at": item.get("created_at").isoformat() if item.get("created_at") else None,
        }

    return {
        "items": [_serialize(i) for i in items],
        "total": total,
    }


@router.get("/health")
async def system_health():
    return {
        "status": "healthy",
        "database": "connected",
        "uptime": "running",
    }


@router.get("/stats")
async def usage_stats(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.lims.domain.models import SampleModel
    from app.modules.phenotyping.domain.models import ExperimentModel
    from app.modules.project.domain.models import ProjectModel

    user_count = (await db.execute(select(func.count()).select_from(UserModel))).scalar() or 0
    sample_count = (await db.execute(select(func.count()).select_from(SampleModel))).scalar() or 0
    exp_count = (await db.execute(select(func.count()).select_from(ExperimentModel))).scalar() or 0
    project_count = (await db.execute(select(func.count()).select_from(ProjectModel))).scalar() or 0

    return {
        "total_users": user_count,
        "total_projects": project_count,
        "total_samples": sample_count,
        "active_experiments": exp_count,
    }


@router.get("/teams")
async def admin_list_teams(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None, max_length=255),
):
    from app.modules.team.domain.models import TeamMemberModel, TeamModel

    stmt = select(TeamModel).order_by(TeamModel.created_at.desc()).offset(skip).limit(limit)
    if search:
        stmt = stmt.where(TeamModel.name.ilike(f"%{search}%"))
    teams = (await db.execute(stmt)).scalars().all()

    count_stmt = select(func.count()).select_from(TeamModel)
    if search:
        count_stmt = count_stmt.where(TeamModel.name.ilike(f"%{search}%"))
    total = (await db.execute(count_stmt)).scalar() or 0

    team_ids = [str(t.id) for t in teams]
    member_counts = {}
    if team_ids:
        counts = (
            await db.execute(
                select(TeamMemberModel.team_id, func.count(TeamMemberModel.id))
                .where(TeamMemberModel.team_id.in_(team_ids))
                .group_by(TeamMemberModel.team_id)
            )
        ).all()
        member_counts = {str(cid): cnt for cid, cnt in counts}

    return {
        "items": [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "owner_id": str(t.owner_id) if t.owner_id else None,
                "department_id": str(t.department_id) if t.department_id else None,
                "parent_id": str(t.parent_id) if t.parent_id else None,
                "member_count": member_counts.get(str(t.id), 0),
                "created_at": t.created_at.isoformat(),
            }
            for t in teams
        ],
        "total": total,
    }


@router.delete("/teams/{team_id}")
async def admin_delete_team(
    team_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.team.domain.models import TeamModel

    team = (
        await db.execute(select(TeamModel).where(TeamModel.id == team_id))
    ).scalar_one_or_none()
    if not team:
        return {"message": "Team not found"}
    await db.delete(team)
    await db.commit()
    return {"message": "Team deleted", "id": team_id}


@router.get("/departments")
async def admin_list_departments(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None, max_length=255),
):
    from app.modules.department.domain.models import DepartmentModel
    from app.modules.department.domain.models import DepartmentMemberModel

    stmt = (
        select(DepartmentModel)
        .order_by(DepartmentModel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    if search:
        stmt = stmt.where(DepartmentModel.name.ilike(f"%{search}%"))
    deps = (await db.execute(stmt)).scalars().all()

    count_stmt = select(func.count()).select_from(DepartmentModel)
    if search:
        count_stmt = count_stmt.where(DepartmentModel.name.ilike(f"%{search}%"))
    total = (await db.execute(count_stmt)).scalar() or 0

    dep_ids = [str(d.id) for d in deps]
    member_counts = {}
    if dep_ids:
        counts = (
            await db.execute(
                select(DepartmentMemberModel.department_id, func.count(DepartmentMemberModel.id))
                .where(DepartmentMemberModel.department_id.in_(dep_ids))
                .group_by(DepartmentMemberModel.department_id)
            )
        ).all()
        member_counts = {str(cid): cnt for cid, cnt in counts}

    return {
        "items": [
            {
                "id": str(d.id),
                "name": d.name,
                "code": d.code,
                "description": d.description,
                "head_user_id": str(d.head_user_id) if d.head_user_id else None,
                "is_active": bool(d.is_active),
                "member_count": member_counts.get(str(d.id), 0),
                "created_at": d.created_at.isoformat(),
            }
            for d in deps
        ],
        "total": total,
    }
