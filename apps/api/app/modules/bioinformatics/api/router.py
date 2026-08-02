from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.bioinformatics.api.schemas import (
    AnalysisJobDetailResponse,
    CreateAnalysisJobRequest,
    CreatePipelineTemplateRequest,
    PaginatedAnalysisJobsResponse,
    PaginatedPipelineTemplatesResponse,
    PipelineTemplateResponse,
    UpdateAnalysisJobRequest,
    UpdatePipelineTemplateRequest,
)
from app.modules.bioinformatics.domain.use_cases import (
    CancelAnalysisJobUseCase,
    CreateAnalysisJobUseCase,
    CreatePipelineTemplateUseCase,
    DeleteAnalysisJobUseCase,
    DeletePipelineTemplateUseCase,
    GetAnalysisJobUseCase,
    GetPipelineTemplateUseCase,
    ListAnalysisJobsUseCase,
    ListPipelineTemplatesUseCase,
    UpdateAnalysisJobUseCase,
    UpdatePipelineTemplateUseCase,
)

router = APIRouter()


# ────────────────────────── Analysis Jobs ─────────────────────────────
@router.post("/jobs", response_model=AnalysisJobDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis_job(
    request: CreateAnalysisJobRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.job_repository import AnalysisJobRepository
    repo = AnalysisJobRepository(db)
    uc = CreateAnalysisJobUseCase(job_repo=repo)
    return await uc.execute(
        name=request.name,
        analysis_type=request.analysis_type,
        user_id=current_user["id"],
        description=request.description,
        priority=request.priority,
        input_data=request.input_data,
        parameters=request.parameters,
        tags=request.tags,
        project_id=request.project_id,
    )


@router.get("/jobs", response_model=PaginatedAnalysisJobsResponse)
async def list_analysis_jobs(
    skip: int = 0,
    limit: int = 20,
    analysis_type: str | None = None,
    status_filter: str | None = None,
    project_id: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.job_repository import AnalysisJobRepository
    repo = AnalysisJobRepository(db)
    uc = ListAnalysisJobsUseCase(job_repo=repo)
    result = await uc.execute(
        skip=skip, limit=limit, analysis_type=analysis_type,
        status=status_filter, project_id=project_id, search=search,
        user_id=current_user["id"],
    )
    return PaginatedAnalysisJobsResponse(**result)


@router.get("/jobs/{job_id}", response_model=AnalysisJobDetailResponse)
async def get_analysis_job(
    job_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.job_repository import AnalysisJobRepository
    repo = AnalysisJobRepository(db)
    uc = GetAnalysisJobUseCase(job_repo=repo)
    return await uc.execute(job_id)


@router.put("/jobs/{job_id}", response_model=AnalysisJobDetailResponse)
async def update_analysis_job(
    job_id: str,
    request: UpdateAnalysisJobRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.job_repository import AnalysisJobRepository
    repo = AnalysisJobRepository(db)
    uc = UpdateAnalysisJobUseCase(job_repo=repo)
    return await uc.execute(
        job_id=job_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        priority=request.priority,
        tags=request.tags,
    )


@router.post("/jobs/{job_id}/cancel", response_model=AnalysisJobDetailResponse)
async def cancel_analysis_job(
    job_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.job_repository import AnalysisJobRepository
    repo = AnalysisJobRepository(db)
    uc = CancelAnalysisJobUseCase(job_repo=repo)
    return await uc.execute(job_id=job_id, user_id=current_user["id"])


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis_job(
    job_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.job_repository import AnalysisJobRepository
    repo = AnalysisJobRepository(db)
    uc = DeleteAnalysisJobUseCase(job_repo=repo)
    await uc.execute(job_id=job_id, user_id=current_user["id"])


# ────────────────────────── Pipeline Templates ────────────────────────
@router.post("/templates", response_model=PipelineTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline_template(
    request: CreatePipelineTemplateRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.template_repository import (
        PipelineTemplateRepository,
    )
    repo = PipelineTemplateRepository(db)
    uc = CreatePipelineTemplateUseCase(template_repo=repo)
    return await uc.execute(
        name=request.name,
        analysis_type=request.analysis_type,
        user_id=current_user["id"],
        description=request.description,
        steps=request.steps,
        default_parameters=request.default_parameters,
        required_inputs=request.required_inputs,
        tags=request.tags,
    )


@router.get("/templates", response_model=PaginatedPipelineTemplatesResponse)
async def list_pipeline_templates(
    skip: int = 0,
    limit: int = 20,
    analysis_type: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
):
    from app.modules.bioinformatics.infrastructure.template_repository import (
        PipelineTemplateRepository,
    )
    # Template listing doesn't need DB in current impl, but follows pattern
    repo = PipelineTemplateRepository(None)
    uc = ListPipelineTemplatesUseCase(template_repo=repo)
    result = await uc.execute(skip=skip, limit=limit, analysis_type=analysis_type, search=search)
    return PaginatedPipelineTemplatesResponse(**result)


@router.get("/templates/{template_id}", response_model=PipelineTemplateResponse)
async def get_pipeline_template(
    template_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.template_repository import (
        PipelineTemplateRepository,
    )
    repo = PipelineTemplateRepository(db)
    uc = GetPipelineTemplateUseCase(template_repo=repo)
    return await uc.execute(template_id)


@router.put("/templates/{template_id}", response_model=PipelineTemplateResponse)
async def update_pipeline_template(
    template_id: str,
    request: UpdatePipelineTemplateRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.template_repository import (
        PipelineTemplateRepository,
    )
    repo = PipelineTemplateRepository(db)
    uc = UpdatePipelineTemplateUseCase(template_repo=repo)
    return await uc.execute(
        template_id=template_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        steps=request.steps,
        default_parameters=request.default_parameters,
        required_inputs=request.required_inputs,
        tags=request.tags,
    )


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline_template(
    template_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.bioinformatics.infrastructure.template_repository import (
        PipelineTemplateRepository,
    )
    repo = PipelineTemplateRepository(db)
    uc = DeletePipelineTemplateUseCase(template_repo=repo)
    await uc.execute(template_id=template_id, user_id=current_user["id"])
