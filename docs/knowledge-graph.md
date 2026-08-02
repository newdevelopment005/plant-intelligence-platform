# Knowledge Graph Module

## Overview

The Knowledge Graph module enables researchers to model, explore, and analyze relationships between scientific entities (genes, proteins, traits, pathways, species, experiments, publications, etc.) within the Plant Intelligence Platform.

## Architecture

Follows Clean Architecture with three layers:

```
knowledge_graph/
├── domain/
│   ├── models.py          # EntityModel, EdgeModel
│   ├── interfaces.py      # EntityRepositoryInterface, EdgeRepositoryInterface
│   └── use_cases.py       # 10 use cases
├── infrastructure/
│   ├── entity_repository.py
│   ├── edge_repository.py
│   └── __init__.py
└── api/
    ├── router.py           # 11 REST endpoints
    └── schemas.py          # 12 Pydantic schemas
```

## Domain Models

### EntityModel

Represents a node in the knowledge graph.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `name` | str (required) | Display name |
| `entity_type` | str (required) | One of 20 types (see below) |
| `description` | str \| None | Description text |
| `source_module` | str \| None | Originating PIP module |
| `source_id` | str \| None | ID in originating module |
| `properties` | dict \| None | Arbitrary JSON properties |
| `tags` | list[str] \| None | Categorization tags |
| `project_id` | UUID \| None | Owning project |
| `created_by` | UUID | Creator user ID |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

**Supported entity types:** `gene`, `protein`, `trait`, `phenotype`, `pathway`, `species`, `researcher`, `institution`, `experiment`, `publication`, `environment`, `treatment`, `disease`, `pest`, `chemical`, `marker`, `qtl`, `go_term`, `kegg_pathway`, `other`

### EdgeModel

Represents a directed relationship between two entities.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `source_entity_id` | UUID | Origin entity |
| `target_entity_id` | UUID | Destination entity |
| `relation_type` | str (required) | Relationship type |
| `description` | str \| None | Relationship description |
| `properties` | dict \| None | Arbitrary JSON properties |
| `weight` | float \| None | Relationship weight |
| `source` | str \| None | Data source |
| `project_id` | UUID \| None | Owning project |
| `created_by` | UUID | Creator user ID |
| `created_at` | datetime | Creation timestamp |

## Interfaces

### EntityRepositoryInterface

```python
class EntityRepositoryInterface(ABC):
    async def create(self, entity: EntityModel) -> EntityModel
    async def get_by_id(self, entity_id: str) -> EntityModel | None
    async def list_entities(self, skip, limit, entity_type, project_id, source_module, search, user_id) -> list[EntityModel]
    async def count_entities(self, entity_type, project_id, source_module, search, user_id) -> int
    async def update(self, entity: EntityModel) -> EntityModel
    async def delete(self, entity_id: str) -> bool
    async def get_neighbors(self, entity_id, relation_type, direction) -> list[dict]
    async def search_semantic(self, query_embedding, limit, project_id) -> list[EntityModel]
```

### EdgeRepositoryInterface

```python
class EdgeRepositoryInterface(ABC):
    async def create(self, edge: EdgeModel) -> EdgeModel
    async def get_by_id(self, edge_id: str) -> EdgeModel | None
    async def list_edges(self, skip, limit, source_entity_id, target_entity_id, relation_type, project_id) -> list[EdgeModel]
    async def count_edges(self, source_entity_id, target_entity_id, relation_type, project_id) -> int
    async def delete(self, edge_id: str) -> bool
    async def delete_by_entity(self, entity_id: str) -> int
    async def get_relation_types(self, project_id) -> list[str]
```

## Use Cases

