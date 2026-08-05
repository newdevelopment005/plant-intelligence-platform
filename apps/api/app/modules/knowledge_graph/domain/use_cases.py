from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.knowledge_graph.domain.interfaces import (
    EdgeRepositoryInterface,
    EntityRepositoryInterface,
)
from app.modules.knowledge_graph.domain.models import EdgeModel, EntityModel


def _to_uuid(value: str | None) -> UUID | None:
    if value is None:
        return None
    return UUID(value) if not isinstance(value, UUID) else value


class CreateEntityUseCase:
    def __init__(self, entity_repo: EntityRepositoryInterface):
        self.entity_repo = entity_repo

    async def execute(
        self,
        name: str,
        entity_type: str,
        user_id: str,
        description: str | None = None,
        source_module: str | None = None,
        source_id: str | None = None,
        properties: dict | None = None,
        tags: list[str] | None = None,
        project_id: str | None = None,
    ) -> EntityModel:
        if not name or not name.strip():
            raise ValidationException("Entity name is required")
        if len(name.strip()) > 500:
            raise ValidationException("Entity name must be less than 500 characters")

        valid_types = (
            "gene", "protein", "trait", "phenotype", "pathway", "species",
            "researcher", "institution", "experiment", "publication",
            "environment", "treatment", "disease", "pest", "chemical",
            "marker", "qtl", "go_term", "kegg_pathway", "other",
        )
        if entity_type not in valid_types:
            raise ValidationException(f"Invalid entity type. Must be one of: {', '.join(valid_types)}")

        entity = EntityModel(
            name=name.strip(),
            entity_type=entity_type,
            description=description.strip() if description else None,
            source_module=source_module,
            source_id=source_id,
            properties=properties,
            tags=tags,
            project_id=_to_uuid(project_id),
            created_by=_to_uuid(user_id),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.entity_repo.create(entity)


class GetEntityUseCase:
    def __init__(self, entity_repo: EntityRepositoryInterface):
        self.entity_repo = entity_repo

    async def execute(self, entity_id: str) -> EntityModel:
        entity = await self.entity_repo.get_by_id(entity_id)
        if not entity:
            raise NotFoundException("Entity", entity_id)
        return entity


class ListEntitiesUseCase:
    def __init__(self, entity_repo: EntityRepositoryInterface):
        self.entity_repo = entity_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        entity_type: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        entities = await self.entity_repo.list_entities(
            skip=skip, limit=limit, entity_type=entity_type,
            project_id=project_id, source_module=source_module,
            search=search, user_id=user_id,
        )
        total = await self.entity_repo.count_entities(
            entity_type=entity_type, project_id=project_id,
            source_module=source_module, search=search, user_id=user_id,
        )
        return {
            "items": [
                {
                    "id": str(e.id),
                    "name": e.name,
                    "entity_type": e.entity_type,
                    "description": e.description,
                    "source_module": e.source_module,
                    "source_id": e.source_id,
                    "properties": e.properties,
                    "tags": e.tags,
                    "project_id": str(e.project_id) if e.project_id else None,
                    "created_by": str(e.created_by),
                    "created_at": e.created_at.isoformat(),
                    "updated_at": e.updated_at.isoformat(),
                }
                for e in entities
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateEntityUseCase:
    def __init__(self, entity_repo: EntityRepositoryInterface):
        self.entity_repo = entity_repo

    async def execute(
        self,
        entity_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        properties: dict | None = None,
        tags: list[str] | None = None,
    ) -> EntityModel:
        entity = await self.entity_repo.get_by_id(entity_id)
        if not entity:
            raise NotFoundException("Entity", entity_id)

        if str(entity.created_by) != user_id:
            raise ValidationException("Only the creator can update this entity")

        if name is not None:
            if not name.strip():
                raise ValidationException("Entity name cannot be empty")
            entity.name = name.strip()
        if description is not None:
            entity.description = description.strip() if description else None
        if properties is not None:
            entity.properties = properties
        if tags is not None:
            entity.tags = tags

        entity.updated_at = datetime.now(UTC)
        return await self.entity_repo.update(entity)


class DeleteEntityUseCase:
    def __init__(self, entity_repo: EntityRepositoryInterface, edge_repo: EdgeRepositoryInterface):
        self.entity_repo = entity_repo
        self.edge_repo = edge_repo

    async def execute(self, entity_id: str, user_id: str) -> bool:
        entity = await self.entity_repo.get_by_id(entity_id)
        if not entity:
            raise NotFoundException("Entity", entity_id)

        if str(entity.created_by) != user_id:
            raise ValidationException("Only the creator can delete this entity")

        await self.edge_repo.delete_by_entity(entity_id)
        return await self.entity_repo.delete(entity_id)


class ExploreEntityUseCase:
    def __init__(self, entity_repo: EntityRepositoryInterface):
        self.entity_repo = entity_repo

    async def execute(
        self,
        entity_id: str,
        relation_type: str | None = None,
        depth: int = 1,
    ) -> dict:
        entity = await self.entity_repo.get_by_id(entity_id)
        if not entity:
            raise NotFoundException("Entity", entity_id)

        neighbors = await self.entity_repo.get_neighbors(
            entity_id=entity_id,
            relation_type=relation_type,
            direction="both",
        )

        return {
            "entity": {
                "id": str(entity.id),
                "name": entity.name,
                "entity_type": entity.entity_type,
                "description": entity.description,
                "properties": entity.properties,
            },
            "neighbors": neighbors,
            "depth": depth,
        }


class CreateEdgeUseCase:
    def __init__(self, edge_repo: EdgeRepositoryInterface, entity_repo: EntityRepositoryInterface):
        self.edge_repo = edge_repo
        self.entity_repo = entity_repo

    async def execute(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relation_type: str,
        user_id: str,
        description: str | None = None,
        properties: dict | None = None,
        weight: float | None = None,
        source: str | None = None,
        project_id: str | None = None,
    ) -> EdgeModel:
        source = await self.entity_repo.get_by_id(source_entity_id)
        if not source:
            raise NotFoundException("Source entity", source_entity_id)

        target = await self.entity_repo.get_by_id(target_entity_id)
        if not target:
            raise NotFoundException("Target entity", target_entity_id)

        if not relation_type or not relation_type.strip():
            raise ValidationException("Relation type is required")

        if source_entity_id == target_entity_id:
            raise ValidationException("Self-referencing edges are not allowed")

        edge = EdgeModel(
            source_entity_id=_to_uuid(source_entity_id),
            target_entity_id=_to_uuid(target_entity_id),
            relation_type=relation_type.strip(),
            description=description.strip() if description else None,
            properties=properties,
            weight=weight,
            source=source,
            project_id=_to_uuid(project_id),
            created_by=_to_uuid(user_id),
            created_at=datetime.now(UTC),
        )

        return await self.edge_repo.create(edge)


class ListEdgesUseCase:
    def __init__(self, edge_repo: EdgeRepositoryInterface):
        self.edge_repo = edge_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 50,
        source_entity_id: str | None = None,
        target_entity_id: str | None = None,
        relation_type: str | None = None,
        project_id: str | None = None,
    ) -> dict:
        edges = await self.edge_repo.list_edges(
            skip=skip, limit=limit,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relation_type=relation_type,
            project_id=project_id,
        )
        total = await self.edge_repo.count_edges(
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relation_type=relation_type,
            project_id=project_id,
        )
        return {
            "items": [
                {
                    "id": str(e.id),
                    "source_entity_id": str(e.source_entity_id),
                    "target_entity_id": str(e.target_entity_id),
                    "relation_type": e.relation_type,
                    "description": e.description,
                    "properties": e.properties,
                    "weight": e.weight,
                    "source": e.source,
                    "project_id": str(e.project_id) if e.project_id else None,
                    "created_by": str(e.created_by),
                    "created_at": e.created_at.isoformat(),
                }
                for e in edges
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class DeleteEdgeUseCase:
    def __init__(self, edge_repo: EdgeRepositoryInterface):
        self.edge_repo = edge_repo

    async def execute(self, edge_id: str) -> bool:
        edge = await self.edge_repo.get_by_id(edge_id)
        if not edge:
            raise NotFoundException("Edge", edge_id)
        return await self.edge_repo.delete(edge_id)


class GetRelationTypesUseCase:
    def __init__(self, edge_repo: EdgeRepositoryInterface):
        self.edge_repo = edge_repo

    async def execute(self, project_id: str | None = None) -> list[str]:
        return await self.edge_repo.get_relation_types(project_id=project_id)
