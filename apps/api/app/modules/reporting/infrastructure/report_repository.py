from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reporting.domain.interfaces import ReportRepositoryInterface
from app.modules.reporting.domain.models import ReportModel


class ReportRepository(ReportRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, report: ReportModel) -> ReportModel:
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def get_by_id(self, report_id: str) -> ReportModel | None:
        result = await self.db.execute(
            select(ReportModel).where(ReportModel.id == report_id)
        )
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        skip: int = 0,
        limit: int = 20,
        report_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[ReportModel]:
        query = select(ReportModel)
        if report_type:
            query = query.where(ReportModel.report_type == report_type)
        if status:
            query = query.where(ReportModel.status == status)
        if project_id:
            query = query.where(ReportModel.project_id == project_id)
        if search:
            query = query.where(ReportModel.name.ilike(f"%{search}%"))
        if user_id:
            query = query.where(ReportModel.created_by == user_id)
        query = query.order_by(ReportModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_reports(
        self,
        report_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(ReportModel)
        if report_type:
            query = query.where(ReportModel.report_type == report_type)
        if status:
            query = query.where(ReportModel.status == status)
        if project_id:
            query = query.where(ReportModel.project_id == project_id)
        if search:
            query = query.where(ReportModel.name.ilike(f"%{search}%"))
        if user_id:
            query = query.where(ReportModel.created_by == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, report: ReportModel) -> ReportModel:
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def delete(self, report_id: str) -> bool:
        report = await self.get_by_id(report_id)
        if not report:
            return False
        await self.db.delete(report)
        return True
