from fastapi import APIRouter

router = APIRouter()


@router.get("/entries")
async def list_entries():
    return {"message": "Notebook module - list entries"}


@router.post("/entries")
async def create_entry():
    return {"message": "Notebook module - create entry"}


@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str):
    return {"message": "Notebook module - get entry", "id": entry_id}


@router.put("/entries/{entry_id}")
async def update_entry(entry_id: str):
    return {"message": "Notebook module - update entry", "id": entry_id}


@router.post("/entries/{entry_id}/lock")
async def lock_entry(entry_id: str):
    return {"message": "Notebook module - lock entry", "id": entry_id}


@router.post("/entries/{entry_id}/unlock")
async def unlock_entry(entry_id: str):
    return {"message": "Notebook module - unlock entry", "id": entry_id}


@router.get("/entries/{entry_id}/versions")
async def list_versions(entry_id: str):
    return {"message": "Notebook module - list versions", "id": entry_id}
