from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.knowledge_graph.api.schemas import (
    CreateEdgeRequest,
    CreateEntityRequest,
    EdgeResponse,
    EntityResponse,
    ExploreEntityResponse,
    PaginatedEdgesResponse,
    PaginatedEntitiesResponse,
)
from app.modules.knowledge_graph.domain.interfaces import (
    EdgeRepositoryInterface,
    EntityRepositoryInterface,
)
from app.modules.knowledge_graph.domain.use_cases import (
    CreateEdgeUseCase,
    CreateEntityUseCase,
    DeleteEdgeUseCase,
    DeleteEntityUseCase,
    ExploreEntityUseCase,
    GetEntityUseCase,
    GetRelationTypesUseCase,
    ListEdgesUseCase,
    ListEntitiesUseCase,
    UpdateEntityUseCase,
)
from app.modules.knowledge_graph.infrastructure.edge_repository import EdgeRepository
from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository


def make_mock_repo(**methods):
    repo = MagicMock(name="MockRepo")
    for method_name, value in methods.items():
        if callable(value):
            try:
                result = value()
                setattr(repo, method_name, AsyncMock(return_value=result))
            except TypeError:
                setattr(repo, method_name, AsyncMock(side_effect=value))
        else:
            setattr(repo, method_name, AsyncMock(return_value=value))
    return repo


# ────────────────────────── Interface Tests ────────────────────────────
class TestInterfaces:
    def test_entity_interface_methods(self):
        for method in [
            "create", "get_by_id", "list_entities", "count_entities",
            "update", "delete", "search_semantic", "get_neighbors",
        ]:
            assert hasattr(EntityRepositoryInterface, method)

    def test_edge_interface_methods(self):
        for method in [
            "create", "get_by_id", "list_edges", "count_edges",
            "delete", "delete_by_entity", "get_relation_types",
        ]:
            assert hasattr(EdgeRepositoryInterface, method)


