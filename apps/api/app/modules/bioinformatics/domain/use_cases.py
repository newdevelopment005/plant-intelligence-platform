from datetime import UTC, datetime

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.bioinformatics.domain.interfaces import (
    AnalysisJobRepositoryInterface,
    PipelineTemplateRepositoryInterface,
)
from app.modules.bioinformatics.domain.models import AnalysisJobModel, PipelineTemplateModel


class CreateAnalysisJobUseCase:
    def __init__(self, job_repo: AnalysisJobRepositoryInterface):
        self.job_repo = job_repo

    async def execute(
        self,
        name: str,
        analysis_type: str,
        user_id: str,
        description: str | None = None,
        priority: str = "normal",
        input_data: dict | None = None,
        parameters: dict | None = None,
        tags: list[str] | None = None,
        project_id: str | None = None,
    ) -> AnalysisJobModel:
        if not name or not name.strip():
            raise ValidationException("Job name is required")
        if len(name.strip()) > 500:
            raise ValidationException("Job name must be less than 500 characters")

        valid_types = (
            "alignment", "blast", "variant_calling", "rnaseq",
            "phylogenetics", "pathway_analysis", "gene_prediction",
            "primer_design", "codon_usage", "motif_search",
            "population_genetics", "gwas", "qtl_mapping",
        )
        if analysis_type not in valid_types:
            raise ValidationException(f"Invalid analysis type. Must be one of: {', '.join(valid_types)}")

        valid_priorities = ("low", "normal", "high", "urgent")
        if priority not in valid_priorities:
            raise ValidationException(f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")

        if not input_data:
            raise ValidationException("Input data is required")

        job = AnalysisJobModel(
            name=name.strip(),
            description=description.strip() if description else None,
            analysis_type=analysis_type,
            status="pending",
            priority=priority,
            input_data=input_data,
            parameters=parameters,
            tags=tags,
            project_id=project_id,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.job_repo.create(job)


class GetAnalysisJobUseCase:
    def __init__(self, job_repo: AnalysisJobRepositoryInterface):
        self.job_repo = job_repo

    async def execute(self, job_id: str) -> AnalysisJobModel:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException("Analysis job", job_id)
        return job


class ListAnalysisJobsUseCase:
    def __init__(self, job_repo: AnalysisJobRepositoryInterface):
        self.job_repo = job_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        if status is not None:
            valid_statuses = ("pending", "running", "completed", "failed", "cancelled")
            if status not in valid_statuses:
                raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        jobs = await self.job_repo.list_jobs(
            skip=skip, limit=limit, analysis_type=analysis_type,
            status=status, project_id=project_id, search=search, user_id=user_id,
        )
        total = await self.job_repo.count_jobs(
            analysis_type=analysis_type, status=status, project_id=project_id,
            search=search, user_id=user_id,
        )
        return {
            "items": [
                {
                    "id": str(j.id),
                    "name": j.name,
                    "description": j.description,
                    "analysis_type": j.analysis_type,
                    "status": j.status,
                    "priority": j.priority,
                    "progress_percent": j.progress_percent,
                    "error_message": j.error_message,
                    "started_at": j.started_at.isoformat() if j.started_at else None,
                    "completed_at": j.completed_at.isoformat() if j.completed_at else None,
                    "runtime_seconds": j.runtime_seconds,
                    "tags": j.tags,
                    "project_id": str(j.project_id) if j.project_id else None,
                    "created_by": str(j.created_by),
                    "created_at": j.created_at.isoformat(),
                    "updated_at": j.updated_at.isoformat(),
                }
                for j in jobs
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateAnalysisJobUseCase:
    def __init__(self, job_repo: AnalysisJobRepositoryInterface):
        self.job_repo = job_repo

    async def execute(
        self,
        job_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        tags: list[str] | None = None,
    ) -> AnalysisJobModel:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException("Analysis job", job_id)

        if str(job.created_by) != user_id:
            raise ValidationException("Only the creator can update this job")

        if job.status not in ("pending", "failed"):
            raise ValidationException("Only pending or failed jobs can be edited")

        if name is not None:
            if not name.strip():
                raise ValidationException("Job name cannot be empty")
            job.name = name.strip()
        if description is not None:
            job.description = description.strip() if description else None
        if priority is not None:
            valid_priorities = ("low", "normal", "high", "urgent")
            if priority not in valid_priorities:
                raise ValidationException("Invalid priority")
            job.priority = priority
        if tags is not None:
            job.tags = tags

        job.updated_at = datetime.now(UTC)
        return await self.job_repo.update(job)


class CancelAnalysisJobUseCase:
    def __init__(self, job_repo: AnalysisJobRepositoryInterface):
        self.job_repo = job_repo

    async def execute(self, job_id: str, user_id: str) -> AnalysisJobModel:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException("Analysis job", job_id)

        if str(job.created_by) != user_id:
            raise ValidationException("Only the creator can cancel this job")

        if job.status not in ("pending", "running"):
            raise ValidationException("Only pending or running jobs can be cancelled")

        job.status = "cancelled"
        job.updated_at = datetime.now(UTC)
        return await self.job_repo.update(job)


class DeleteAnalysisJobUseCase:
    def __init__(self, job_repo: AnalysisJobRepositoryInterface):
        self.job_repo = job_repo

    async def execute(self, job_id: str, user_id: str) -> bool:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException("Analysis job", job_id)

        if str(job.created_by) != user_id:
            raise ValidationException("Only the creator can delete this job")

        if job.status == "running":
            raise ValidationException("Cannot delete a running job")

        return await self.job_repo.delete(job_id)


class CreatePipelineTemplateUseCase:
    def __init__(self, template_repo: PipelineTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(
        self,
        name: str,
        analysis_type: str,
        user_id: str,
        description: str | None = None,
        steps: list[dict] | None = None,
        default_parameters: dict | None = None,
        required_inputs: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> PipelineTemplateModel:
        if not name or not name.strip():
            raise ValidationException("Template name is required")
        if len(name.strip()) > 255:
            raise ValidationException("Template name must be less than 255 characters")

        valid_types = (
            "alignment", "blast", "variant_calling", "rnaseq",
            "phylogenetics", "pathway_analysis", "gene_prediction",
            "primer_design", "codon_usage", "motif_search",
            "population_genetics", "gwas", "qtl_mapping",
        )
        if analysis_type not in valid_types:
            raise ValidationException(f"Invalid analysis type. Must be one of: {', '.join(valid_types)}")

        template = PipelineTemplateModel(
            name=name.strip(),
            description=description.strip() if description else None,
            analysis_type=analysis_type,
            steps=steps,
            default_parameters=default_parameters,
            required_inputs=required_inputs,
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.template_repo.create(template)


class GetPipelineTemplateUseCase:
    def __init__(self, template_repo: PipelineTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(self, template_id: str) -> PipelineTemplateModel:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise NotFoundException("Pipeline template", template_id)
        return template


class ListPipelineTemplatesUseCase:
    def __init__(self, template_repo: PipelineTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        analysis_type: str | None = None,
        search: str | None = None,
    ) -> dict:
        templates = await self.template_repo.list_templates(
            skip=skip, limit=limit, analysis_type=analysis_type, search=search,
        )
        total = await self.template_repo.count_templates(
            analysis_type=analysis_type, search=search,
        )
        return {
            "items": [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "description": t.description,
                    "analysis_type": t.analysis_type,
                    "steps": t.steps,
                    "default_parameters": t.default_parameters,
                    "required_inputs": t.required_inputs,
                    "version": t.version,
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


class UpdatePipelineTemplateUseCase:
    def __init__(self, template_repo: PipelineTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(
        self,
        template_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        steps: list[dict] | None = None,
        default_parameters: dict | None = None,
        required_inputs: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> PipelineTemplateModel:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise NotFoundException("Pipeline template", template_id)

        if str(template.created_by) != user_id:
            raise ValidationException("Only the creator can update this template")

        if name is not None:
            if not name.strip():
                raise ValidationException("Template name cannot be empty")
            template.name = name.strip()
        if description is not None:
            template.description = description.strip() if description else None
        if steps is not None:
            template.steps = steps
        if default_parameters is not None:
            template.default_parameters = default_parameters
        if required_inputs is not None:
            template.required_inputs = required_inputs
        if tags is not None:
            template.tags = tags

        template.updated_at = datetime.now(UTC)
        return await self.template_repo.update(template)


class DeletePipelineTemplateUseCase:
    def __init__(self, template_repo: PipelineTemplateRepositoryInterface):
        self.template_repo = template_repo

    async def execute(self, template_id: str, user_id: str) -> bool:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise NotFoundException("Pipeline template", template_id)

        if str(template.created_by) != user_id:
            raise ValidationException("Only the creator can delete this template")

        return await self.template_repo.delete(template_id)
