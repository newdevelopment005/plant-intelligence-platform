from abc import ABC, abstractmethod

from app.modules.knowledge_graph.domain.models import EdgeModel, EntityModel


class EntityRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, entity: EntityModel) -> EntityModel: ...

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> EntityModel | None: ...

    @abstractmethod
    async def list_entities(
        self,
        skip: int = 0,
        limit: int = 20,
        entity_type: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[EntityModel]: ...

    @abstractmethod
    async def count_entities(
        self,
        entity_type: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, entity: EntityModel) -> EntityModel: ...

    @abstractmethod
    async def delete(self, entity_id: str) -> bool: ...

    @abstractmethod
    async def search_semantic(
        self, query_embedding: list[float], limit: int = 10, project_id: str | None = None
    ) -> list[EntityModel]: ...

    @abstractmethod
    async def get_neighbors(
        self, entity_id: str, relation_type: str | None = None, direction: str = "both"
    ) -> dict: ...


class EdgeRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, edge: EdgeModel) -> EdgeModel: ...

    @abstractmethod
    async def get_by_id(self, edge_id: str) -> EdgeModel | None: ...

    @abstractmethod
    async def list_edges(
        self,
        skip: int = 0,
        limit: int = 50,
        source_entity_id: str | None = None,
        target_entity_id: str | None = None,
        relation_type: str | None = None,
        project_id: str | None = None,
    ) -> list[EdgeModel]: ...

    @abstractmethod
    async def count_edges(
        self,
        source_entity_id: str | None = None,
        target_entity_id: str | None = None,
        relation_type: str | None = None,
        project_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def delete(self, edge_id: str) -> bool: ...

    @abstractmethod
    async def delete_by_entity(self, entity_id: str) -> int: ...

    @abstractmethod
    async def get_relation_types(self, project_id: str | None = None) -> list[str]: ...
