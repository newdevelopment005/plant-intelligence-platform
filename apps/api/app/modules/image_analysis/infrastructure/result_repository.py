from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.image_analysis.domain.interfaces import AnalysisResultRepositoryInterface
from app.modules.image_analysis.domain.models import AnalysisResultModel


class AnalysisResultRepository(AnalysisResultRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, result: AnalysisResultModel) -> AnalysisResultModel:
        self.db.add(result)
        await self.db.flush()
        await self.db.refresh(result)
        return result

    async def get_by_id(self, result_id: str) -> AnalysisResultModel | None:
        result_row = await self.db.execute(
            select(AnalysisResultModel).where(AnalysisResultModel.id == result_id)
        )
        return result_row.scalar_one_or_none()

    async def list_by_job(
        self, job_id: str, skip: int = 0, limit: int = 100
    ) -> list[AnalysisResultModel]:
        query = (
            select(AnalysisResultModel)
            .where(AnalysisResultModel.job_id == job_id)
            .order_by(AnalysisResultModel.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_job(self, job_id: str) -> int:
        query = (
            select(func.count())
            .select_from(AnalysisResultModel)
            .where(AnalysisResultModel.job_id == job_id)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def delete(self, result_id: str) -> bool:
        result_row = await self.db.execute(
            select(AnalysisResultModel).where(AnalysisResultModel.id == result_id)
        )
        result = result_row.scalar_one_or_none()
        if not result:
            return False
        await self.db.delete(result)
        return True
