from fastapi import APIRouter

router = APIRouter()


@router.get("/samples")
async def list_samples():
    return {"message": "LIMS module - list samples"}


@router.post("/samples")
async def create_sample():
    return {"message": "LIMS module - create sample"}


@router.get("/samples/{sample_id}")
async def get_sample(sample_id: str):
    return {"message": "LIMS module - get sample", "id": sample_id}


@router.post("/samples/transfer")
async def transfer_sample():
    return {"message": "LIMS module - transfer sample"}


@router.get("/equipment")
async def list_equipment():
    return {"message": "LIMS module - list equipment"}


@router.get("/reagents")
async def list_reagents():
    return {"message": "LIMS module - list reagents"}


@router.get("/inventory/low-stock")
async def low_stock_alerts():
    return {"message": "LIMS module - low stock alerts"}
