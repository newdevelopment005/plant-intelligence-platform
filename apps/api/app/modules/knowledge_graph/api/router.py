from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.knowledge_graph.api.schemas import (
    CreateEdgeRequest,
    CreateEntityRequest,
    EdgeResponse,
    EntityResponse,
    ExploreEntityResponse,
    PaginatedEdgesResponse,
    PaginatedEntitiesResponse,
    SemanticSearchRequest,
    UpdateEntityRequest,
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

router = APIRouter(redirect_slashes=False)


def _entity_to_dict(e) -> dict:
    return {
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


def _edge_to_dict(e) -> dict:
    return {
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


# ────────────────────────── Entities ───────────────────────────────────
@router.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    request: CreateEntityRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository
    repo = EntityRepository(db)
    uc = CreateEntityUseCase(entity_repo=repo)
    entity = await uc.execute(
        name=request.name,
        entity_type=request.entity_type,
        user_id=current_user["id"],
        description=request.description,
        source_module=request.source_module,
        source_id=request.source_id,
        properties=request.properties,
        tags=request.tags,
        project_id=request.project_id,
    )
    return _entity_to_dict(entity)


@router.get("/entities", response_model=PaginatedEntitiesResponse)
async def list_entities(
    skip: int = 0,
    limit: int = 20,
    entity_type: str | None = None,
    project_id: str | None = None,
    source_module: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository
    repo = EntityRepository(db)
    uc = ListEntitiesUseCase(entity_repo=repo)
    result = await uc.execute(
        skip=skip, limit=limit, entity_type=entity_type,
        project_id=project_id, source_module=source_module,
        search=search, user_id=current_user["id"],
    )
    return PaginatedEntitiesResponse(**result)


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository
    repo = EntityRepository(db)
    uc = GetEntityUseCase(entity_repo=repo)
    entity = await uc.execute(entity_id)
    return _entity_to_dict(entity)


@router.put("/entities/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    request: UpdateEntityRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository
    repo = EntityRepository(db)
    uc = UpdateEntityUseCase(entity_repo=repo)
    entity = await uc.execute(
        entity_id=entity_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        properties=request.properties,
        tags=request.tags,
    )
    return _entity_to_dict(entity)


@router.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.edge_repository import EdgeRepository
    from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository
    entity_repo = EntityRepository(db)
    edge_repo = EdgeRepository(db)
    uc = DeleteEntityUseCase(entity_repo=entity_repo, edge_repo=edge_repo)
    await uc.execute(entity_id=entity_id, user_id=current_user["id"])


@router.get("/entities/{entity_id}/explore", response_model=ExploreEntityResponse)
async def explore_entity(
    entity_id: str,
    relation_type: str | None = None,
    depth: int = 1,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository
    repo = EntityRepository(db)
    uc = ExploreEntityUseCase(entity_repo=repo)
    return await uc.execute(entity_id=entity_id, relation_type=relation_type, depth=depth)


# ────────────────────────── Edges ──────────────────────────────────────
@router.post("/edges", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
async def create_edge(
    request: CreateEdgeRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.edge_repository import EdgeRepository
    from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository
    edge_repo = EdgeRepository(db)
    entity_repo = EntityRepository(db)
    uc = CreateEdgeUseCase(edge_repo=edge_repo, entity_repo=entity_repo)
    edge = await uc.execute(
        source_entity_id=request.source_entity_id,
        target_entity_id=request.target_entity_id,
        relation_type=request.relation_type,
        user_id=current_user["id"],
        description=request.description,
        properties=request.properties,
        weight=request.weight,
        source=request.source,
        project_id=request.project_id,
    )
    return _edge_to_dict(edge)


@router.get("/edges", response_model=PaginatedEdgesResponse)
async def list_edges(
    skip: int = 0,
    limit: int = 50,
    source_entity_id: str | None = None,
    target_entity_id: str | None = None,
    relation_type: str | None = None,
    project_id: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.edge_repository import EdgeRepository
    repo = EdgeRepository(db)
    uc = ListEdgesUseCase(edge_repo=repo)
    result = await uc.execute(
        skip=skip, limit=limit,
        source_entity_id=source_entity_id,
        target_entity_id=target_entity_id,
        relation_type=relation_type,
        project_id=project_id,
    )
    return PaginatedEdgesResponse(**result)


@router.delete("/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(
    edge_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.edge_repository import EdgeRepository
    repo = EdgeRepository(db)
    uc = DeleteEdgeUseCase(edge_repo=repo)
    await uc.execute(edge_id)


@router.get("/relations", response_model=list[str])
async def get_relation_types(
    project_id: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.edge_repository import EdgeRepository
    repo = EdgeRepository(db)
    uc = GetRelationTypesUseCase(edge_repo=repo)
    return await uc.execute(project_id=project_id)


# ────────────────────────── Semantic Search ────────────────────────────
@router.post("/search", response_model=PaginatedEntitiesResponse)
async def search_entities(
    request: SemanticSearchRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.knowledge_graph.infrastructure.entity_repository import EntityRepository
    repo = EntityRepository(db)
    embedding = [0.0] * 384
    entities = await repo.search_semantic(
        query_embedding=embedding,
        limit=request.limit,
        project_id=request.project_id,
    )
    return PaginatedEntitiesResponse(
        items=[EntityResponse.model_validate(e) for e in entities],
        total=len(entities),
        skip=0,
        limit=request.limit,
    )
