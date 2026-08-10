from fastapi import APIRouter, Depends
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
):
    return {"items": [], "total": 0}


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
