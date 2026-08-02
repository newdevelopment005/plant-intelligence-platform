from pydantic import BaseModel, Field


class CreateConversationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    model_used: str | None = Field(None, max_length=100)
    tags: list[str] | None = Field(None, max_length=20)
    project_id: str | None = None


class UpdateConversationRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    status: str | None = Field(None, pattern="^(active|archived|deleted)$")
    tags: list[str] | None = Field(None, max_length=20)


class ConversationResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: str
    model_used: str | None = None
    tags: list[str] | None = None
    message_count: int = 0
    project_id: str | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedConversationsResponse(BaseModel):
    items: list[ConversationResponse]
    total: int
    skip: int
    limit: int


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    model_used: str | None = None
    tokens_used: int | None = None
    sources: list[dict] | None = None
    created_at: str


class PaginatedMessagesResponse(BaseModel):
    items: list[MessageResponse]
    total: int
    skip: int
    limit: int


class SummarizeLiteratureRequest(BaseModel):
    paper_ids: list[str] = Field(..., min_length=1, max_length=50)
    focus_areas: list[str] | None = Field(None, max_length=10)


class LiteratureSummaryResponse(BaseModel):
    summary: str
    key_findings: list[str]
    methodologies: list[str]
    gaps_identified: list[str]
    paper_count: int


class RecommendGenesRequest(BaseModel):
    trait_description: str = Field(..., min_length=1, max_length=2000)
    species: str | None = Field(None, max_length=200)


class GeneRecommendationResponse(BaseModel):
    recommendations: list[dict]
    trait: str
    species: str | None = None
    reasoning: str


class DesignExperimentRequest(BaseModel):
    research_question: str = Field(..., min_length=1, max_length=5000)
    species: str | None = Field(None, max_length=200)
    variables: list[str] | None = Field(None, max_length=50)
    constraints: dict | None = None


class ExperimentDesignResponse(BaseModel):
    experiment_design: dict
    suggestions: list[str]


class AnalyzeImageRequest(BaseModel):
    image_url: str | None = None
    image_base64: str | None = Field(None, max_length=1000000)
    analysis_type: str = Field(
        "general",
        pattern="^(general|phenotype|disease|growth_stage|morphism)$",
    )


class ImageAnalysisResponse(BaseModel):
    analysis: dict
    interpretation: str
