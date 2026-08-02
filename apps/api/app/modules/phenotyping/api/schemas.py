from datetime import date, datetime

from pydantic import BaseModel, Field


class CreateExperimentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    experiment_type: str = Field(
        "field",
        pattern="^(field|greenhouse|controlled_environment|growth_chamber)$",
    )
    project_id: str | None = None
    location: str | None = Field(None, max_length=255)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    altitude: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    tags: list[str] | None = Field(None, max_length=20)


class UpdateExperimentRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    experiment_type: str | None = Field(
        None,
        pattern="^(field|greenhouse|controlled_environment|growth_chamber)$",
    )
    location: str | None = Field(None, max_length=255)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    altitude: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(
        None,
        pattern="^(planned|in_progress|completed|archived)$",
    )
    tags: list[str] | None = Field(None, max_length=20)


class ExperimentResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    experiment_type: str
    project_id: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class ExperimentDetailResponse(ExperimentResponse):
    traits: list[dict] = []
    measurement_count: int = 0


class PaginatedExperimentsResponse(BaseModel):
    items: list[ExperimentResponse]
    total: int
    skip: int
    limit: int


class CreateTraitRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    trait_category: str | None = Field(None, max_length=100)
    unit: str | None = Field(None, max_length=50)
    data_type: str = Field(
        "numeric",
        pattern="^(numeric|text|categorical|date|boolean)$",
    )
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: list[str] | None = None
    is_required: bool = False


class UpdateTraitRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    trait_category: str | None = Field(None, max_length=100)
    unit: str | None = Field(None, max_length=50)
    data_type: str | None = Field(
        None,
        pattern="^(numeric|text|categorical|date|boolean)$",
    )
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: list[str] | None = None
    is_required: bool | None = None


class TraitResponse(BaseModel):
    id: str
    experiment_id: str
    name: str
    description: str | None = None
    trait_category: str | None = None
    unit: str | None = None
    data_type: str
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: list[str] | None = None
    is_required: bool
    created_at: str
    updated_at: str


class PaginatedTraitsResponse(BaseModel):
    items: list[TraitResponse]
    total: int
    skip: int
    limit: int


class CreateMeasurementRequest(BaseModel):
    experiment_id: str
    trait_id: str
    accession_id: str | None = None
    value_numeric: float | None = None
    value_text: str | None = Field(None, max_length=500)
    value_date: date | None = None
    rep: int | None = Field(None, ge=0)
    block: str | None = Field(None, max_length=50)
    plot: str | None = Field(None, max_length=50)
    plant_id: str | None = Field(None, max_length=100)
    notes: str | None = Field(None, max_length=5000)
    measured_at: datetime | None = None
    image_url: str | None = Field(None, max_length=500)


class BulkCreateMeasurementItem(BaseModel):
    trait_id: str
    accession_id: str | None = None
    value_numeric: float | None = None
    value_text: str | None = Field(None, max_length=500)
    value_date: date | None = None
    rep: int | None = Field(None, ge=0)
    block: str | None = Field(None, max_length=50)
    plot: str | None = Field(None, max_length=50)
    plant_id: str | None = Field(None, max_length=100)
    notes: str | None = Field(None, max_length=5000)
    measured_at: datetime | None = None
    image_url: str | None = Field(None, max_length=500)


class BulkCreateMeasurementsRequest(BaseModel):
    experiment_id: str
    measurements: list[BulkCreateMeasurementItem] = Field(..., min_length=1, max_length=1000)


class UpdateMeasurementRequest(BaseModel):
    value_numeric: float | None = None
    value_text: str | None = Field(None, max_length=500)
    value_date: date | None = None
    rep: int | None = Field(None, ge=0)
    block: str | None = Field(None, max_length=50)
    plot: str | None = Field(None, max_length=50)
    plant_id: str | None = Field(None, max_length=100)
    notes: str | None = Field(None, max_length=5000)
    measured_at: datetime | None = None
    image_url: str | None = Field(None, max_length=500)


class MeasurementResponse(BaseModel):
    id: str
    experiment_id: str
    trait_id: str
    accession_id: str | None = None
    value_numeric: float | None = None
    value_text: str | None = None
    value_date: str | None = None
    rep: int | None = None
    block: str | None = None
    plot: str | None = None
    plant_id: str | None = None
    notes: str | None = None
    measured_at: str | None = None
    measured_by: str | None = None
    image_url: str | None = None
    created_at: str
    updated_at: str


class PaginatedMeasurementsResponse(BaseModel):
    items: list[MeasurementResponse]
    total: int
    skip: int
    limit: int


class ExperimentSummaryResponse(BaseModel):
    experiment_id: str
    total_measurements: int
    trait_count: int
    accession_count: int
    traits_summary: list[dict]
