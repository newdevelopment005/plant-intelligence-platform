from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.knowledge_graph.domain.interfaces import EntityRepositoryInterface
from app.modules.knowledge_graph.domain.models import EdgeModel, EntityModel


class EntityRepository(EntityRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, entity: EntityModel) -> EntityModel:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: str) -> EntityModel | None:
        result = await self.db.execute(
            select(EntityModel).where(EntityModel.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def list_entities(
        self,
        skip: int = 0,
        limit: int = 20,
        entity_type: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[EntityModel]:
        query = select(EntityModel)
        if entity_type:
            query = query.where(EntityModel.entity_type == entity_type)
        if project_id:
            query = query.where(EntityModel.project_id == project_id)
        if source_module:
            query = query.where(EntityModel.source_module == source_module)
        if user_id:
            query = query.where(EntityModel.created_by == user_id)
        if search:
            query = query.where(EntityModel.name.ilike(f"%{search}%"))
        query = query.order_by(EntityModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_entities(
        self,
        entity_type: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count(EntityModel.id))
        if entity_type:
            query = query.where(EntityModel.entity_type == entity_type)
        if project_id:
            query = query.where(EntityModel.project_id == project_id)
        if source_module:
            query = query.where(EntityModel.source_module == source_module)
        if user_id:
            query = query.where(EntityModel.created_by == user_id)
        if search:
            query = query.where(EntityModel.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, entity: EntityModel) -> EntityModel:
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity_id: str) -> bool:
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False
        await self.db.delete(entity)
        return True

    async def search_semantic(
        self, query_embedding: list[float], limit: int = 10, project_id: str | None = None
    ) -> list[EntityModel]:
        query = select(EntityModel).where(EntityModel.embedding_id.isnot(None))
        if project_id:
            query = query.where(EntityModel.project_id == project_id)
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_neighbors(
        self, entity_id: str, relation_type: str | None = None, direction: str = "both"
    ) -> dict:
        outgoing = []
        incoming = []

        if direction in ("outgoing", "both"):
            query = select(EdgeModel).where(EdgeModel.source_entity_id == entity_id)
            if relation_type:
                query = query.where(EdgeModel.relation_type == relation_type)
            result = await self.db.execute(query)
            outgoing = list(result.scalars().all())

        if direction in ("incoming", "both"):
            query = select(EdgeModel).where(EdgeModel.target_entity_id == entity_id)
            if relation_type:
                query = query.where(EdgeModel.relation_type == relation_type)
            result = await self.db.execute(query)
            incoming = list(result.scalars().all())

        return {
            "outgoing": [
                {
                    "edge_id": str(e.id),
                    "target_entity_id": str(e.target_entity_id),
                    "relation_type": e.relation_type,
                    "description": e.description,
                    "weight": e.weight,
                }
                for e in outgoing
            ],
            "incoming": [
                {
                    "edge_id": str(e.id),
                    "source_entity_id": str(e.source_entity_id),
                    "relation_type": e.relation_type,
                    "description": e.description,
                    "weight": e.weight,
                }
                for e in incoming
            ],
        }
