from pydantic import BaseModel, Field


class UploadImageRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    file_url: str = Field(..., min_length=1, max_length=2000)
    image_type: str = Field(
        "general",
        pattern="^(general|leaf|root|seed|fruit|flower|microscopy|drone|phenotype|xray|thermal)$",
    )
    source_module: str | None = Field(None, max_length=50)
    source_id: str | None = Field(None, max_length=255)
    species: str | None = Field(None, max_length=255)
    tissue_type: str | None = Field(None, max_length=100)
    growth_stage: str | None = Field(None, max_length=100)
    magnification: str | None = Field(None, max_length=50)
    file_size_bytes: int | None = Field(None, ge=0)
    mime_type: str | None = Field(None, max_length=100)
    width: int | None = Field(None, ge=1)
    height: int | None = Field(None, ge=1)
    tags: list[str] | None = Field(None, max_length=20)
    project_id: str | None = None
    metadata_json: dict | None = None


class UpdateImageRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    image_type: str | None = Field(None, max_length=50)
    species: str | None = Field(None, max_length=255)
    tissue_type: str | None = Field(None, max_length=100)
    growth_stage: str | None = Field(None, max_length=100)
    tags: list[str] | None = Field(None, max_length=20)


class ImageResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    file_url: str
    thumbnail_url: str | None = None
    file_size_bytes: int | None = None
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    image_type: str
    source_module: str | None = None
    source_id: str | None = None
    species: str | None = None
    tissue_type: str | None = None
    growth_stage: str | None = None
    magnification: str | None = None
    tags: list[str] | None = None
    project_id: str | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedImagesResponse(BaseModel):
    items: list[ImageResponse]
    total: int
    skip: int
    limit: int


class CreateAnalysisJobRequest(BaseModel):
    image_id: str
    analysis_type: str = Field(
        ...,
        pattern="^(disease_detection|pest_detection|growth_stage|phenotype_measurement|leaf_area|root_analysis|seed_counting|fruit_quality|morphology|stress_detection|weed_detection|flowering_time)$",
    )
    parameters: dict | None = None
    project_id: str | None = None


class AnalysisJobResponse(BaseModel):
    id: str
    image_id: str
    analysis_type: str
    status: str
    error_message: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    runtime_seconds: float | None = None
    model_version: str | None = None
    project_id: str | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedAnalysisJobsResponse(BaseModel):
    items: list[AnalysisJobResponse]
    total: int
    skip: int
    limit: int


class AnalysisResultResponse(BaseModel):
    id: str
    job_id: str
    result_type: str
    label: str | None = None
    confidence: float | None = None
    bbox: dict | None = None
    measurements: dict | None = None
    annotations: dict | None = None
    created_at: str


class PaginatedAnalysisResultsResponse(BaseModel):
    items: list[AnalysisResultResponse]
    total: int
    skip: int
    limit: int
