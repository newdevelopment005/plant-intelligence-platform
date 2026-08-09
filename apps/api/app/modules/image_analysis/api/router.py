from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.image_analysis.api.schemas import (
    AnalysisJobResponse,
    CreateAnalysisJobRequest,
    ImageResponse,
    PaginatedAnalysisJobsResponse,
    PaginatedAnalysisResultsResponse,
    PaginatedImagesResponse,
    UpdateImageRequest,
    UploadImageRequest,
)
from app.modules.image_analysis.domain.use_cases import (
    CreateAnalysisJobUseCase,
    DeleteImageUseCase,
    GetAnalysisJobUseCase,
    GetAnalysisResultsUseCase,
    GetImageUseCase,
    ListAnalysisJobsUseCase,
    ListImagesUseCase,
    UpdateImageUseCase,
    UploadImageUseCase,
)

router = APIRouter(redirect_slashes=False)


def _image_to_dict(img) -> dict:
    return {
        "id": str(img.id),
        "name": img.name,
        "description": img.description,
        "file_url": img.file_url,
        "thumbnail_url": img.thumbnail_url,
        "file_size_bytes": img.file_size_bytes,
        "mime_type": img.mime_type,
        "width": img.width,
        "height": img.height,
        "image_type": img.image_type,
        "source_module": img.source_module,
        "source_id": img.source_id,
        "species": img.species,
        "tissue_type": img.tissue_type,
        "growth_stage": img.growth_stage,
        "magnification": img.magnification,
        "tags": img.tags,
        "project_id": str(img.project_id) if img.project_id else None,
        "created_by": str(img.created_by),
        "created_at": img.created_at.isoformat(),
        "updated_at": img.updated_at.isoformat(),
    }


