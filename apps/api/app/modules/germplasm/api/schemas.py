from datetime import date

from pydantic import BaseModel, Field


class CreateSpeciesRequest(BaseModel):
    common_name: str = Field(..., min_length=1, max_length=255)
    scientific_name: str = Field(..., min_length=1, max_length=255)
    family: str | None = Field(None, max_length=255)
    genus: str | None = Field(None, max_length=255)
    species_epithet: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=5000)


class UpdateSpeciesRequest(BaseModel):
    common_name: str | None = Field(None, min_length=1, max_length=255)
    scientific_name: str | None = Field(None, min_length=1, max_length=255)
    family: str | None = Field(None, max_length=255)
    genus: str | None = Field(None, max_length=255)
    species_epithet: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=5000)


class SpeciesResponse(BaseModel):
    id: str
    common_name: str
    scientific_name: str
    family: str | None = None
    genus: str | None = None
    species_epithet: str | None = None
    created_at: str


class PaginatedSpeciesResponse(BaseModel):
    items: list[SpeciesResponse]
    total: int
    skip: int
    limit: int


class CreateAccessionRequest(BaseModel):
    accession_number: str = Field(..., min_length=1, max_length=100)
    species_id: str
    name: str = Field(..., min_length=1, max_length=255)
    project_id: str | None = None
    description: str | None = Field(None, max_length=5000)
    collection_source: str | None = Field(None, max_length=255)
    collection_date: date | None = None
    collection_location: str | None = Field(None, max_length=255)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    altitude: float | None = None
    tags: list[str] | None = Field(None, max_length=20)


class UpdateAccessionRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    collection_source: str | None = Field(None, max_length=255)
    availability_status: str | None = Field(None, pattern="^(available|limited|unavailable|reserved)$")
    tags: list[str] | None = Field(None, max_length=20)


class AccessionResponse(BaseModel):
    id: str
    accession_number: str
    name: str
    species_id: str
    project_id: str | None = None
    description: str | None = None
    collection_source: str | None = None
    collection_date: str | None = None
    collection_location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    availability_status: str
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class AccessionDetailResponse(AccessionResponse):
    passport_data: dict | None = None
    pedigree: dict | None = None
    seed_storages: list[dict] = []
    images: list[dict] = []
    files: list[dict] = []


class PaginatedAccessionsResponse(BaseModel):
    items: list[AccessionResponse]
    total: int
    skip: int
    limit: int


class CreatePassportDataRequest(BaseModel):
    institute_code: str | None = Field(None, max_length=50)
    institute_name: str | None = Field(None, max_length=255)
    country_code: str | None = Field(None, max_length=10)
    collection_number: str | None = Field(None, max_length=100)
    collection_source: str | None = Field(None, max_length=255)
    status: str | None = Field(None, max_length=50)
    duplicates: int | None = Field(None, ge=0)
    remarks: str | None = Field(None, max_length=5000)


class UpdatePassportDataRequest(BaseModel):
    institute_code: str | None = Field(None, max_length=50)
    institute_name: str | None = Field(None, max_length=255)
    country_code: str | None = Field(None, max_length=10)
    collection_number: str | None = Field(None, max_length=100)
    collection_source: str | None = Field(None, max_length=255)
    status: str | None = Field(None, max_length=50)
    duplicates: int | None = Field(None, ge=0)
    remarks: str | None = Field(None, max_length=5000)


class PassportDataResponse(BaseModel):
    id: str
    accession_id: str
    institute_code: str | None = None
    institute_name: str | None = None
    country_code: str | None = None
    collection_number: str | None = None
    collection_source: str | None = None
    status: str | None = None
    duplicates: int | None = None
    remarks: str | None = None
    created_at: str
    updated_at: str


class CreatePedigreeRequest(BaseModel):
    parent1_accession_id: str | None = None
    parent2_accession_id: str | None = None
    parent1_name: str | None = Field(None, max_length=255)
    parent2_name: str | None = Field(None, max_length=255)
    cross_type: str | None = Field(None, max_length=50)
    generation: int | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=5000)


class PedigreeResponse(BaseModel):
    id: str
    accession_id: str
    parent1_accession_id: str | None = None
    parent2_accession_id: str | None = None
    parent1_name: str | None = None
    parent2_name: str | None = None
    cross_type: str | None = None
    generation: int | None = None
    notes: str | None = None
    created_at: str
    updated_at: str


class PedigreeTreeResponse(BaseModel):
    accession_id: str
    ancestors: list[dict]
    descendants: list[dict]


class CreateSeedStorageRequest(BaseModel):
    location: str = Field(..., min_length=1, max_length=255)
    container_type: str | None = Field(None, max_length=50)
    quantity_grams: float | None = Field(None, ge=0)
    seed_count: int | None = Field(None, ge=0)
    storage_conditions: str | None = Field(None, max_length=255)
    storage_date: date | None = None
    expiry_date: date | None = None
    viability: float | None = Field(None, ge=0, le=100)
    notes: str | None = Field(None, max_length=5000)


class UpdateSeedStorageRequest(BaseModel):
    location: str | None = Field(None, min_length=1, max_length=255)
    container_type: str | None = Field(None, max_length=50)
    quantity_grams: float | None = Field(None, ge=0)
    seed_count: int | None = Field(None, ge=0)
    storage_conditions: str | None = Field(None, max_length=255)
    expiry_date: date | None = None
    viability: float | None = Field(None, ge=0, le=100)
    notes: str | None = Field(None, max_length=5000)


class SeedStorageResponse(BaseModel):
    id: str
    accession_id: str
    location: str
    container_type: str | None = None
    quantity_grams: float | None = None
    seed_count: int | None = None
    storage_conditions: str | None = None
    storage_date: str | None = None
    expiry_date: str | None = None
    viability: float | None = None
    notes: str | None = None
    created_at: str
    updated_at: str


class GermplasmImageResponse(BaseModel):
    id: str
    accession_id: str
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    caption: str | None = None
    image_type: str | None = None
    taken_at: str | None = None
    uploaded_by: str
    created_at: str


class GermplasmFileResponse(BaseModel):
    id: str
    accession_id: str
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    description: str | None = None
    file_type: str | None = None
    uploaded_by: str
    created_at: str
