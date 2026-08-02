from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reporting.domain.interfaces import ReportTemplateRepositoryInterface
from app.modules.reporting.domain.models import ReportTemplateModel


class ReportTemplateRepository(ReportTemplateRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, template: ReportTemplateModel) -> ReportTemplateModel:
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def get_by_id(self, template_id: str) -> ReportTemplateModel | None:
        result = await self.db.execute(
            select(ReportTemplateModel).where(ReportTemplateModel.id == template_id)
        )
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        skip: int = 0,
        limit: int = 20,
        report_type: str | None = None,
        search: str | None = None,
    ) -> list[ReportTemplateModel]:
        query = select(ReportTemplateModel)
        if report_type:
            query = query.where(ReportTemplateModel.report_type == report_type)
        if search:
            query = query.where(ReportTemplateModel.name.ilike(f"%{search}%"))
        query = query.order_by(ReportTemplateModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_templates(
        self,
        report_type: str | None = None,
        search: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(ReportTemplateModel)
        if report_type:
            query = query.where(ReportTemplateModel.report_type == report_type)
        if search:
            query = query.where(ReportTemplateModel.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, template: ReportTemplateModel) -> ReportTemplateModel:
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def delete(self, template_id: str) -> bool:
        template = await self.get_by_id(template_id)
        if not template:
            return False
        await self.db.delete(template)
        return True
