from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.literature.domain.interfaces import PaperRepositoryInterface
from app.modules.literature.domain.models import PaperModel


class PaperRepository(PaperRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, paper: PaperModel) -> PaperModel:
        self.db.add(paper)
        await self.db.flush()
        await self.db.refresh(paper)
        return paper

    async def get_by_id(self, paper_id: str) -> PaperModel | None:
        result = await self.db.execute(
            select(PaperModel).where(PaperModel.id == paper_id)
        )
        return result.scalar_one_or_none()

    async def get_by_doi(self, doi: str) -> PaperModel | None:
        result = await self.db.execute(
            select(PaperModel).where(PaperModel.doi == doi)
        )
        return result.scalar_one_or_none()

    async def get_by_pmid(self, pmid: str) -> PaperModel | None:
        result = await self.db.execute(
            select(PaperModel).where(PaperModel.pmid == pmid)
        )
        return result.scalar_one_or_none()

    async def list_papers(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        source: str | None = None,
        paper_type: str | None = None,
        year: int | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[PaperModel]:
        query = select(PaperModel)
        if project_id:
            query = query.where(PaperModel.project_id == project_id)
        if source:
            query = query.where(PaperModel.source == source)
        if paper_type:
            query = query.where(PaperModel.paper_type == paper_type)
        if year:
            query = query.where(PaperModel.year == year)
        if user_id:
            query = query.where(PaperModel.created_by == user_id)
        if search:
            query = query.where(PaperModel.title.ilike(f"%{search}%"))
        query = query.order_by(PaperModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_papers(
        self,
        project_id: str | None = None,
        source: str | None = None,
        paper_type: str | None = None,
        year: int | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count(PaperModel.id))
        if project_id:
            query = query.where(PaperModel.project_id == project_id)
        if source:
            query = query.where(PaperModel.source == source)
        if paper_type:
            query = query.where(PaperModel.paper_type == paper_type)
        if year:
            query = query.where(PaperModel.year == year)
        if user_id:
            query = query.where(PaperModel.created_by == user_id)
        if search:
            query = query.where(PaperModel.title.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, paper: PaperModel) -> PaperModel:
        await self.db.flush()
        await self.db.refresh(paper)
        return paper

    async def delete(self, paper_id: str) -> bool:
        paper = await self.get_by_id(paper_id)
        if not paper:
            return False
        await self.db.delete(paper)
        return True

    async def search_semantic(
        self, query_embedding: list[float], limit: int = 10, project_id: str | None = None
    ) -> list[PaperModel]:
        query = select(PaperModel).where(PaperModel.embedding_id.isnot(None))
        if project_id:
            query = query.where(PaperModel.project_id == project_id)
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