def _job_to_dict(job) -> dict:
    return {
        "id": str(job.id),
        "image_id": str(job.image_id),
        "analysis_type": job.analysis_type,
        "status": job.status,
        "error_message": job.error_message,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "runtime_seconds": job.runtime_seconds,
        "model_version": job.model_version,
        "project_id": str(job.project_id) if job.project_id else None,
        "created_by": str(job.created_by),
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


# ────────────────────────── Plant Images ──────────────────────────────
@router.post("", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    request: UploadImageRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.image_repository import PlantImageRepository
    repo = PlantImageRepository(db)
    uc = UploadImageUseCase(image_repo=repo)
    image = await uc.execute(
        name=request.name,
        file_url=request.file_url,
        user_id=current_user["id"],
        description=request.description,
        image_type=request.image_type,
        source_module=request.source_module,
        source_id=request.source_id,
        species=request.species,
        tissue_type=request.tissue_type,
        growth_stage=request.growth_stage,
        magnification=request.magnification,
        file_size_bytes=request.file_size_bytes,
        mime_type=request.mime_type,
        width=request.width,
        height=request.height,
        tags=request.tags,
        project_id=request.project_id,
        metadata_json=request.metadata_json,
    )
    return _image_to_dict(image)


@router.post("/upload", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image_file(
    file: UploadFile = File(...),
    name: str = Form(""),
    description: str = Form(None),
    image_type: str = Form("general"),
    species: str = Form(None),
    tags: str = Form(None),
    project_id: str = Form(None),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    import json
    from app.shared.file_storage import save_uploaded_file

    file_url = await save_uploaded_file(file, "images")
    file_tags = json.loads(tags) if tags else None

    from app.modules.image_analysis.infrastructure.image_repository import PlantImageRepository
    repo = PlantImageRepository(db)
    uc = UploadImageUseCase(image_repo=repo)
    image = await uc.execute(
        name=name or file.filename or "uploaded_image",
        file_url=file_url,
        user_id=current_user["id"],
        description=description,
        image_type=image_type,
        species=species,
        tags=file_tags,
        file_size_bytes=file.size,
        mime_type=file.content_type,
        project_id=project_id,
    )
    return _image_to_dict(image)


@router.get("", response_model=PaginatedImagesResponse)
async def list_images(
    skip: int = 0,
    limit: int = 20,
    image_type: str | None = None,
    species: str | None = None,
    project_id: str | None = None,
    source_module: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.image_repository import PlantImageRepository
    repo = PlantImageRepository(db)
    uc = ListImagesUseCase(image_repo=repo)
    result = await uc.execute(
        skip=skip, limit=limit, image_type=image_type,
        species=species, project_id=project_id,
        source_module=source_module, search=search,
        user_id=current_user["id"],
    )
    return PaginatedImagesResponse(**result)


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.image_repository import PlantImageRepository
    repo = PlantImageRepository(db)
    uc = GetImageUseCase(image_repo=repo)
    image = await uc.execute(image_id)
    return _image_to_dict(image)


@router.put("/{image_id}", response_model=ImageResponse)
async def update_image(
    image_id: str,
    request: UpdateImageRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.image_repository import PlantImageRepository
    repo = PlantImageRepository(db)
    uc = UpdateImageUseCase(image_repo=repo)
    image = await uc.execute(
        image_id=image_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        image_type=request.image_type,
        species=request.species,
        tissue_type=request.tissue_type,
        growth_stage=request.growth_stage,
        tags=request.tags,
    )
    return _image_to_dict(image)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.image_repository import PlantImageRepository
    repo = PlantImageRepository(db)
    uc = DeleteImageUseCase(image_repo=repo)
    await uc.execute(image_id=image_id, user_id=current_user["id"])


# ────────────────────────── Analysis Jobs ─────────────────────────────
@router.post("/{image_id}/analyze", response_model=AnalysisJobResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis_job(
    image_id: str,
    request: CreateAnalysisJobRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.image_repository import PlantImageRepository
    from app.modules.image_analysis.infrastructure.job_repository import ImageAnalysisJobRepository
    image_repo = PlantImageRepository(db)
    job_repo = ImageAnalysisJobRepository(db)
    uc = CreateAnalysisJobUseCase(job_repo=job_repo, image_repo=image_repo)
    job = await uc.execute(
        image_id=image_id,
        analysis_type=request.analysis_type,
        user_id=current_user["id"],
        parameters=request.parameters,
        project_id=request.project_id,
    )
    return _job_to_dict(job)


@router.get("/{image_id}/analyze", response_model=PaginatedAnalysisJobsResponse)
async def list_analysis_jobs(
    image_id: str,
    skip: int = 0,
    limit: int = 20,
    status_filter: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.job_repository import ImageAnalysisJobRepository
    repo = ImageAnalysisJobRepository(db)
    uc = ListAnalysisJobsUseCase(job_repo=repo)
    result = await uc.execute(
        skip=skip, limit=limit, image_id=image_id, status=status_filter,
    )
    return PaginatedAnalysisJobsResponse(**result)


@router.get("/analyze/{job_id}", response_model=AnalysisJobResponse)
async def get_analysis_job(
    job_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.job_repository import ImageAnalysisJobRepository
    repo = ImageAnalysisJobRepository(db)
    uc = GetAnalysisJobUseCase(job_repo=repo)
    job = await uc.execute(job_id)
    return _job_to_dict(job)


@router.get("/analyze/{job_id}/results", response_model=PaginatedAnalysisResultsResponse)
async def get_analysis_results(
    job_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.job_repository import ImageAnalysisJobRepository
    from app.modules.image_analysis.infrastructure.result_repository import AnalysisResultRepository
    job_repo = ImageAnalysisJobRepository(db)
    result_repo = AnalysisResultRepository(db)
    uc = GetAnalysisResultsUseCase(job_repo=job_repo, result_repo=result_repo)
    result = await uc.execute(job_id=job_id, skip=skip, limit=limit)
    return PaginatedAnalysisResultsResponse(**result)
