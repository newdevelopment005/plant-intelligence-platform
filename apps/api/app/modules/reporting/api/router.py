from fastapi import APIRouter, Depends, File, UploadFile, status
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

router = APIRouter(redirect_slashes=False)


def _template_to_dict(t) -> dict:
    return {
        "id": str(t.id),
        "name": t.name,
        "description": t.description,
        "report_type": t.report_type,
        "default_format": t.default_format,
        "data_source": t.data_source,
        "layout": t.layout,
        "default_parameters": t.default_parameters,
        "is_active": bool(t.is_active),
        "tags": t.tags,
        "created_by": str(t.created_by),
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


def _report_to_dict(report) -> dict:
    return {
        "id": str(report.id),
        "name": report.name,
        "description": report.description,
        "report_type": report.report_type,
        "status": report.status,
        "format": report.format,
        "data_source": report.data_source,
        "file_url": report.file_url,
        "file_size_bytes": report.file_size_bytes,
        "error_message": report.error_message,
        "tags": report.tags,
        "project_id": str(report.project_id) if report.project_id else None,
        "created_by": str(report.created_by),
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "updated_at": report.updated_at.isoformat() if report.updated_at else None,
    }


# ────────────────────────── Reports ───────────────────────────────────
@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    request: CreateReportRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.report_repository import ReportRepository
    repo = ReportRepository(db)
    uc = CreateReportUseCase(report_repo=repo)
    report = await uc.execute(
        name=request.name,
        report_type=request.report_type,
        user_id=current_user["id"],
        description=request.description,
        format=request.format,
        data_source=request.data_source,
        parameters=request.parameters,
        tags=request.tags,
        project_id=request.project_id,
        file_url=request.file_url,
        file_size_bytes=request.file_size_bytes,
    )
    return _report_to_dict(report)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_report_file(
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user),
):
    """Attach a ready-made report file. Returns the stored URL and metadata."""
    from app.shared.file_storage import save_uploaded_file

    if not file.filename:
        from app.core.exceptions import ValidationException
        raise ValidationException("File is required")

    url = await save_uploaded_file(file, "reports")
    return {
        "file_url": url,
        "format": _format_from_filename(file.filename),
        "filename": file.filename,
    }


def _format_from_filename(filename: str | None) -> str:
    ext = (filename or "").rsplit(".", 1)[-1].lower()
    mapping = {"pdf": "pdf", "csv": "csv", "json": "json", "xlsx": "xlsx", "xls": "xlsx", "html": "html", "htm": "html", "docx": "docx"}
    return mapping.get(ext, "pdf")


@router.get("", response_model=PaginatedReportsResponse)
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
    return result


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
    template = await uc.execute(
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
    return _template_to_dict(template)


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
    return result


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.template_repository import ReportTemplateRepository
    repo = ReportTemplateRepository(db)
    uc = GetTemplateUseCase(template_repo=repo)
    template = await uc.execute(template_id)
    return _template_to_dict(template)


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
    template = await uc.execute(
        template_id=template_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        layout=request.layout,
        default_parameters=request.default_parameters,
        tags=request.tags,
    )
    return _template_to_dict(template)


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


# ────────────────────────── Reports ───────────────────────────────────
@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.reporting.infrastructure.report_repository import ReportRepository
    repo = ReportRepository(db)
    uc = GetReportUseCase(report_repo=repo)
    report = await uc.execute(report_id)
    return _report_to_dict(report)


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
    report = await uc.execute(
        report_id=report_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        tags=request.tags,
    )
    return _report_to_dict(report)


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