| Use Case | Input | Output | Validation |
|----------|-------|--------|------------|
| `CreateEntityUseCase` | name, entity_type, user_id, ... | `EntityModel` | Name required, ≤500 chars, valid type |
| `GetEntityUseCase` | entity_id | `EntityModel` | Raises `NotFoundException` if missing |
| `ListEntitiesUseCase` | skip, limit, filters | `dict` (items, total, skip, limit) | Paginated |
| `UpdateEntityUseCase` | entity_id, user_id, fields | `EntityModel` | Creator-only update |
| `DeleteEntityUseCase` | entity_id, user_id | `bool` | Creator-only, cascades edges |
| `ExploreEntityUseCase` | entity_id, relation_type, depth | `dict` (entity, neighbors, depth) | Raises `NotFoundException` if missing |
| `CreateEdgeUseCase` | source_id, target_id, relation_type, user_id, ... | `EdgeModel` | Both entities exist, no self-ref, relation required |
| `ListEdgesUseCase` | skip, limit, filters | `dict` (items, total, skip, limit) | Paginated |
| `DeleteEdgeUseCase` | edge_id | `bool` | Raises `NotFoundException` if missing |
| `GetRelationTypesUseCase` | project_id | `list[str]` | Distinct relation types |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/knowledge-graph/entities` | Create entity |
| GET | `/api/v1/knowledge-graph/entities` | List entities (query: skip, limit, entity_type, project_id, source_module, search) |
| GET | `/api/v1/knowledge-graph/entities/{entity_id}` | Get entity |
| PUT | `/api/v1/knowledge-graph/entities/{entity_id}` | Update entity (creator only) |
| DELETE | `/api/v1/knowledge-graph/entities/{entity_id}` | Delete entity + cascade edges (creator only) |
| GET | `/api/v1/knowledge-graph/entities/{entity_id}/explore` | Explore neighbors (query: relation_type, depth) |
| POST | `/api/v1/knowledge-graph/edges` | Create edge |
| GET | `/api/v1/knowledge-graph/edges` | List edges (query: skip, limit, source_entity_id, target_entity_id, relation_type, project_id) |
| DELETE | `/api/v1/knowledge-graph/edges/{edge_id}` | Delete edge |
| GET | `/api/v1/knowledge-graph/relations` | Get distinct relation types (query: project_id) |
| POST | `/api/v1/knowledge-graph/search` | Semantic search (body: query, limit, project_id) |

## Validation Rules

- **Entity name:** Required, non-empty, max 500 characters.
- **Entity type:** Must be one of the 20 allowed values.
- **Edge relation type:** Required, non-empty string.
- **Self-references:** Edges from an entity to itself are forbidden.
- **Existence:** Source and target entities must exist before creating an edge.
- **Authorization:** Only the creator can update or delete an entity.

## Example: Create Gene → Protein Relationship

```http
POST /api/v1/knowledge-graph/entities
Authorization: Bearer <token>

{
  "name": "TaDREB2A",
  "entity_type": "gene",
  "description": "Drought-responsive element-binding factor",
  "tags": ["drought", "transcription-factor"],
  "project_id": "uuid"
}

# Response: { "id": "gene-uuid", ... }
```

```http
POST /api/v1/knowledge-graph/entities
Authorization: Bearer <token>

{
  "name": "DREB2A Protein",
  "entity_type": "protein",
  "description": "Protein encoded by TaDREB2A",
  "tags": ["drought"],
  "project_id": "uuid"
}

# Response: { "id": "protein-uuid", ... }
```

```http
POST /api/v1/knowledge-graph/edges
Authorization: Bearer <token>

{
  "source_entity_id": "gene-uuid",
  "target_entity_id": "protein-uuid",
  "relation_type": "encodes",
  "description": "Gene encodes protein",
  "project_id": "uuid"
}

# Response: { "id": "edge-uuid", ... }
```

## Example: Explore Gene Network

```http
GET /api/v1/knowledge-graph/entities/{gene-id}/explore?depth=1
Authorization: Bearer <token>

{
  "entity": { "id": "gene-uuid", "name": "TaDREB2A", "entity_type": "gene", ... },
  "neighbors": [
    { "id": "protein-uuid", "name": "DREB2A Protein", "relation_type": "encodes" },
    { "id": "pathway-uuid", "name": "Drought Response Pathway", "relation_type": "participates_in" }
  ],
  "depth": 1
}
```

## Semantic Search

The `/search` endpoint accepts a natural language query and returns entities ranked by vector similarity. The current implementation uses zero-vector embeddings as a placeholder — production will integrate with Sentence Transformers via the AI service.

```http
POST /api/v1/knowledge-graph/search
Authorization: Bearer <token>

{
  "query": "genes involved in drought tolerance",
  "limit": 10,
  "project_id": "uuid"
}
```

## Testing

```bash
cd apps/api
python -m pytest tests/unit/test_knowledge_graph.py -v
```

36 unit tests covering:
- Interface contract validation
- All 10 use cases (success + error paths)
- 6 Pydantic schema validations
- 4 integration tests (module structure, router endpoints, class existence, repo exports)
