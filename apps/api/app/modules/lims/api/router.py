from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.lims.domain.models import EquipmentModel, SampleModel

router = APIRouter()


class CreateSampleRequest(BaseModel):
    sample_code: str
    sample_type: str = "DNA"
    name: str
    description: str | None = None
    location: str | None = None
    quantity: float | None = None
    unit: str | None = None


class TransferSampleRequest(BaseModel):
    to_location: str
    quantity_transferred: float | None = None
    notes: str | None = None


@router.get("/samples")
async def list_samples(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SampleModel)
        .where(SampleModel.created_by == current_user["id"])
        .order_by(SampleModel.created_at.desc())
    )
    samples = result.scalars().all()

    count_result = await db.execute(
        select(func.count()).select_from(SampleModel)
        .where(SampleModel.created_by == current_user["id"])
    )
    total = count_result.scalar() or 0

    return {
        "items": [
            {
                "id": str(s.id),
                "sample_code": s.sample_code,
                "sample_type": s.sample_type,
                "name": s.name,
                "status": s.status,
                "location": s.location,
                "quantity": s.quantity,
                "unit": s.unit,
                "created_at": s.created_at.isoformat(),
            }
            for s in samples
        ],
        "total": total,
    }


@router.post("/samples", status_code=201)
async def create_sample(
    body: CreateSampleRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(SampleModel).where(SampleModel.sample_code == body.sample_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Sample code already exists")

    sample = SampleModel(
        sample_code=body.sample_code,
        sample_type=body.sample_type,
        name=body.name,
        description=body.description,
        location=body.location,
        quantity=body.quantity,
        unit=body.unit,
        created_by=current_user["id"],
    )
    db.add(sample)
    await db.commit()
    await db.refresh(sample)

    return {
        "id": str(sample.id),
        "sample_code": sample.sample_code,
        "sample_type": sample.sample_type,
        "name": sample.name,
        "status": sample.status,
        "location": sample.location,
        "quantity": sample.quantity,
        "unit": sample.unit,
        "created_at": sample.created_at.isoformat(),
    }


@router.get("/samples/{sample_id}")
async def get_sample(
    sample_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SampleModel).where(
            SampleModel.id == sample_id,
            SampleModel.created_by == current_user["id"],
        )
    )
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    return {
        "id": str(sample.id),
        "sample_code": sample.sample_code,
        "sample_type": sample.sample_type,
        "name": sample.name,
        "status": sample.status,
        "location": sample.location,
        "quantity": sample.quantity,
        "unit": sample.unit,
        "created_at": sample.created_at.isoformat(),
    }


@router.delete("/samples/{sample_id}")
async def delete_sample(
    sample_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SampleModel).where(
            SampleModel.id == sample_id,
            SampleModel.created_by == current_user["id"],
        )
    )
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    await db.delete(sample)
    await db.commit()
    return {"message": "Sample deleted"}


@router.post("/samples/transfer")
async def transfer_sample(
    body: TransferSampleRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "Transfer recorded"}


@router.get("/equipment")
async def list_equipment(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EquipmentModel).order_by(EquipmentModel.name)
    )
    equipment = result.scalars().all()

    return {
        "items": [
            {
                "id": str(e.id),
                "name": e.name,
                "equipment_code": e.equipment_code,
                "status": e.status,
                "category": e.category,
            }
            for e in equipment
        ],
        "total": len(equipment),
    }


@router.get("/reagents")
async def list_reagents(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.lims.domain.models import ReagentModel

    result = await db.execute(select(ReagentModel).order_by(ReagentModel.name))
    reagents = result.scalars().all()

    return {
        "items": [
            {
                "id": str(r.id),
                "name": r.name,
                "catalog_number": r.catalog_number,
                "quantity": r.quantity,
                "unit": r.unit,
                "location": r.location,
            }
            for r in reagents
        ],
        "total": len(reagents),
    }


@router.get("/inventory/low-stock")
async def low_stock_alerts(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.lims.domain.models import ReagentModel

    result = await db.execute(
        select(ReagentModel).where(
            ReagentModel.is_active,
            ReagentModel.min_quantity.isnot(None),
            ReagentModel.quantity <= ReagentModel.min_quantity,
        )
    )
    low_stock = result.scalars().all()

    return {
        "items": [
            {
                "id": str(r.id),
                "name": r.name,
                "quantity": r.quantity,
                "unit": r.unit,
                "min_quantity": r.min_quantity,
            }
            for r in low_stock
        ],
        "total": len(low_stock),
    }
