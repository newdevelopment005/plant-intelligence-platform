from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.literature.domain.interfaces import NoteRepositoryInterface
from app.modules.literature.domain.models import NoteModel


class NoteRepository(NoteRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, note: NoteModel) -> NoteModel:
        self.db.add(note)
        await self.db.flush()
        await self.db.refresh(note)
        return note

    async def get_by_id(self, note_id: str) -> NoteModel | None:
        result = await self.db.execute(
            select(NoteModel).where(NoteModel.id == note_id)
        )
        return result.scalar_one_or_none()

    async def list_by_paper(
        self, paper_id: str, skip: int = 0, limit: int = 100
    ) -> list[NoteModel]:
        query = (
            select(NoteModel)
            .where(NoteModel.paper_id == paper_id)
            .order_by(NoteModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_paper(self, paper_id: str) -> int:
        result = await self.db.execute(
            select(func.count(NoteModel.id)).where(NoteModel.paper_id == paper_id)
        )
        return result.scalar_one()

    async def update(self, note: NoteModel) -> NoteModel:
        await self.db.flush()
        await self.db.refresh(note)
        return note

    async def delete(self, note_id: str) -> bool:
        note = await self.get_by_id(note_id)
        if not note:
            return False
        await self.db.delete(note)
        return True
