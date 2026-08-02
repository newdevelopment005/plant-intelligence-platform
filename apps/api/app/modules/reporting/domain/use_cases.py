from datetime import UTC, datetime

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.reporting.domain.interfaces import (
    ReportRepositoryInterface,
    ReportTemplateRepositoryInterface,
)
from app.modules.reporting.domain.models import ReportModel, ReportTemplateModel


class CreateReportUseCase:
    def __init__(self, report_repo: ReportRepositoryInterface):
        self.report_repo = report_repo

    async def execute(
        self,
        name: str,
        report_type: str,
        user_id: str,
        description: str | None = None,
        format: str = "pdf",
        data_source: str | None = None,
        parameters: dict | None = None,
        tags: list[str] | None = None,
        project_id: str | None = None,
    ) -> ReportModel:
        if not name or not name.strip():
            raise ValidationException("Report name is required")
        if len(name.strip()) > 500:
            raise ValidationException("Report name must be less than 500 characters")

        valid_types = (
            "phenotyping", "genotyping", "germplasm", "experiment",
            "project_summary", "custom", "statistical", "comparative",
            "temporal", "geospatial",
        )
        if report_type not in valid_types:
            raise ValidationException(f"Invalid report type. Must be one of: {', '.join(valid_types)}")

        valid_formats = ("pdf", "csv", "json", "xlsx", "html", "docx")
        if format not in valid_formats:
            raise ValidationException(f"Invalid format. Must be one of: {', '.join(valid_formats)}")

        report = ReportModel(
            name=name.strip(),
            description=description.strip() if description else None,
            report_type=report_type,
            status="pending",
            format=format,
            data_source=data_source,
            parameters=parameters,
            tags=tags,
            project_id=project_id,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.report_repo.create(report)


class GetReportUseCase:
    def __init__(self, report_repo: ReportRepositoryInterface):
        self.report_repo = report_repo

    async def execute(self, report_id: str) -> ReportModel:
        report = await self.report_repo.get_by_id(report_id)
        if not report:
            raise NotFoundException("Report", report_id)
        return report


class ListReportsUseCase:
    def __init__(self, report_repo: ReportRepositoryInterface):
        self.report_repo = report_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        report_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        if status is not None:
            valid_statuses = ("pending", "generating", "completed", "failed")
            if status not in valid_statuses:
                raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        reports = await self.report_repo.list_reports(
            skip=skip, limit=limit, report_type=report_type,
            status=status, project_id=project_id, search=search, user_id=user_id,
        )
        total = await self.report_repo.count_reports(
            report_type=report_type, status=status, project_id=project_id,
            search=search, user_id=user_id,
        )
        return {
            "items": [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "description": r.description,
                    "report_type": r.report_type,
                    "status": r.status,
                    "format": r.format,
                    "data_source": r.data_source,
                    "file_url": r.file_url,
                    "file_size_bytes": r.file_size_bytes,
                    "error_message": r.error_message,
                    "tags": r.tags,
                    "project_id": str(r.project_id) if r.project_id else None,
                    "created_by": str(r.created_by),
                    "created_at": r.created_at.isoformat(),
                    "updated_at": r.updated_at.isoformat(),
                }
                for r in reports
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateReportUseCase:
    def __init__(self, report_repo: ReportRepositoryInterface):
        self.report_repo = report_repo

    async def execute(
        self,
        report_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> ReportModel:
        report = await self.report_repo.get_by_id(report_id)
        if not report:
            raise NotFoundException("Report", report_id)

        if str(report.created_by) != user_id:
            raise ValidationException("Only the creator can update this report")

        if report.status not in ("pending", "failed"):
            raise ValidationException("Only pending or failed reports can be edited")

        if name is not None:
            if not name.strip():
                raise ValidationException("Report name cannot be empty")
            report.name = name.strip()
        if description is not None:
            report.description = description.strip() if description else None
        if tags is not None:
            report.tags = tags

        report.updated_at = datetime.now(UTC)
        return await self.report_repo.update(report)


class DeleteReportUseCase:
    def __init__(self, report_repo: ReportRepositoryInterface):
        self.report_repo = report_repo

    async def execute(self, report_id: str, user_id: str) -> bool:
        report = await self.report_repo.get_by_id(report_id)
        if not report:
            raise NotFoundException("Report", report_id)

        if str(report.created_by) != user_id:
            raise ValidationException("Only the creator can delete this report")

        if report.status == "generating":
            raise ValidationException("Cannot delete a report that is being generated")

        return await self.report_repo.delete(report_id)


class CreateTemplateUseCase:
    def __init__(self, template_repo: ReportTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(
        self,
        name: str,
        report_type: str,
        user_id: str,
        description: str | None = None,
        default_format: str = "pdf",
        data_source: str | None = None,
        layout: dict | None = None,
        default_parameters: dict | None = None,
        tags: list[str] | None = None,
    ) -> ReportTemplateModel:
        if not name or not name.strip():
            raise ValidationException("Template name is required")
        if len(name.strip()) > 255:
            raise ValidationException("Template name must be less than 255 characters")

        valid_types = (
            "phenotyping", "genotyping", "germplasm", "experiment",
            "project_summary", "custom", "statistical", "comparative",
            "temporal", "geospatial",
        )
        if report_type not in valid_types:
            raise ValidationException(f"Invalid report type. Must be one of: {', '.join(valid_types)}")

        template = ReportTemplateModel(
            name=name.strip(),
            description=description.strip() if description else None,
            report_type=report_type,
            default_format=default_format,
            data_source=data_source,
            layout=layout,
            default_parameters=default_parameters,
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.template_repo.create(template)


class GetTemplateUseCase:
    def __init__(self, template_repo: ReportTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(self, template_id: str) -> ReportTemplateModel:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise NotFoundException("Report template", template_id)
        return template


class ListTemplatesUseCase:
    def __init__(self, template_repo: ReportTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        report_type: str | None = None,
        search: str | None = None,
    ) -> dict:
        templates = await self.template_repo.list_templates(
            skip=skip, limit=limit, report_type=report_type, search=search,
        )
        total = await self.template_repo.count_templates(
            report_type=report_type, search=search,
        )
        return {
            "items": [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "description": t.description,
                    "report_type": t.report_type,
                    "default_format": t.default_format,
                    "data_source": t.data_source,
                    "layout": t.layout,
                    "default_parameters": t.default_parameters,
                    "is_active": t.is_active,
                    "tags": t.tags,
                    "created_by": str(t.created_by),
                    "created_at": t.created_at.isoformat(),
                    "updated_at": t.updated_at.isoformat(),
                }
                for t in templates
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateTemplateUseCase:
    def __init__(self, template_repo: ReportTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(
        self,
        template_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        layout: dict | None = None,
        default_parameters: dict | None = None,
        tags: list[str] | None = None,
    ) -> ReportTemplateModel:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise NotFoundException("Report template", template_id)

        if str(template.created_by) != user_id:
            raise ValidationException("Only the creator can update this template")

        if name is not None:
            if not name.strip():
                raise ValidationException("Template name cannot be empty")
            template.name = name.strip()
        if description is not None:
            template.description = description.strip() if description else None
        if layout is not None:
            template.layout = layout
        if default_parameters is not None:
            template.default_parameters = default_parameters
        if tags is not None:
            template.tags = tags

        template.updated_at = datetime.now(UTC)
        return await self.template_repo.update(template)


class DeleteTemplateUseCase:
    def __init__(self, template_repo: ReportTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(self, template_id: str, user_id: str) -> bool:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise NotFoundException("Report template", template_id)

        if str(template.created_by) != user_id:
            raise ValidationException("Only the creator can delete this template")

        return await self.template_repo.delete(template_id)
