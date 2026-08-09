from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.image_analysis.domain.interfaces import (
    AnalysisResultRepositoryInterface,
    ImageAnalysisJobRepositoryInterface,
    PlantImageRepositoryInterface,
)
from app.modules.image_analysis.domain.models import (
    ImageAnalysisJobModel,
    PlantImageModel,
)


def _to_uuid(value: str | None) -> UUID | None:
    if value is None:
        return None
    return UUID(value) if not isinstance(value, UUID) else value


class UploadImageUseCase:
    def __init__(self, image_repo: PlantImageRepositoryInterface):
        self.image_repo = image_repo

    async def execute(
        self,
        name: str,
        file_url: str,
        user_id: str,
        description: str | None = None,
        image_type: str = "general",
        source_module: str | None = None,
        source_id: str | None = None,
        species: str | None = None,
        tissue_type: str | None = None,
        growth_stage: str | None = None,
        magnification: str | None = None,
        file_size_bytes: int | None = None,
        mime_type: str | None = None,
        width: int | None = None,
        height: int | None = None,
        tags: list[str] | None = None,
        project_id: str | None = None,
        metadata_json: dict | None = None,
    ) -> PlantImageModel:
        if not name or not name.strip():
            raise ValidationException("Image name is required")
        if len(name.strip()) > 500:
            raise ValidationException("Image name must be less than 500 characters")
        if not file_url or not file_url.strip():
            raise ValidationException("File URL is required")

        valid_types = (
            "general", "leaf", "root", "seed", "fruit", "flower",
            "microscopy", "drone", "phenotype", "xray", "thermal",
        )
        if image_type not in valid_types:
            raise ValidationException(f"Invalid image type. Must be one of: {', '.join(valid_types)}")

        image = PlantImageModel(
            name=name.strip(),
            description=description.strip() if description else None,
            file_url=file_url.strip(),
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            width=width,
            height=height,
            image_type=image_type,
            source_module=source_module,
            source_id=source_id,
            species=species,
            tissue_type=tissue_type,
            growth_stage=growth_stage,
            magnification=magnification,
            tags=tags,
            metadata_json=metadata_json,
            project_id=_to_uuid(project_id),
            created_by=_to_uuid(user_id),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.image_repo.create(image)


class GetImageUseCase:
    def __init__(self, image_repo: PlantImageRepositoryInterface):
        self.image_repo = image_repo

    async def execute(self, image_id: str) -> PlantImageModel:
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            raise NotFoundException("Image", image_id)
        return image


class ListImagesUseCase:
    def __init__(self, image_repo: PlantImageRepositoryInterface):
        self.image_repo = image_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        image_type: str | None = None,
        species: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        images = await self.image_repo.list_images(
            skip=skip, limit=limit, image_type=image_type,
            species=species, project_id=project_id,
            source_module=source_module, search=search, user_id=user_id,
        )
        total = await self.image_repo.count_images(
            image_type=image_type, species=species, project_id=project_id,
            source_module=source_module, search=search, user_id=user_id,
        )
        return {
            "items": [
                {
                    "id": str(i.id),
                    "name": i.name,
                    "description": i.description,
                    "file_url": i.file_url,
                    "thumbnail_url": i.thumbnail_url,
                    "file_size_bytes": i.file_size_bytes,
                    "mime_type": i.mime_type,
                    "width": i.width,
                    "height": i.height,
                    "image_type": i.image_type,
                    "source_module": i.source_module,
                    "source_id": i.source_id,
                    "species": i.species,
                    "tissue_type": i.tissue_type,
                    "growth_stage": i.growth_stage,
                    "magnification": i.magnification,
                    "tags": i.tags,
                    "project_id": str(i.project_id) if i.project_id else None,
                    "created_by": str(i.created_by),
                    "created_at": i.created_at.isoformat(),
                    "updated_at": i.updated_at.isoformat(),
                }
                for i in images
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateImageUseCase:
    def __init__(self, image_repo: PlantImageRepositoryInterface):
        self.image_repo = image_repo

    async def execute(
        self,
        image_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        image_type: str | None = None,
        species: str | None = None,
        tissue_type: str | None = None,
        growth_stage: str | None = None,
        tags: list[str] | None = None,
    ) -> PlantImageModel:
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            raise NotFoundException("Image", image_id)

        if str(image.created_by) != user_id:
            raise ValidationException("Only the uploader can update this image")

        if name is not None:
            if not name.strip():
                raise ValidationException("Image name cannot be empty")
            image.name = name.strip()
        if description is not None:
            image.description = description.strip() if description else None
        if image_type is not None:
            image.image_type = image_type.strip()
        if species is not None:
            image.species = species.strip() if species else None
        if tissue_type is not None:
            image.tissue_type = tissue_type.strip() if tissue_type else None
        if growth_stage is not None:
            image.growth_stage = growth_stage.strip() if growth_stage else None
        if tags is not None:
            image.tags = tags

        image.updated_at = datetime.now(UTC)
        return await self.image_repo.update(image)


class DeleteImageUseCase:
    def __init__(self, image_repo: PlantImageRepositoryInterface):
        self.image_repo = image_repo

    async def execute(self, image_id: str, user_id: str) -> bool:
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            raise NotFoundException("Image", image_id)

        if str(image.created_by) != user_id:
            raise ValidationException("Only the uploader can delete this image")

        return await self.image_repo.delete(image_id)


class CreateAnalysisJobUseCase:
    def __init__(
        self,
        job_repo: ImageAnalysisJobRepositoryInterface,
        image_repo: PlantImageRepositoryInterface,
    ):
        self.job_repo = job_repo
        self.image_repo = image_repo

    async def execute(
        self,
        image_id: str,
        analysis_type: str,
        user_id: str,
        parameters: dict | None = None,
        project_id: str | None = None,
    ) -> ImageAnalysisJobModel:
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            raise NotFoundException("Image", image_id)

        valid_types = (
            "disease_detection", "pest_detection", "growth_stage",
            "phenotype_measurement", "leaf_area", "root_analysis",
            "seed_counting", "fruit_quality", "morphology",
            "stress_detection", "weed_detection", "flowering_time",
        )
        if analysis_type not in valid_types:
            raise ValidationException(f"Invalid analysis type. Must be one of: {', '.join(valid_types)}")

        job = ImageAnalysisJobModel(
            image_id=_to_uuid(image_id),
            analysis_type=analysis_type,
            status="pending",
            parameters=parameters,
            project_id=_to_uuid(project_id) if project_id else image.project_id,
            created_by=_to_uuid(user_id),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.job_repo.create(job)


class GetAnalysisJobUseCase:
    def __init__(self, job_repo: ImageAnalysisJobRepositoryInterface):
        self.job_repo = job_repo

    async def execute(self, job_id: str) -> ImageAnalysisJobModel:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException("Analysis job", job_id)
        return job


class ListAnalysisJobsUseCase:
    def __init__(self, job_repo: ImageAnalysisJobRepositoryInterface):
        self.job_repo = job_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        image_id: str | None = None,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
    ) -> dict:
        if status is not None:
            valid_statuses = ("pending", "running", "completed", "failed")
            if status not in valid_statuses:
                raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        jobs = await self.job_repo.list_jobs(
            skip=skip, limit=limit, image_id=image_id,
            analysis_type=analysis_type, status=status, project_id=project_id,
        )
        total = await self.job_repo.count_jobs(
            image_id=image_id, analysis_type=analysis_type,
            status=status, project_id=project_id,
        )
        return {
            "items": [
                {
                    "id": str(j.id),
                    "image_id": str(j.image_id),
                    "analysis_type": j.analysis_type,
                    "status": j.status,
                    "error_message": j.error_message,
                    "started_at": j.started_at.isoformat() if j.started_at else None,
                    "completed_at": j.completed_at.isoformat() if j.completed_at else None,
                    "runtime_seconds": j.runtime_seconds,
                    "model_version": j.model_version,
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


class GetAnalysisResultsUseCase:
    def __init__(
        self,
        job_repo: ImageAnalysisJobRepositoryInterface,
        result_repo: AnalysisResultRepositoryInterface,
    ):
        self.job_repo = job_repo
        self.result_repo = result_repo

    async def execute(
        self,
        job_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException("Analysis job", job_id)

        results = await self.result_repo.list_by_job(job_id, skip=skip, limit=limit)
        total = await self.result_repo.count_by_job(job_id)

        return {
            "items": [
                {
                    "id": str(r.id),
                    "job_id": str(r.job_id),
                    "result_type": r.result_type,
                    "label": r.label,
                    "confidence": r.confidence,
                    "bbox": r.bbox,
                    "measurements": r.measurements,
                    "annotations": r.annotations,
                    "created_at": r.created_at.isoformat(),
                }
                for r in results
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
