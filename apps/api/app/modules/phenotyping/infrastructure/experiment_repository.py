from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.phenotyping.domain.interfaces import ExperimentRepositoryInterface
from app.modules.phenotyping.domain.models import ExperimentModel


class ExperimentRepository(ExperimentRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, experiment: ExperimentModel) -> ExperimentModel:
        self.db.add(experiment)
        await self.db.flush()
        await self.db.refresh(experiment)
        return experiment

    async def get_by_id(self, experiment_id: str) -> ExperimentModel | None:
        result = await self.db.execute(
            select(ExperimentModel).where(ExperimentModel.id == experiment_id)
        )
        return result.scalar_one_or_none()

    async def list_experiments(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[ExperimentModel]:
        query = select(ExperimentModel)

        if project_id:
            query = query.where(ExperimentModel.project_id == project_id)
        if status:
            query = query.where(ExperimentModel.status == status)
        if user_id:
            query = query.where(ExperimentModel.created_by == user_id)
        if search:
            query = query.where(
                ExperimentModel.name.ilike(f"%{search}%")
            )

        query = query.order_by(ExperimentModel.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_experiments(
        self,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count(ExperimentModel.id))

        if project_id:
            query = query.where(ExperimentModel.project_id == project_id)
        if status:
            query = query.where(ExperimentModel.status == status)
        if user_id:
            query = query.where(ExperimentModel.created_by == user_id)
        if search:
            query = query.where(
                ExperimentModel.name.ilike(f"%{search}%")
            )

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, experiment: ExperimentModel) -> ExperimentModel:
        await self.db.flush()
        await self.db.refresh(experiment)
        return experiment

    async def delete(self, experiment_id: str) -> bool:
        experiment = await self.get_by_id(experiment_id)
        if not experiment:
            return False
        await self.db.delete(experiment)
        return True
