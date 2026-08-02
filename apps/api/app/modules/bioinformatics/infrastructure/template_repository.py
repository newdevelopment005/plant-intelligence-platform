from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bioinformatics.domain.interfaces import PipelineTemplateRepositoryInterface
from app.modules.bioinformatics.domain.models import PipelineTemplateModel


class PipelineTemplateRepository(PipelineTemplateRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, template: PipelineTemplateModel) -> PipelineTemplateModel:
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def get_by_id(self, template_id: str) -> PipelineTemplateModel | None:
        result = await self.db.execute(
            select(PipelineTemplateModel).where(PipelineTemplateModel.id == template_id)
        )
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        skip: int = 0,
        limit: int = 20,
        analysis_type: str | None = None,
        search: str | None = None,
    ) -> list[PipelineTemplateModel]:
        query = select(PipelineTemplateModel)
        if analysis_type:
            query = query.where(PipelineTemplateModel.analysis_type == analysis_type)
        if search:
            query = query.where(PipelineTemplateModel.name.ilike(f"%{search}%"))
        query = query.order_by(PipelineTemplateModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_templates(
        self,
        analysis_type: str | None = None,
        search: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(PipelineTemplateModel)
        if analysis_type:
            query = query.where(PipelineTemplateModel.analysis_type == analysis_type)
        if search:
            query = query.where(PipelineTemplateModel.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, template: PipelineTemplateModel) -> PipelineTemplateModel:
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def delete(self, template_id: str) -> bool:
        template = await self.get_by_id(template_id)
        if not template:
            return False
        await self.db.delete(template)
        return True
