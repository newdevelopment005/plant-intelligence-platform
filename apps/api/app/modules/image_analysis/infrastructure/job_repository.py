from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.image_analysis.domain.interfaces import ImageAnalysisJobRepositoryInterface
from app.modules.image_analysis.domain.models import ImageAnalysisJobModel


class ImageAnalysisJobRepository(ImageAnalysisJobRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, job: ImageAnalysisJobModel) -> ImageAnalysisJobModel:
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def get_by_id(self, job_id: str) -> ImageAnalysisJobModel | None:
        result = await self.db.execute(
            select(ImageAnalysisJobModel).where(ImageAnalysisJobModel.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 20,
        image_id: str | None = None,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
    ) -> list[ImageAnalysisJobModel]:
        query = select(ImageAnalysisJobModel)
        if image_id:
            query = query.where(ImageAnalysisJobModel.image_id == image_id)
        if analysis_type:
            query = query.where(ImageAnalysisJobModel.analysis_type == analysis_type)
        if status:
            query = query.where(ImageAnalysisJobModel.status == status)
        if project_id:
            query = query.where(ImageAnalysisJobModel.project_id == project_id)
        query = query.order_by(ImageAnalysisJobModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_jobs(
        self,
        image_id: str | None = None,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(ImageAnalysisJobModel)
        if image_id:
            query = query.where(ImageAnalysisJobModel.image_id == image_id)
        if analysis_type:
            query = query.where(ImageAnalysisJobModel.analysis_type == analysis_type)
        if status:
            query = query.where(ImageAnalysisJobModel.status == status)
        if project_id:
            query = query.where(ImageAnalysisJobModel.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, job: ImageAnalysisJobModel) -> ImageAnalysisJobModel:
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def delete(self, job_id: str) -> bool:
        job = await self.get_by_id(job_id)
        if not job:
            return False
        await self.db.delete(job)
        return True
