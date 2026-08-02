from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.literature.domain.interfaces import CollectionRepositoryInterface
from app.modules.literature.domain.models import (
    CollectionModel,
    CollectionPaperModel,
    PaperModel,
)


class CollectionRepository(CollectionRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, collection: CollectionModel) -> CollectionModel:
        self.db.add(collection)
        await self.db.flush()
        await self.db.refresh(collection)
        return collection

    async def get_by_id(self, collection_id: str) -> CollectionModel | None:
        result = await self.db.execute(
            select(CollectionModel).where(CollectionModel.id == collection_id)
        )
        return result.scalar_one_or_none()

    async def list_collections(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[CollectionModel]:
        query = select(CollectionModel)
        if project_id:
            query = query.where(CollectionModel.project_id == project_id)
        if user_id:
            query = query.where(CollectionModel.created_by == user_id)
        if search:
            query = query.where(CollectionModel.name.ilike(f"%{search}%"))
        query = query.order_by(CollectionModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_collections(
        self,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count(CollectionModel.id))
        if project_id:
            query = query.where(CollectionModel.project_id == project_id)
        if user_id:
            query = query.where(CollectionModel.created_by == user_id)
        if search:
            query = query.where(CollectionModel.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, collection: CollectionModel) -> CollectionModel:
        await self.db.flush()
        await self.db.refresh(collection)
        return collection

    async def delete(self, collection_id: str) -> bool:
        collection = await self.get_by_id(collection_id)
        if not collection:
            return False
        await self.db.delete(collection)
        return True

    async def add_paper(self, collection_id: str, paper_id: str) -> bool:
        import uuid
        link = CollectionPaperModel(
            collection_id=uuid.UUID(collection_id),
            paper_id=uuid.UUID(paper_id),
        )
        self.db.add(link)
        await self.db.flush()
        return True

    async def remove_paper(self, collection_id: str, paper_id: str) -> bool:
        import uuid
        result = await self.db.execute(
            select(CollectionPaperModel).where(
                CollectionPaperModel.collection_id == uuid.UUID(collection_id),
                CollectionPaperModel.paper_id == uuid.UUID(paper_id),
            )
        )
        link = result.scalar_one_or_none()
        if not link:
            return False
        await self.db.delete(link)
        await self.db.flush()
        return True

    async def list_papers_in_collection(
        self, collection_id: str, skip: int = 0, limit: int = 100
    ) -> list[PaperModel]:
        import uuid
        result = await self.db.execute(
            select(PaperModel)
            .join(CollectionPaperModel, PaperModel.id == CollectionPaperModel.paper_id)
            .where(CollectionPaperModel.collection_id == uuid.UUID(collection_id))
            .order_by(CollectionPaperModel.added_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_papers_in_collection(self, collection_id: str) -> int:
        import uuid
        result = await self.db.execute(
            select(func.count(CollectionPaperModel.paper_id)).where(
                CollectionPaperModel.collection_id == uuid.UUID(collection_id)
            )
        )
        return result.scalar_one()

    async def paper_in_collection(self, collection_id: str, paper_id: str) -> bool:
        import uuid
        result = await self.db.execute(
            select(func.count(CollectionPaperModel.paper_id)).where(
                CollectionPaperModel.collection_id == uuid.UUID(collection_id),
                CollectionPaperModel.paper_id == uuid.UUID(paper_id),
            )
        )
        return result.scalar_one() > 0
