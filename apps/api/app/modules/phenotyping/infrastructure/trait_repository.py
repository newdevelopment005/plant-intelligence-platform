from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.phenotyping.domain.interfaces import TraitRepositoryInterface
from app.modules.phenotyping.domain.models import TraitModel


class TraitRepository(TraitRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, trait: TraitModel) -> TraitModel:
        self.db.add(trait)
        await self.db.flush()
        await self.db.refresh(trait)
        return trait

    async def get_by_id(self, trait_id: str) -> TraitModel | None:
        result = await self.db.execute(
            select(TraitModel).where(TraitModel.id == trait_id)
        )
        return result.scalar_one_or_none()

    async def list_by_experiment(
        self, experiment_id: str, skip: int = 0, limit: int = 100
    ) -> list[TraitModel]:
        query = (
            select(TraitModel)
            .where(TraitModel.experiment_id == experiment_id)
            .order_by(TraitModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_experiment(self, experiment_id: str) -> int:
        query = select(func.count(TraitModel.id)).where(
            TraitModel.experiment_id == experiment_id
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, trait: TraitModel) -> TraitModel:
        await self.db.flush()
        await self.db.refresh(trait)
        return trait

    async def delete(self, trait_id: str) -> bool:
        trait = await self.get_by_id(trait_id)
        if not trait:
            return False
        await self.db.delete(trait)
        return True
