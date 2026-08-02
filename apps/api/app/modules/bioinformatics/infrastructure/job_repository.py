from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bioinformatics.domain.interfaces import AnalysisJobRepositoryInterface
from app.modules.bioinformatics.domain.models import AnalysisJobModel


class AnalysisJobRepository(AnalysisJobRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, job: AnalysisJobModel) -> AnalysisJobModel:
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def get_by_id(self, job_id: str) -> AnalysisJobModel | None:
        result = await self.db.execute(
            select(AnalysisJobModel).where(AnalysisJobModel.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 20,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[AnalysisJobModel]:
        query = select(AnalysisJobModel)
        if analysis_type:
            query = query.where(AnalysisJobModel.analysis_type == analysis_type)
        if status:
            query = query.where(AnalysisJobModel.status == status)
        if project_id:
            query = query.where(AnalysisJobModel.project_id == project_id)
        if search:
            query = query.where(AnalysisJobModel.name.ilike(f"%{search}%"))
        if user_id:
            query = query.where(AnalysisJobModel.created_by == user_id)
        query = query.order_by(AnalysisJobModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_jobs(
        self,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(AnalysisJobModel)
        if analysis_type:
            query = query.where(AnalysisJobModel.analysis_type == analysis_type)
        if status:
            query = query.where(AnalysisJobModel.status == status)
        if project_id:
            query = query.where(AnalysisJobModel.project_id == project_id)
        if search:
            query = query.where(AnalysisJobModel.name.ilike(f"%{search}%"))
        if user_id:
            query = query.where(AnalysisJobModel.created_by == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, job: AnalysisJobModel) -> AnalysisJobModel:
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def delete(self, job_id: str) -> bool:
        job = await self.get_by_id(job_id)
        if not job:
            return False
        await self.db.delete(job)
        return True
