import structlog
from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.germplasm.api.schemas import (
    CreateAccessionRequest,
    CreatePassportDataRequest,
    CreatePedigreeRequest,
    CreateSeedStorageRequest,
    CreateSpeciesRequest,
    UpdateAccessionRequest,
    UpdatePassportDataRequest,
    UpdateSeedStorageRequest,
    UpdateSpeciesRequest,
)
from app.modules.germplasm.domain.use_cases import (
    CreateAccessionUseCase,
    CreatePassportDataUseCase,
    CreatePedigreeUseCase,
    CreateSeedStorageUseCase,
    CreateSpeciesUseCase,
    DeleteAccessionUseCase,
    DeleteGermplasmFileUseCase,
    DeleteGermplasmImageUseCase,
    DeleteSeedStorageUseCase,
    DeleteSpeciesUseCase,
    GetAccessionUseCase,
    GetPassportDataUseCase,
    GetPedigreeTreeUseCase,
    GetPedigreeUseCase,
    GetSpeciesUseCase,
    ListAccessionsUseCase,
    ListGermplasmFilesUseCase,
    ListGermplasmImagesUseCase,
    ListSeedStoragesUseCase,
    ListSpeciesUseCase,
    SearchAccessionsUseCase,
    UpdateAccessionUseCase,
    UpdatePassportDataUseCase,
    UpdateSeedStorageUseCase,
    UpdateSpeciesUseCase,
    UploadGermplasmFileUseCase,
    UploadGermplasmImageUseCase,
)
from app.modules.germplasm.infrastructure.accession_repository import AccessionRepository
from app.modules.germplasm.infrastructure.repositories import (
    GermplasmFileRepository,
    GermplasmImageRepository,
    PassportDataRepository,
    PedigreeRepository,
    SeedStorageRepository,
)
from app.modules.germplasm.infrastructure.species_repository import SpeciesRepository

logger = structlog.get_logger()
router = APIRouter()


def _get_repos(db: AsyncSession):
    return {
        "species": SpeciesRepository(db),
        "accession": AccessionRepository(db),
        "passport": PassportDataRepository(db),
        "pedigree": PedigreeRepository(db),
        "storage": SeedStorageRepository(db),
        "image": GermplasmImageRepository(db),
        "file": GermplasmFileRepository(db),
    }


@router.get("/species", response_model=None)
async def list_species(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
):
    repos = _get_repos(db)
    use_case = ListSpeciesUseCase(repos["species"])
    return await use_case.execute(skip=skip, limit=limit, search=search)


