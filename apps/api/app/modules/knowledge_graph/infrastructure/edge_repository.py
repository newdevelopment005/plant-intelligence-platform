from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.knowledge_graph.domain.interfaces import EdgeRepositoryInterface
from app.modules.knowledge_graph.domain.models import EdgeModel


class EdgeRepository(EdgeRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, edge: EdgeModel) -> EdgeModel:
        self.db.add(edge)
        await self.db.flush()
        await self.db.refresh(edge)
        return edge

    async def get_by_id(self, edge_id: str) -> EdgeModel | None:
        result = await self.db.execute(
            select(EdgeModel).where(EdgeModel.id == edge_id)
        )
        return result.scalar_one_or_none()

    async def list_edges(
        self,
        skip: int = 0,
        limit: int = 50,
        source_entity_id: str | None = None,
        target_entity_id: str | None = None,
        relation_type: str | None = None,
        project_id: str | None = None,
    ) -> list[EdgeModel]:
        query = select(EdgeModel)
        if source_entity_id:
            query = query.where(EdgeModel.source_entity_id == source_entity_id)
        if target_entity_id:
            query = query.where(EdgeModel.target_entity_id == target_entity_id)
        if relation_type:
            query = query.where(EdgeModel.relation_type == relation_type)
        if project_id:
            query = query.where(EdgeModel.project_id == project_id)
        query = query.order_by(EdgeModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_edges(
        self,
        source_entity_id: str | None = None,
        target_entity_id: str | None = None,
        relation_type: str | None = None,
        project_id: str | None = None,
    ) -> int:
        query = select(func.count(EdgeModel.id))
        if source_entity_id:
            query = query.where(EdgeModel.source_entity_id == source_entity_id)
        if target_entity_id:
            query = query.where(EdgeModel.target_entity_id == target_entity_id)
        if relation_type:
            query = query.where(EdgeModel.relation_type == relation_type)
        if project_id:
            query = query.where(EdgeModel.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def delete(self, edge_id: str) -> bool:
        edge = await self.get_by_id(edge_id)
        if not edge:
            return False
        await self.db.delete(edge)
        return True

    async def delete_by_entity(self, entity_id: str) -> int:
        import uuid
        eid = uuid.UUID(entity_id) if isinstance(entity_id, str) else entity_id
        result = await self.db.execute(
            select(EdgeModel).where(
                (EdgeModel.source_entity_id == eid) | (EdgeModel.target_entity_id == eid)
            )
        )
        edges = list(result.scalars().all())
        for edge in edges:
            await self.db.delete(edge)
        return len(edges)

    async def get_relation_types(self, project_id: str | None = None) -> list[str]:
        query = select(EdgeModel.relation_type).distinct()
        if project_id:
            query = query.where(EdgeModel.project_id == project_id)
        query = query.order_by(EdgeModel.relation_type)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]
