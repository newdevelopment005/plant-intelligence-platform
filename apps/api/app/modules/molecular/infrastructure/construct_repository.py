from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.molecular.domain.interfaces import ConstructRepositoryInterface
from app.modules.molecular.domain.models import ConstructModel


class ConstructRepository(ConstructRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, construct: ConstructModel) -> ConstructModel:
        self.db.add(construct)
        await self.db.flush()
        await self.db.refresh(construct)
        return construct

    async def get_by_id(self, construct_id: str) -> ConstructModel | None:
        result = await self.db.execute(
            select(ConstructModel).where(ConstructModel.id == construct_id)
        )
        return result.scalar_one_or_none()

    async def list_by_experiment(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        construct_type: str | None = None,
        search: str | None = None,
    ) -> list[ConstructModel]:
        query = select(ConstructModel).where(ConstructModel.experiment_id == experiment_id)
        if construct_type:
            query = query.where(ConstructModel.construct_type == construct_type)
        if search:
            query = query.where(ConstructModel.name.ilike(f"%{search}%"))
        query = query.order_by(ConstructModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_experiment(
        self,
        experiment_id: str,
        construct_type: str | None = None,
        search: str | None = None,
    ) -> int:
        query = select(func.count(ConstructModel.id)).where(ConstructModel.experiment_id == experiment_id)
        if construct_type:
            query = query.where(ConstructModel.construct_type == construct_type)
        if search:
            query = query.where(ConstructModel.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, construct: ConstructModel) -> ConstructModel:
        await self.db.flush()
        await self.db.refresh(construct)
        return construct

    async def delete(self, construct_id: str) -> bool:
        construct = await self.get_by_id(construct_id)
        if not construct:
            return False
        await self.db.delete(construct)
        return True