@router.post("/species", status_code=201)
async def create_species(
    body: CreateSpeciesRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateSpeciesUseCase(repos["species"])
    species = await use_case.execute(
        common_name=body.common_name,
        scientific_name=body.scientific_name,
        family=body.family,
        genus=body.genus,
        species_epithet=body.species_epithet,
        description=body.description,
    )
    logger.info("species_created", species_id=str(species.id))
    return {
        "id": str(species.id),
        "common_name": species.common_name,
        "scientific_name": species.scientific_name,
        "family": species.family,
        "genus": species.genus,
        "species_epithet": species.species_epithet,
        "created_at": species.created_at.isoformat(),
    }


@router.get("/species/{species_id}")
async def get_species(
    species_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetSpeciesUseCase(repos["species"])
    species = await use_case.execute(species_id)
    return {
        "id": str(species.id),
        "common_name": species.common_name,
        "scientific_name": species.scientific_name,
        "family": species.family,
        "genus": species.genus,
        "species_epithet": species.species_epithet,
        "description": species.description,
        "created_at": species.created_at.isoformat(),
    }


@router.put("/species/{species_id}")
async def update_species(
    species_id: str,
    body: UpdateSpeciesRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdateSpeciesUseCase(repos["species"])
    species = await use_case.execute(
        species_id=species_id,
        common_name=body.common_name,
        scientific_name=body.scientific_name,
        family=body.family,
        genus=body.genus,
        species_epithet=body.species_epithet,
        description=body.description,
    )
    return {
        "id": str(species.id),
        "common_name": species.common_name,
        "scientific_name": species.scientific_name,
        "family": species.family,
        "genus": species.genus,
        "species_epithet": species.species_epithet,
        "created_at": species.created_at.isoformat(),
    }


@router.delete("/species/{species_id}")
async def delete_species(
    species_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteSpeciesUseCase(repos["species"])
    await use_case.execute(species_id)
    return {"message": "Species deleted successfully"}


@router.get("/accessions", response_model=None)
async def list_accessions(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    species_id: str | None = Query(None),
    project_id: str | None = Query(None),
    status: str | None = Query(None, pattern="^(available|limited|unavailable|reserved)$"),
    search: str | None = Query(None, max_length=255),
):
    repos = _get_repos(db)
    use_case = ListAccessionsUseCase(repos["accession"])
    return await use_case.execute(
        skip=skip,
        limit=limit,
        species_id=species_id,
        project_id=project_id,
        status=status,
        search=search,
        user_id=str(current_user["id"]),
    )


@router.post("/accessions", status_code=201)
async def create_accession(
    body: CreateAccessionRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateAccessionUseCase(repos["accession"], repos["species"])
    accession = await use_case.execute(
        accession_number=body.accession_number,
        species_id=body.species_id,
        name=body.name,
        project_id=body.project_id,
        description=body.description,
        collection_source=body.collection_source,
        collection_date=body.collection_date,
        collection_location=body.collection_location,
        latitude=body.latitude,
        longitude=body.longitude,
        altitude=body.altitude,
        tags=body.tags,
        user_id=str(current_user["id"]),
    )
    logger.info("accession_created", accession_id=str(accession.id))
    return {
        "id": str(accession.id),
        "accession_number": accession.accession_number,
        "name": accession.name,
        "species_id": str(accession.species_id),
        "project_id": str(accession.project_id) if accession.project_id else None,
        "description": accession.description,
        "availability_status": accession.availability_status,
        "tags": accession.tags,
        "created_by": str(accession.created_by),
        "created_at": accession.created_at.isoformat(),
        "updated_at": accession.updated_at.isoformat(),
    }


@router.get("/accessions/search")
async def search_accessions(
    q: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    repos = _get_repos(db)
    use_case = SearchAccessionsUseCase(repos["accession"])
    return await use_case.execute(query=q, skip=skip, limit=limit)


@router.get("/accessions/{accession_id}")
async def get_accession(
    accession_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetAccessionUseCase(repos["accession"])
    accession = await use_case.execute(accession_id)
    return {
        "id": str(accession.id),
        "accession_number": accession.accession_number,
        "name": accession.name,
        "species_id": str(accession.species_id),
        "project_id": str(accession.project_id) if accession.project_id else None,
        "description": accession.description,
        "collection_source": accession.collection_source,
        "collection_date": accession.collection_date.isoformat() if accession.collection_date else None,
        "collection_location": accession.collection_location,
        "latitude": accession.latitude,
        "longitude": accession.longitude,
        "altitude": accession.altitude,
        "availability_status": accession.availability_status,
        "tags": accession.tags,
        "metadata": accession.metadata_json,
        "created_by": str(accession.created_by),
        "created_at": accession.created_at.isoformat(),
        "updated_at": accession.updated_at.isoformat(),
    }


@router.put("/accessions/{accession_id}")
async def update_accession(
    accession_id: str,
    body: UpdateAccessionRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdateAccessionUseCase(repos["accession"])
    accession = await use_case.execute(
        accession_id=accession_id,
        user_id=str(current_user["id"]),
        name=body.name,
        description=body.description,
        collection_source=body.collection_source,
        collection_location=body.collection_location,
        availability_status=body.availability_status,
        tags=body.tags,
    )
    return {
        "id": str(accession.id),
        "accession_number": accession.accession_number,
        "name": accession.name,
        "species_id": str(accession.species_id),
        "description": accession.description,
        "availability_status": accession.availability_status,
        "tags": accession.tags,
        "created_at": accession.created_at.isoformat(),
        "updated_at": accession.updated_at.isoformat(),
    }


@router.delete("/accessions/{accession_id}")
async def delete_accession(
    accession_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteAccessionUseCase(repos["accession"])
    await use_case.execute(accession_id, str(current_user["id"]))
    return {"message": "Accession deleted successfully"}


@router.get("/accessions/{accession_id}/passport")
async def get_passport_data(
    accession_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetPassportDataUseCase(repos["passport"])
    passport = await use_case.execute(accession_id)
    if not passport:
        return None
    return {
        "id": str(passport.id),
        "accession_id": str(passport.accession_id),
        "institute_code": passport.institute_code,
        "institute_name": passport.institute_name,
        "country_code": passport.country_code,
        "collection_number": passport.collection_number,
        "collection_source": passport.collection_source,
        "status": passport.status,
        "duplicates": passport.duplicates,
        "remarks": passport.remarks,
        "created_at": passport.created_at.isoformat(),
        "updated_at": passport.updated_at.isoformat(),
    }


@router.post("/accessions/{accession_id}/passport", status_code=201)
async def create_passport_data(
    accession_id: str,
    body: CreatePassportDataRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreatePassportDataUseCase(repos["passport"], repos["accession"])
    passport = await use_case.execute(
        accession_id=accession_id,
        institute_code=body.institute_code,
        institute_name=body.institute_name,
        country_code=body.country_code,
        collection_number=body.collection_number,
        collection_source=body.collection_source,
        status=body.status,
        duplicates=body.duplicates,
        remarks=body.remarks,
    )
    return {
        "id": str(passport.id),
        "accession_id": str(passport.accession_id),
        "institute_code": passport.institute_code,
        "institute_name": passport.institute_name,
        "country_code": passport.country_code,
        "collection_number": passport.collection_number,
        "collection_source": passport.collection_source,
        "status": passport.status,
        "duplicates": passport.duplicates,
        "remarks": passport.remarks,
        "created_at": passport.created_at.isoformat(),
        "updated_at": passport.updated_at.isoformat(),
    }


@router.put("/accessions/{accession_id}/passport")
async def update_passport_data(
    accession_id: str,
    body: UpdatePassportDataRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdatePassportDataUseCase(repos["passport"])
    passport = await use_case.execute(
        accession_id=accession_id,
        institute_code=body.institute_code,
        institute_name=body.institute_name,
        country_code=body.country_code,
        collection_number=body.collection_number,
        collection_source=body.collection_source,
        status=body.status,
        duplicates=body.duplicates,
        remarks=body.remarks,
    )
    return {
        "id": str(passport.id),
        "accession_id": str(passport.accession_id),
        "institute_code": passport.institute_code,
        "institute_name": passport.institute_name,
        "country_code": passport.country_code,
        "collection_number": passport.collection_number,
        "collection_source": passport.collection_source,
        "status": passport.status,
        "duplicates": passport.duplicates,
        "remarks": passport.remarks,
        "created_at": passport.created_at.isoformat(),
        "updated_at": passport.updated_at.isoformat(),
    }


@router.get("/accessions/{accession_id}/pedigree")
async def get_pedigree(
    accession_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetPedigreeUseCase(repos["pedigree"])
    pedigree = await use_case.execute(accession_id)
    if not pedigree:
        return None
    return {
        "id": str(pedigree.id),
        "accession_id": str(pedigree.accession_id),
        "parent1_accession_id": str(pedigree.parent1_accession_id) if pedigree.parent1_accession_id else None,
        "parent2_accession_id": str(pedigree.parent2_accession_id) if pedigree.parent2_accession_id else None,
        "parent1_name": pedigree.parent1_name,
        "parent2_name": pedigree.parent2_name,
        "cross_type": pedigree.cross_type,
        "generation": pedigree.generation,
        "notes": pedigree.notes,
        "created_at": pedigree.created_at.isoformat(),
        "updated_at": pedigree.updated_at.isoformat(),
    }


@router.get("/accessions/{accession_id}/pedigree/tree")
async def get_pedigree_tree(
    accession_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    depth: int = Query(3, ge=1, le=10),
):
    repos = _get_repos(db)
    use_case = GetPedigreeTreeUseCase(repos["pedigree"])
    return await use_case.execute(accession_id, depth)


@router.post("/accessions/{accession_id}/pedigree", status_code=201)
async def create_pedigree(
    accession_id: str,
    body: CreatePedigreeRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreatePedigreeUseCase(repos["pedigree"], repos["accession"])
    pedigree = await use_case.execute(
        accession_id=accession_id,
        parent1_accession_id=body.parent1_accession_id,
        parent2_accession_id=body.parent2_accession_id,
        parent1_name=body.parent1_name,
        parent2_name=body.parent2_name,
        cross_type=body.cross_type,
        generation=body.generation,
        notes=body.notes,
    )
    return {
        "id": str(pedigree.id),
        "accession_id": str(pedigree.accession_id),
        "parent1_accession_id": str(pedigree.parent1_accession_id) if pedigree.parent1_accession_id else None,
        "parent2_accession_id": str(pedigree.parent2_accession_id) if pedigree.parent2_accession_id else None,
        "parent1_name": pedigree.parent1_name,
        "parent2_name": pedigree.parent2_name,
        "cross_type": pedigree.cross_type,
        "generation": pedigree.generation,
        "notes": pedigree.notes,
        "created_at": pedigree.created_at.isoformat(),
        "updated_at": pedigree.updated_at.isoformat(),
    }


@router.get("/accessions/{accession_id}/storage")
async def list_seed_storages(
    accession_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = ListSeedStoragesUseCase(repos["storage"])
    storages = await use_case.execute(accession_id)
    return [
        {
            "id": str(s.id),
            "accession_id": str(s.accession_id),
            "location": s.location,
            "container_type": s.container_type,
            "quantity_grams": s.quantity_grams,
            "seed_count": s.seed_count,
            "storage_conditions": s.storage_conditions,
            "storage_date": s.storage_date.isoformat() if s.storage_date else None,
            "expiry_date": s.expiry_date.isoformat() if s.expiry_date else None,
            "viability": s.viability,
            "notes": s.notes,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in storages
    ]


@router.post("/accessions/{accession_id}/storage", status_code=201)
async def create_seed_storage(
    accession_id: str,
    body: CreateSeedStorageRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateSeedStorageUseCase(repos["storage"], repos["accession"])
    storage = await use_case.execute(
        accession_id=accession_id,
        location=body.location,
        container_type=body.container_type,
        quantity_grams=body.quantity_grams,
        seed_count=body.seed_count,
        storage_conditions=body.storage_conditions,
        storage_date=body.storage_date,
        expiry_date=body.expiry_date,
        viability=body.viability,
        notes=body.notes,
    )
    return {
        "id": str(storage.id),
        "accession_id": str(storage.accession_id),
        "location": storage.location,
        "container_type": storage.container_type,
        "quantity_grams": storage.quantity_grams,
        "seed_count": storage.seed_count,
        "storage_conditions": storage.storage_conditions,
        "storage_date": storage.storage_date.isoformat() if storage.storage_date else None,
        "expiry_date": storage.expiry_date.isoformat() if storage.expiry_date else None,
        "viability": storage.viability,
        "notes": storage.notes,
        "created_at": storage.created_at.isoformat(),
        "updated_at": storage.updated_at.isoformat(),
    }


@router.put("/storage/{storage_id}")
async def update_seed_storage(
    storage_id: str,
    body: UpdateSeedStorageRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdateSeedStorageUseCase(repos["storage"])
    storage = await use_case.execute(
        storage_id=storage_id,
        location=body.location,
        container_type=body.container_type,
        quantity_grams=body.quantity_grams,
        seed_count=body.seed_count,
        storage_conditions=body.storage_conditions,
        expiry_date=body.expiry_date,
        viability=body.viability,
        notes=body.notes,
    )
    return {
        "id": str(storage.id),
        "accession_id": str(storage.accession_id),
        "location": storage.location,
        "container_type": storage.container_type,
        "quantity_grams": storage.quantity_grams,
        "seed_count": storage.seed_count,
        "storage_conditions": storage.storage_conditions,
        "storage_date": storage.storage_date.isoformat() if storage.storage_date else None,
        "expiry_date": storage.expiry_date.isoformat() if storage.expiry_date else None,
        "viability": storage.viability,
        "notes": storage.notes,
        "created_at": storage.created_at.isoformat(),
        "updated_at": storage.updated_at.isoformat(),
    }


@router.delete("/storage/{storage_id}")
async def delete_seed_storage(
    storage_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteSeedStorageUseCase(repos["storage"])
    await use_case.execute(storage_id)
    return {"message": "Seed storage deleted successfully"}


@router.get("/accessions/{accession_id}/images")
async def list_germplasm_images(
    accession_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = ListGermplasmImagesUseCase(repos["image"])
    images = await use_case.execute(accession_id)
    return [
        {
            "id": str(img.id),
            "accession_id": str(img.accession_id),
            "filename": img.filename,
            "original_filename": img.original_filename,
            "mime_type": img.mime_type,
            "file_size": img.file_size,
            "caption": img.caption,
            "image_type": img.image_type,
            "taken_at": img.taken_at.isoformat() if img.taken_at else None,
            "uploaded_by": str(img.uploaded_by),
            "created_at": img.created_at.isoformat(),
        }
        for img in images
    ]


@router.post("/accessions/{accession_id}/images", status_code=201)
async def upload_germplasm_image(
    accession_id: str,
    file: UploadFile = File(...),
    caption: str | None = None,
    image_type: str | None = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    import os
    import uuid

    upload_dir = f"uploads/germplasm/{accession_id}/images"
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    storage_path = os.path.join(upload_dir, filename)

    content = await file.read()
    with open(storage_path, "wb") as f:
        f.write(content)

    repos = _get_repos(db)
    use_case = UploadGermplasmImageUseCase(repos["image"], repos["accession"])
    image = await use_case.execute(
        accession_id=accession_id,
        filename=filename,
        original_filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        storage_path=storage_path,
        caption=caption,
        image_type=image_type,
        uploaded_by=str(current_user["id"]),
    )
    return {
        "id": str(image.id),
        "accession_id": str(image.accession_id),
        "filename": image.filename,
        "original_filename": image.original_filename,
        "mime_type": image.mime_type,
        "file_size": image.file_size,
        "caption": image.caption,
        "image_type": image.image_type,
        "uploaded_by": str(image.uploaded_by),
        "created_at": image.created_at.isoformat(),
    }


@router.delete("/images/{image_id}")
async def delete_germplasm_image(
    image_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteGermplasmImageUseCase(repos["image"])
    await use_case.execute(image_id=image_id, user_id=str(current_user["id"]))
    return {"message": "Image deleted successfully"}


@router.get("/accessions/{accession_id}/files")
async def list_germplasm_files(
    accession_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = ListGermplasmFilesUseCase(repos["file"])
    files = await use_case.execute(accession_id)
    return [
        {
            "id": str(f.id),
            "accession_id": str(f.accession_id),
            "filename": f.filename,
            "original_filename": f.original_filename,
            "mime_type": f.mime_type,
            "file_size": f.file_size,
            "description": f.description,
            "file_type": f.file_type,
            "uploaded_by": str(f.uploaded_by),
            "created_at": f.created_at.isoformat(),
        }
        for f in files
    ]


@router.post("/accessions/{accession_id}/files", status_code=201)
async def upload_germplasm_file(
    accession_id: str,
    file: UploadFile = File(...),
    description: str | None = None,
    file_type: str | None = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    import os
    import uuid

    upload_dir = f"uploads/germplasm/{accession_id}/files"
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    storage_path = os.path.join(upload_dir, filename)

    content = await file.read()
    with open(storage_path, "wb") as f:
        f.write(content)

    repos = _get_repos(db)
    use_case = UploadGermplasmFileUseCase(repos["file"], repos["accession"])
    file_model = await use_case.execute(
        accession_id=accession_id,
        filename=filename,
        original_filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        storage_path=storage_path,
        description=description,
        file_type=file_type,
        uploaded_by=str(current_user["id"]),
    )
    return {
        "id": str(file_model.id),
        "accession_id": str(file_model.accession_id),
        "filename": file_model.filename,
        "original_filename": file_model.original_filename,
        "mime_type": file_model.mime_type,
        "file_size": file_model.file_size,
        "description": file_model.description,
        "file_type": file_model.file_type,
        "uploaded_by": str(file_model.uploaded_by),
        "created_at": file_model.created_at.isoformat(),
    }


@router.delete("/files/{file_id}")
async def delete_germplasm_file(
    file_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteGermplasmFileUseCase(repos["file"])
    await use_case.execute(file_id=file_id, user_id=str(current_user["id"]))
    return {"message": "File deleted successfully"}
