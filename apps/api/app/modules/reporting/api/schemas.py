from pydantic import BaseModel, Field


class CreateReportRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    report_type: str = Field(
        ...,
        pattern="^(phenotyping|genotyping|germplasm|experiment|project_summary|custom|statistical|comparative|temporal|geospatial|summary|genomics|literature|project)$",
    )
    format: str = Field("pdf", pattern="^(pdf|csv|json|xlsx|html|docx)$")
    data_source: str | None = Field(None, max_length=100)
    parameters: dict | None = None
    tags: list[str] | None = Field(None, max_length=20)
    project_id: str | None = None


class UpdateReportRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    tags: list[str] | None = Field(None, max_length=20)


class ReportResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    report_type: str
    status: str
    format: str
    data_source: str | None = None
    file_url: str | None = None
    file_size_bytes: int | None = None
    error_message: str | None = None
    tags: list[str] | None = None
    project_id: str | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedReportsResponse(BaseModel):
    items: list[ReportResponse]
    total: int
    skip: int
    limit: int


class CreateTemplateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    report_type: str = Field(
        ...,
        pattern="^(phenotyping|genotyping|germplasm|experiment|project_summary|custom|statistical|comparative|temporal|geospatial)$",
    )
    default_format: str = Field("pdf", pattern="^(pdf|csv|json|xlsx|html|docx)$")
    data_source: str | None = Field(None, max_length=100)
    layout: dict | None = None
    default_parameters: dict | None = None
    tags: list[str] | None = Field(None, max_length=20)


class UpdateTemplateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    layout: dict | None = None
    default_parameters: dict | None = None
    tags: list[str] | None = Field(None, max_length=20)


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    report_type: str
    default_format: str
    data_source: str | None = None
    layout: dict | None = None
    default_parameters: dict | None = None
    is_active: bool
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedTemplatesResponse(BaseModel):
    items: list[TemplateResponse]
    total: int
    skip: int
    limit: int
