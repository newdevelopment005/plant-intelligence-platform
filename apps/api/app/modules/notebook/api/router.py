from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.notebook.domain.models import NotebookEntryModel

router = APIRouter()


class CreateEntryRequest(BaseModel):
    title: str
    content: str
    entry_type: str = "note"
    tags: list[str] | None = None


class UpdateEntryRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    entry_type: str | None = None
    tags: list[str] | None = None


@router.get("/entries")
async def list_entries(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotebookEntryModel)
        .where(NotebookEntryModel.created_by == current_user["id"])
        .order_by(NotebookEntryModel.created_at.desc())
    )
    entries = result.scalars().all()

    count_result = await db.execute(
        select(func.count()).select_from(NotebookEntryModel)
        .where(NotebookEntryModel.created_by == current_user["id"])
    )
    total = count_result.scalar() or 0

    return {
        "items": [
            {
                "id": str(e.id),
                "title": e.title,
                "content": e.content,
                "entry_type": e.entry_type,
                "tags": e.tags,
                "is_locked": e.is_locked,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ],
        "total": total,
    }


@router.post("/entries", status_code=201)
async def create_entry(
    body: CreateEntryRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    entry = NotebookEntryModel(
        title=body.title,
        content=body.content,
        entry_type=body.entry_type,
        tags=body.tags,
        created_by=current_user["id"],
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    return {
        "id": str(entry.id),
        "title": entry.title,
        "content": entry.content,
        "entry_type": entry.entry_type,
        "tags": entry.tags,
        "is_locked": entry.is_locked,
        "created_at": entry.created_at.isoformat(),
    }


@router.get("/entries/{entry_id}")
async def get_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotebookEntryModel).where(
            NotebookEntryModel.id == entry_id,
            NotebookEntryModel.created_by == current_user["id"],
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {
        "id": str(entry.id),
        "title": entry.title,
        "content": entry.content,
        "entry_type": entry.entry_type,
        "tags": entry.tags,
        "is_locked": entry.is_locked,
        "created_at": entry.created_at.isoformat(),
    }


@router.put("/entries/{entry_id}")
async def update_entry(
    entry_id: str,
    body: UpdateEntryRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotebookEntryModel).where(
            NotebookEntryModel.id == entry_id,
            NotebookEntryModel.created_by == current_user["id"],
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry.is_locked:
        raise HTTPException(status_code=400, detail="Entry is locked")

    if body.title is not None:
        entry.title = body.title
    if body.content is not None:
        entry.content = body.content
    if body.entry_type is not None:
        entry.entry_type = body.entry_type
    if body.tags is not None:
        entry.tags = body.tags

    await db.commit()
    await db.refresh(entry)

    return {
        "id": str(entry.id),
        "title": entry.title,
        "content": entry.content,
        "entry_type": entry.entry_type,
        "tags": entry.tags,
        "is_locked": entry.is_locked,
        "created_at": entry.created_at.isoformat(),
    }


@router.post("/entries/{entry_id}/lock")
async def lock_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotebookEntryModel).where(
            NotebookEntryModel.id == entry_id,
            NotebookEntryModel.created_by == current_user["id"],
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry.is_locked = True
    await db.commit()
    return {"message": "Entry locked"}


@router.post("/entries/{entry_id}/unlock")
async def unlock_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotebookEntryModel).where(
            NotebookEntryModel.id == entry_id,
            NotebookEntryModel.created_by == current_user["id"],
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry.is_locked = False
    await db.commit()
    return {"message": "Entry unlocked"}


@router.get("/entries/{entry_id}/versions")
async def list_versions(
    entry_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return {"items": [], "total": 0}
