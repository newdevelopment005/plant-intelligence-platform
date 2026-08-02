from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.genomics.domain.interfaces import SequenceRepositoryInterface
from app.modules.genomics.domain.models import SequenceModel


class SequenceRepository(SequenceRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, sequence: SequenceModel) -> SequenceModel:
        self.db.add(sequence)
        await self.db.flush()
        await self.db.refresh(sequence)
        return sequence

    async def get_by_id(self, sequence_id: str) -> SequenceModel | None:
        result = await self.db.execute(
            select(SequenceModel).where(SequenceModel.id == sequence_id)
        )
        return result.scalar_one_or_none()

    async def list_sequences(
        self,
        skip: int = 0,
        limit: int = 20,
        sequence_type: str | None = None,
        species_id: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[SequenceModel]:
        query = select(SequenceModel)

        if sequence_type:
            query = query.where(SequenceModel.sequence_type == sequence_type)
        if species_id:
            query = query.where(SequenceModel.species_id == species_id)
        if project_id:
            query = query.where(SequenceModel.project_id == project_id)
        if user_id:
            query = query.where(SequenceModel.created_by == user_id)
        if search:
            query = query.where(SequenceModel.name.ilike(f"%{search}%"))

        query = query.order_by(SequenceModel.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_sequences(
        self,
        sequence_type: str | None = None,
        species_id: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count(SequenceModel.id))

        if sequence_type:
            query = query.where(SequenceModel.sequence_type == sequence_type)
        if species_id:
            query = query.where(SequenceModel.species_id == species_id)
        if project_id:
            query = query.where(SequenceModel.project_id == project_id)
        if user_id:
            query = query.where(SequenceModel.created_by == user_id)
        if search:
            query = query.where(SequenceModel.name.ilike(f"%{search}%"))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, sequence: SequenceModel) -> SequenceModel:
        await self.db.flush()
        await self.db.refresh(sequence)
        return sequence

    async def delete(self, sequence_id: str) -> bool:
        sequence = await self.get_by_id(sequence_id)
        if not sequence:
            return False
        await self.db.delete(sequence)
        return True
