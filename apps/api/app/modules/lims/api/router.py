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
    return {"detail": "Sample deleted"}


class UpdateSampleRequest(BaseModel):
    name: str | None = None
    sample_type: str | None = None
    status: str | None = None
    location: str | None = None
    quantity: float | None = None
    unit: str | None = None


@router.put("/samples/{sample_id}")
async def update_sample(
    sample_id: str,
    body: UpdateSampleRequest,
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

    if body.name is not None:
        sample.name = body.name
    if body.sample_type is not None:
        sample.sample_type = body.sample_type
    if body.status is not None:
        sample.status = body.status
    if body.location is not None:
        sample.location = body.location
    if body.quantity is not None:
        sample.quantity = body.quantity
    if body.unit is not None:
        sample.unit = body.unit

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


class CreateEquipmentRequest(BaseModel):
    name: str
    equipment_code: str
    description: str | None = None
    category: str | None = None
    status: str = "available"
    location: str | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    serial_number: str | None = None


class UpdateEquipmentRequest(BaseModel):
    name: str | None = None
    equipment_code: str | None = None
    description: str | None = None
    category: str | None = None
    status: str | None = None
    location: str | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    serial_number: str | None = None


def _equipment_to_dict(e: EquipmentModel) -> dict:
    return {
        "id": str(e.id),
        "name": e.name,
        "equipment_code": e.equipment_code,
        "description": e.description,
        "status": e.status,
        "category": e.category,
        "location": e.location,
        "manufacturer": e.manufacturer,
        "model_number": e.model_number,
        "serial_number": e.serial_number,
        "created_at": e.created_at.isoformat(),
        "updated_at": e.updated_at.isoformat(),
    }


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
        "items": [_equipment_to_dict(e) for e in equipment],
        "total": len(equipment),
    }


@router.post("/equipment", status_code=201)
async def create_equipment(
    body: CreateEquipmentRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if not body.name.strip():
        raise HTTPException(status_code=422, detail="Equipment name is required")

    existing = await db.execute(
        select(EquipmentModel).where(EquipmentModel.equipment_code == body.equipment_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Equipment code already exists")

    equipment = EquipmentModel(
        name=body.name.strip(),
        equipment_code=body.equipment_code.strip(),
        description=body.description,
        category=body.category,
        status=body.status,
        location=body.location,
        manufacturer=body.manufacturer,
        model_number=body.model_number,
        serial_number=body.serial_number,
    )
    db.add(equipment)
    await db.commit()
    await db.refresh(equipment)

    return _equipment_to_dict(equipment)


@router.put("/equipment/{equipment_id}")
async def update_equipment(
    equipment_id: str,
    body: UpdateEquipmentRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EquipmentModel).where(EquipmentModel.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    if body.name is not None:
        if not body.name.strip():
            raise HTTPException(status_code=422, detail="Equipment name cannot be empty")
        equipment.name = body.name.strip()
    if body.equipment_code is not None:
        if not body.equipment_code.strip():
            raise HTTPException(status_code=422, detail="Equipment code cannot be empty")
        dup = await db.execute(
            select(EquipmentModel).where(
                EquipmentModel.equipment_code == body.equipment_code.strip(),
                EquipmentModel.id != equipment_id,
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Equipment code already exists")
        equipment.equipment_code = body.equipment_code.strip()
    if body.description is not None:
        equipment.description = body.description
    if body.category is not None:
        equipment.category = body.category
    if body.status is not None:
        equipment.status = body.status
    if body.location is not None:
        equipment.location = body.location
    if body.manufacturer is not None:
        equipment.manufacturer = body.manufacturer
    if body.model_number is not None:
        equipment.model_number = body.model_number
    if body.serial_number is not None:
        equipment.serial_number = body.serial_number

    await db.commit()
    await db.refresh(equipment)

    return _equipment_to_dict(equipment)


@router.delete("/equipment/{equipment_id}")
async def delete_equipment(
    equipment_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EquipmentModel).where(EquipmentModel.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    await db.delete(equipment)
    await db.commit()
    return {"detail": "Equipment deleted"}


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
