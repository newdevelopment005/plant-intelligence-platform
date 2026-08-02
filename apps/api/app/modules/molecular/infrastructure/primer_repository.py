from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.molecular.domain.interfaces import PrimerRepositoryInterface
from app.modules.molecular.domain.models import PrimerModel


class PrimerRepository(PrimerRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, primer: PrimerModel) -> PrimerModel:
        self.db.add(primer)
        await self.db.flush()
        await self.db.refresh(primer)
        return primer

    async def get_by_id(self, primer_id: str) -> PrimerModel | None:
        result = await self.db.execute(
            select(PrimerModel).where(PrimerModel.id == primer_id)
        )
        return result.scalar_one_or_none()

    async def list_by_experiment(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        primer_type: str | None = None,
        search: str | None = None,
    ) -> list[PrimerModel]:
        query = select(PrimerModel).where(PrimerModel.experiment_id == experiment_id)
        if primer_type:
            query = query.where(PrimerModel.primer_type == primer_type)
        if search:
            query = query.where(PrimerModel.name.ilike(f"%{search}%"))
        query = query.order_by(PrimerModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_experiment(
        self,
        experiment_id: str,
        primer_type: str | None = None,
        search: str | None = None,
    ) -> int:
        query = select(func.count(PrimerModel.id)).where(PrimerModel.experiment_id == experiment_id)
        if primer_type:
            query = query.where(PrimerModel.primer_type == primer_type)
        if search:
            query = query.where(PrimerModel.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, primer: PrimerModel) -> PrimerModel:
        await self.db.flush()
        await self.db.refresh(primer)
        return primer

    async def delete(self, primer_id: str) -> bool:
        primer = await self.get_by_id(primer_id)
        if not primer:
            return False
        await self.db.delete(primer)
        return True
