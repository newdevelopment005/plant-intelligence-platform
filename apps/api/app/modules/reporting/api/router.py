from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.reporting.api.schemas import (
    CreateReportRequest,
    CreateTemplateRequest,
    PaginatedReportsResponse,
    PaginatedTemplatesResponse,
    ReportResponse,
    TemplateResponse,
    UpdateReportRequest,
    UpdateTemplateRequest,
)
from app.modules.reporting.domain.use_cases import (
    CreateReportUseCase,
    CreateTemplateUseCase,
    DeleteReportUseCase,
    DeleteTemplateUseCase,
    GetReportUseCase,
    GetTemplateUseCase,
    ListReportsUseCase,
    ListTemplatesUseCase,
    UpdateReportUseCase,
    UpdateTemplateUseCase,
)

router = APIRouter()


# ────────────────────────── Reports ───────────────────────────────────
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    request: CreateReportRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.report_repository import ReportRepository
    repo = ReportRepository(db)
    uc = CreateReportUseCase(report_repo=repo)
    return await uc.execute(
        name=request.name,
        report_type=request.report_type,
        user_id=current_user["id"],
        description=request.description,
        format=request.format,
        data_source=request.data_source,
        parameters=request.parameters,
        tags=request.tags,
        project_id=request.project_id,
    )


@router.get("/", response_model=PaginatedReportsResponse)
async def list_reports(
    skip: int = 0,
    limit: int = 20,
    report_type: str | None = None,
    status_filter: str | None = None,
    project_id: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.report_repository import ReportRepository
    repo = ReportRepository(db)
    uc = ListReportsUseCase(report_repo=repo)
    result = await uc.execute(
        skip=skip, limit=limit, report_type=report_type,
        status=status_filter, project_id=project_id, search=search,
        user_id=current_user["id"],
    )
    return PaginatedReportsResponse(**result)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.report_repository import ReportRepository
    repo = ReportRepository(db)
    uc = GetReportUseCase(report_repo=repo)
    return await uc.execute(report_id)


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    request: UpdateReportRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.report_repository import ReportRepository
    repo = ReportRepository(db)
    uc = UpdateReportUseCase(report_repo=repo)
    return await uc.execute(
        report_id=report_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        tags=request.tags,
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.report_repository import ReportRepository
    repo = ReportRepository(db)
    uc = DeleteReportUseCase(report_repo=repo)
    await uc.execute(report_id=report_id, user_id=current_user["id"])


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.report_repository import ReportRepository
    repo = ReportRepository(db)
    uc = GetReportUseCase(report_repo=repo)
    report = await uc.execute(report_id)
    if not report.file_url:
        from app.core.exceptions import ValidationException
        raise ValidationException("Report is not ready for download")
    return {"download_url": report.file_url, "format": report.format, "name": report.name}


# ────────────────────────── Templates ─────────────────────────────────
@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: CreateTemplateRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.template_repository import ReportTemplateRepository
    repo = ReportTemplateRepository(db)
    uc = CreateTemplateUseCase(template_repo=repo)
    return await uc.execute(
        name=request.name,
        report_type=request.report_type,
        user_id=current_user["id"],
        description=request.description,
        default_format=request.default_format,
        data_source=request.data_source,
        layout=request.layout,
        default_parameters=request.default_parameters,
        tags=request.tags,
    )


@router.get("/templates", response_model=PaginatedTemplatesResponse)
async def list_templates(
    skip: int = 0,
    limit: int = 20,
    report_type: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.template_repository import ReportTemplateRepository
    repo = ReportTemplateRepository(db)
    uc = ListTemplatesUseCase(template_repo=repo)
    result = await uc.execute(skip=skip, limit=limit, report_type=report_type, search=search)
    return PaginatedTemplatesResponse(**result)


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.template_repository import ReportTemplateRepository
    repo = ReportTemplateRepository(db)
    uc = GetTemplateUseCase(template_repo=repo)
    return await uc.execute(template_id)


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    request: UpdateTemplateRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.template_repository import ReportTemplateRepository
    repo = ReportTemplateRepository(db)
    uc = UpdateTemplateUseCase(template_repo=repo)
    return await uc.execute(
        template_id=template_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        layout=request.layout,
        default_parameters=request.default_parameters,
        tags=request.tags,
    )


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.template_repository import ReportTemplateRepository
    repo = ReportTemplateRepository(db)
    uc = DeleteTemplateUseCase(template_repo=repo)
    await uc.execute(template_id=template_id, user_id=current_user["id"])
