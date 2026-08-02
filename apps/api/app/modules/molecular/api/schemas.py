from datetime import date

from pydantic import BaseModel, Field


class CreateMoleculeExperimentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    experiment_type: str = Field(
        "PCR",
        pattern="^(PCR|qPCR|RT-PCR|RNA-Seq|DNA_Extraction|RNA_Extraction|ChIP-Seq|ATAC-Seq|Proteomics|Metabolomics|CRISPR|Transformation|Cloning)$",
    )
    project_id: str | None = None
    species_id: str | None = None
    protocol: str | None = Field(None, max_length=10000)
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = Field(None, max_length=5000)
    tags: list[str] | None = Field(None, max_length=20)


class UpdateMoleculeExperimentRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    experiment_type: str | None = Field(
        None,
        pattern="^(PCR|qPCR|RT-PCR|RNA-Seq|DNA_Extraction|RNA_Extraction|ChIP-Seq|ATAC-Seq|Proteomics|Metabolomics|CRISPR|Transformation|Cloning)$",
    )
    protocol: str | None = Field(None, max_length=10000)
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(
        None, pattern="^(planned|in_progress|completed|archived)$"
    )
    result_summary: str | None = Field(None, max_length=5000)
    notes: str | None = Field(None, max_length=5000)
    tags: list[str] | None = Field(None, max_length=20)


class MoleculeExperimentResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    experiment_type: str
    project_id: str | None = None
    species_id: str | None = None
    status: str
    start_date: str | None = None
    end_date: str | None = None
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedMoleculeExperimentsResponse(BaseModel):
    items: list[MoleculeExperimentResponse]
    total: int
    skip: int
    limit: int


class CreatePrimerRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    sequence: str = Field(..., min_length=1, max_length=200)
    primer_type: str = Field(
        "forward", pattern="^(forward|reverse|probe|nested|universal)$"
    )
    target_gene: str | None = Field(None, max_length=255)
    target_organism: str | None = Field(None, max_length=255)
    tm: float | None = Field(None, ge=0, le=100)
    amplicon_size: int | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=5000)


class UpdatePrimerRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    sequence: str | None = Field(None, min_length=1, max_length=200)
    primer_type: str | None = Field(
        None, pattern="^(forward|reverse|probe|nested|universal)$"
    )
    target_gene: str | None = Field(None, max_length=255)
    target_organism: str | None = Field(None, max_length=255)
    tm: float | None = Field(None, ge=0, le=100)
    amplicon_size: int | None = Field(None, ge=0)
    is_validated: bool | None = None
    notes: str | None = Field(None, max_length=5000)


class PrimerResponse(BaseModel):
    id: str
    experiment_id: str
    name: str
    description: str | None = None
    sequence: str
    primer_type: str
    target_gene: str | None = None
    target_organism: str | None = None
    length: int | None = None
    tm: float | None = None
    gc_percent: float | None = None
    amplicon_size: int | None = None
    is_validated: bool
    created_by: str
    created_at: str
    updated_at: str


class PaginatedPrimersResponse(BaseModel):
    items: list[PrimerResponse]
    total: int
    skip: int
    limit: int


class CreateConstructRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    construct_type: str = Field(
        "plasmid",
        pattern="^(plasmid|binary_vector|expression_construct|reporter|crispr_construct)$",
    )
    vector_backbone: str | None = Field(None, max_length=255)
    insert_sequence: str | None = Field(None, max_length=50000)
    insert_name: str | None = Field(None, max_length=255)
    selection_marker: str | None = Field(None, max_length=255)
    promoter: str | None = Field(None, max_length=255)
    resistance: str | None = Field(None, max_length=255)
    species_id: str | None = None
    notes: str | None = Field(None, max_length=5000)
    tags: list[str] | None = Field(None, max_length=20)


class UpdateConstructRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    construct_type: str | None = Field(
        None,
        pattern="^(plasmid|binary_vector|expression_construct|reporter|crispr_construct)$",
    )
    vector_backbone: str | None = Field(None, max_length=255)
    insert_sequence: str | None = Field(None, max_length=50000)
    insert_name: str | None = Field(None, max_length=255)
    selection_marker: str | None = Field(None, max_length=255)
    promoter: str | None = Field(None, max_length=255)
    resistance: str | None = Field(None, max_length=255)
    is_validated: bool | None = None
    notes: str | None = Field(None, max_length=5000)
    tags: list[str] | None = Field(None, max_length=20)


class ConstructResponse(BaseModel):
    id: str
    experiment_id: str
    name: str
    description: str | None = None
    construct_type: str
    vector_backbone: str | None = None
    insert_name: str | None = None
    insert_size: int | None = None
    selection_marker: str | None = None
    promoter: str | None = None
    resistance: str | None = None
    is_validated: bool
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedConstructsResponse(BaseModel):
    items: list[ConstructResponse]
    total: int
    skip: int
    limit: int
