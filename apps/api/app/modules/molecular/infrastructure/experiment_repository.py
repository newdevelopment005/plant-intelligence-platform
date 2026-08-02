from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.molecular.domain.interfaces import MoleculeExperimentRepositoryInterface
from app.modules.molecular.domain.models import MoleculeExperimentModel


class MoleculeExperimentRepository(MoleculeExperimentRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, experiment: MoleculeExperimentModel) -> MoleculeExperimentModel:
        self.db.add(experiment)
        await self.db.flush()
        await self.db.refresh(experiment)
        return experiment

    async def get_by_id(self, experiment_id: str) -> MoleculeExperimentModel | None:
        result = await self.db.execute(
            select(MoleculeExperimentModel).where(MoleculeExperimentModel.id == experiment_id)
        )
        return result.scalar_one_or_none()

    async def list_experiments(
        self,
        skip: int = 0,
        limit: int = 20,
        experiment_type: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[MoleculeExperimentModel]:
        query = select(MoleculeExperimentModel)
        if experiment_type:
            query = query.where(MoleculeExperimentModel.experiment_type == experiment_type)
        if project_id:
            query = query.where(MoleculeExperimentModel.project_id == project_id)
        if status:
            query = query.where(MoleculeExperimentModel.status == status)
        if user_id:
            query = query.where(MoleculeExperimentModel.created_by == user_id)
        if search:
            query = query.where(MoleculeExperimentModel.name.ilike(f"%{search}%"))
        query = query.order_by(MoleculeExperimentModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_experiments(
        self,
        experiment_type: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count(MoleculeExperimentModel.id))
        if experiment_type:
            query = query.where(MoleculeExperimentModel.experiment_type == experiment_type)
        if project_id:
            query = query.where(MoleculeExperimentModel.project_id == project_id)
        if status:
            query = query.where(MoleculeExperimentModel.status == status)
        if user_id:
            query = query.where(MoleculeExperimentModel.created_by == user_id)
        if search:
            query = query.where(MoleculeExperimentModel.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, experiment: MoleculeExperimentModel) -> MoleculeExperimentModel:
        await self.db.flush()
        await self.db.refresh(experiment)
        return experiment

    async def delete(self, experiment_id: str) -> bool:
        experiment = await self.get_by_id(experiment_id)
        if not experiment:
            return False
        await self.db.delete(experiment)
        return True