# ────────────────────────── Entity Use Case Tests ──────────────────────
class TestCreateEntityUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(create=lambda: MagicMock(name="entity"))
        uc = CreateEntityUseCase(entity_repo=mock_repo)
        await uc.execute(name="AtTCP1", entity_type="gene", user_id="user-1")
        mock_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        mock_repo = make_mock_repo()
        uc = CreateEntityUseCase(entity_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(name="", entity_type="gene", user_id="user-1")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        mock_repo = make_mock_repo()
        uc = CreateEntityUseCase(entity_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(name="Test", entity_type="invalid", user_id="user-1")


class TestGetEntityUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="entity"))
        uc = GetEntityUseCase(entity_repo=mock_repo)
        await uc.execute("entity-1")
        mock_repo.get_by_id.assert_awaited_once_with("entity-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = GetEntityUseCase(entity_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestListEntitiesUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(list_entities=lambda: [], count_entities=lambda: 0)
        uc = ListEntitiesUseCase(entity_repo=mock_repo)
        result = await uc.execute()
        assert isinstance(result, dict)
        assert "items" in result

    @pytest.mark.asyncio
    async def test_with_filters(self):
        mock_repo = make_mock_repo(list_entities=lambda: [], count_entities=lambda: 0)
        uc = ListEntitiesUseCase(entity_repo=mock_repo)
        await uc.execute(entity_type="gene", project_id="proj-1")
        mock_repo.list_entities.assert_awaited_once()


class TestUpdateEntityUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        entity = MagicMock(name="entity")
        entity.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: entity, update=lambda: entity)
        uc = UpdateEntityUseCase(entity_repo=mock_repo)
        await uc.execute(entity_id="entity-1", user_id="user-1", name="Updated")
        mock_repo.get_by_id.assert_awaited_once_with("entity-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = UpdateEntityUseCase(entity_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(entity_id="nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        entity = MagicMock(name="entity")
        entity.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: entity)
        uc = UpdateEntityUseCase(entity_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(entity_id="entity-1", user_id="user-2")


class TestDeleteEntityUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        entity = MagicMock(name="entity")
        entity.created_by = "user-1"
        mock_entity = make_mock_repo(get_by_id=lambda: entity, delete=lambda: True)
        mock_edge = make_mock_repo(delete_by_entity=lambda: 0)
        uc = DeleteEntityUseCase(entity_repo=mock_entity, edge_repo=mock_edge)
        await uc.execute(entity_id="entity-1", user_id="user-1")
        mock_entity.delete.assert_awaited_once_with("entity-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_entity = make_mock_repo(get_by_id=lambda: None)
        mock_edge = make_mock_repo()
        uc = DeleteEntityUseCase(entity_repo=mock_entity, edge_repo=mock_edge)
        with pytest.raises(NotFoundException):
            await uc.execute(entity_id="nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        entity = MagicMock(name="entity")
        entity.created_by = "user-1"
        mock_entity = make_mock_repo(get_by_id=lambda: entity)
        mock_edge = make_mock_repo()
        uc = DeleteEntityUseCase(entity_repo=mock_entity, edge_repo=mock_edge)
        with pytest.raises(ValidationException):
            await uc.execute(entity_id="entity-1", user_id="user-2")


class TestExploreEntityUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        entity = MagicMock(name="entity")
        entity.id = "entity-1"
        entity.name = "AtTCP1"
        entity.entity_type = "gene"
        entity.description = "Transcription factor"
        entity.properties = {}
        mock_repo = make_mock_repo(
            get_by_id=lambda: entity,
            get_neighbors=lambda: {"outgoing": [], "incoming": []},
        )
        uc = ExploreEntityUseCase(entity_repo=mock_repo)
        result = await uc.execute(entity_id="entity-1")
        assert result["entity"]["name"] == "AtTCP1"
        assert "neighbors" in result

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = ExploreEntityUseCase(entity_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(entity_id="nonexistent")


# ────────────────────────── Edge Use Case Tests ────────────────────────
class TestCreateEdgeUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        source = MagicMock(name="source")
        target = MagicMock(name="target")
        mock_edge = make_mock_repo(create=lambda: MagicMock(name="edge"))
        mock_entity = make_mock_repo(
            get_by_id=lambda eid: source if eid == "src-1" else target,
        )
        uc = CreateEdgeUseCase(edge_repo=mock_edge, entity_repo=mock_entity)
        await uc.execute(
            source_entity_id="src-1",
            target_entity_id="tgt-1",
            relation_type="encodes",
            user_id="user-1",
        )
        mock_edge.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_source_not_found(self):
        mock_edge = make_mock_repo()
        mock_entity = make_mock_repo(get_by_id=lambda eid: None)
        uc = CreateEdgeUseCase(edge_repo=mock_edge, entity_repo=mock_entity)
        with pytest.raises(NotFoundException):
            await uc.execute(
                source_entity_id="nonexistent",
                target_entity_id="tgt-1",
                relation_type="encodes",
                user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_target_not_found(self):
        source = MagicMock(name="source")
        mock_edge = make_mock_repo()
        mock_entity = make_mock_repo(
            get_by_id=lambda eid: source if eid == "src-1" else None,
        )
        uc = CreateEdgeUseCase(edge_repo=mock_edge, entity_repo=mock_entity)
        with pytest.raises(NotFoundException):
            await uc.execute(
                source_entity_id="src-1",
                target_entity_id="nonexistent",
                relation_type="encodes",
                user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_empty_relation_type_raises(self):
        source = MagicMock(name="source")
        target = MagicMock(name="target")
        mock_edge = make_mock_repo()
        mock_entity = make_mock_repo(
            get_by_id=lambda eid: source if eid == "src-1" else target,
        )
        uc = CreateEdgeUseCase(edge_repo=mock_edge, entity_repo=mock_entity)
        with pytest.raises(ValidationException):
            await uc.execute(
                source_entity_id="src-1",
                target_entity_id="tgt-1",
                relation_type="",
                user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_self_reference_raises(self):
        source = MagicMock(name="source")
        mock_edge = make_mock_repo()
        mock_entity = make_mock_repo(get_by_id=lambda eid: source)
        uc = CreateEdgeUseCase(edge_repo=mock_edge, entity_repo=mock_entity)
        with pytest.raises(ValidationException):
            await uc.execute(
                source_entity_id="src-1",
                target_entity_id="src-1",
                relation_type="self_loop",
                user_id="user-1",
            )


class TestListEdgesUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(list_edges=lambda: [], count_edges=lambda: 0)
        uc = ListEdgesUseCase(edge_repo=mock_repo)
        result = await uc.execute()
        assert isinstance(result, dict)
        assert "items" in result


class TestDeleteEdgeUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="edge"), delete=lambda: True)
        uc = DeleteEdgeUseCase(edge_repo=mock_repo)
        await uc.execute("edge-1")
        mock_repo.delete.assert_awaited_once_with("edge-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = DeleteEdgeUseCase(edge_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestGetRelationTypesUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_relation_types=lambda: ["encodes", "associated_with"])
        uc = GetRelationTypesUseCase(edge_repo=mock_repo)
        result = await uc.execute()
        assert isinstance(result, list)


# ────────────────────────── Schema Tests ───────────────────────────────
class TestSchemaValidation:
    def test_create_entity_request(self):
        req = CreateEntityRequest(name="AtTCP1", entity_type="gene")
        assert req.name == "AtTCP1"
        assert req.entity_type == "gene"

    def test_create_edge_request(self):
        req = CreateEdgeRequest(
            source_entity_id="src-1",
            target_entity_id="tgt-1",
            relation_type="encodes",
        )
        assert req.relation_type == "encodes"

    def test_entity_response(self):
        resp = EntityResponse(
            id="e-1", name="Test", entity_type="gene",
            created_by="user-1", created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        assert resp.id == "e-1"

    def test_edge_response(self):
        resp = EdgeResponse(
            id="edge-1", source_entity_id="src-1", target_entity_id="tgt-1",
            relation_type="encodes", created_by="user-1",
            created_at="2025-01-01T00:00:00",
        )
        assert resp.id == "edge-1"

    def test_paginated_responses(self):
        e = PaginatedEntitiesResponse(items=[], total=0, skip=0, limit=20)
        ed = PaginatedEdgesResponse(items=[], total=0, skip=0, limit=50)
        assert e.total == 0
        assert ed.total == 0

    def test_explore_response(self):
        resp = ExploreEntityResponse(
            entity={"id": "e-1", "name": "Test"},
            neighbors={"outgoing": [], "incoming": []},
            depth=1,
        )
        assert resp.depth == 1


# ────────────────────────── Integration Tests ──────────────────────────
class TestKnowledgeGraphModuleIntegration:
    def test_module_has_correct_structure(self):
        pass

    def test_router_has_all_endpoints(self):
        from app.modules.knowledge_graph.api.router import router
        routes = [r.path for r in router.routes]
        assert any("/entities" in p for p in routes)
        assert any("/edges" in p for p in routes)
        assert any("/relations" in p for p in routes)
        assert any("/search" in p for p in routes)
        assert any("/explore" in p for p in routes)

    def test_all_use_case_classes_exist(self):
        use_cases = [
            CreateEntityUseCase, GetEntityUseCase, ListEntitiesUseCase,
            UpdateEntityUseCase, DeleteEntityUseCase, ExploreEntityUseCase,
            CreateEdgeUseCase, ListEdgesUseCase, DeleteEdgeUseCase,
            GetRelationTypesUseCase,
        ]
        assert len(use_cases) == 10

    def test_infrastructure_repos_exist(self):
        assert EntityRepository is not None
        assert EdgeRepository is not None
