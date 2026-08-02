from fastapi import APIRouter, Depends, status
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

router = APIRouter()


# ────────────────────────── Plant Images ──────────────────────────────
@router.post("/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    request: UploadImageRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.image_analysis.infrastructure.image_repository import PlantImageRepository
    repo = PlantImageRepository(db)
    uc = UploadImageUseCase(image_repo=repo)
    return await uc.execute(
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


@router.get("/", response_model=PaginatedImagesResponse)
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
    return await uc.execute(image_id)


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
    return await uc.execute(
        image_id=image_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        species=request.species,
        tissue_type=request.tissue_type,
        growth_stage=request.growth_stage,
        tags=request.tags,
    )


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
    return await uc.execute(
        image_id=image_id,
        analysis_type=request.analysis_type,
        user_id=current_user["id"],
        parameters=request.parameters,
        project_id=request.project_id,
    )


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
    return await uc.execute(job_id)


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
