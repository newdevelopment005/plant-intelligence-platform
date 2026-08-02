from pydantic import BaseModel, Field


class CreateEntityRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    entity_type: str = Field(
        ...,
        pattern="^(gene|protein|trait|phenotype|pathway|species|researcher|institution|experiment|publication|environment|treatment|disease|pest|chemical|marker|qtl|go_term|kegg_pathway|other)$",
    )
    description: str | None = Field(None, max_length=10000)
    source_module: str | None = Field(None, max_length=100)
    source_id: str | None = Field(None, max_length=255)
    properties: dict | None = None
    tags: list[str] | None = Field(None, max_length=20)
    project_id: str | None = None


class UpdateEntityRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=10000)
    properties: dict | None = None
    tags: list[str] | None = Field(None, max_length=20)


class EntityResponse(BaseModel):
    id: str
    name: str
    entity_type: str
    description: str | None = None
    source_module: str | None = None
    source_id: str | None = None
    properties: dict | None = None
    tags: list[str] | None = None
    project_id: str | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedEntitiesResponse(BaseModel):
    items: list[EntityResponse]
    total: int
    skip: int
    limit: int


class CreateEdgeRequest(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relation_type: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    properties: dict | None = None
    weight: float | None = Field(None, ge=0, le=1)
    source: str | None = Field(None, max_length=255)
    project_id: str | None = None


class EdgeResponse(BaseModel):
    id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    description: str | None = None
    properties: dict | None = None
    weight: float | None = None
    source: str | None = None
    project_id: str | None = None
    created_by: str
    created_at: str


class PaginatedEdgesResponse(BaseModel):
    items: list[EdgeResponse]
    total: int
    skip: int
    limit: int


class ExploreEntityResponse(BaseModel):
    entity: dict
    neighbors: dict
    depth: int


class NeighborEntity(BaseModel):
    id: str
    name: str
    entity_type: str
    description: str | None = None


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(10, ge=1, le=100)
    project_id: str | None = None
    entity_type: str | None = None
