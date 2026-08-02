from pydantic import BaseModel, Field


class CreateAnalysisJobRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    analysis_type: str = Field(
        ...,
        pattern="^(alignment|blast|variant_calling|rnaseq|phylogenetics|pathway_analysis|gene_prediction|primer_design|codon_usage|motif_search|population_genetics|gwas|qtl_mapping)$",
    )
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")
    input_data: dict = Field(..., min_length=1)
    parameters: dict | None = None
    tags: list[str] | None = Field(None, max_length=20)
    project_id: str | None = None


class UpdateAnalysisJobRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    priority: str | None = Field(None, pattern="^(low|normal|high|urgent)$")
    tags: list[str] | None = Field(None, max_length=20)


class AnalysisJobResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    analysis_type: str
    status: str
    priority: str
    progress_percent: int | None = None
    error_message: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    runtime_seconds: float | None = None
    tags: list[str] | None = None
    project_id: str | None = None
    created_by: str
    created_at: str
    updated_at: str


class AnalysisJobDetailResponse(AnalysisJobResponse):
    input_data: dict | None = None
    parameters: dict | None = None
    result_data: dict | None = None
    output_files: list[str] | None = None


class PaginatedAnalysisJobsResponse(BaseModel):
    items: list[AnalysisJobResponse]
    total: int
    skip: int
    limit: int


class CreatePipelineTemplateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    analysis_type: str = Field(
        ...,
        pattern="^(alignment|blast|variant_calling|rnaseq|phylogenetics|pathway_analysis|gene_prediction|primer_design|codon_usage|motif_search|population_genetics|gwas|qtl_mapping)$",
    )
    steps: list[dict] | None = Field(None, max_length=50)
    default_parameters: dict | None = None
    required_inputs: list[str] | None = Field(None, max_length=20)
    tags: list[str] | None = Field(None, max_length=20)


class UpdatePipelineTemplateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    steps: list[dict] | None = Field(None, max_length=50)
    default_parameters: dict | None = None
    required_inputs: list[str] | None = Field(None, max_length=20)
    tags: list[str] | None = Field(None, max_length=20)


class PipelineTemplateResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    analysis_type: str
    steps: list[dict] | None = None
    default_parameters: dict | None = None
    required_inputs: list[str] | None = None
    version: str
    is_active: bool
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedPipelineTemplatesResponse(BaseModel):
    items: list[PipelineTemplateResponse]
    total: int
    skip: int
    limit: int
