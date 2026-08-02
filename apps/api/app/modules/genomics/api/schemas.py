from pydantic import BaseModel, Field


class CreateSequenceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    sequence_type: str = Field(
        "genome",
        pattern="^(genome|exome|transcriptome|amplicon|metagenome)$",
    )
    species_id: str | None = None
    project_id: str | None = None
    accession_id: str | None = None
    organism: str | None = Field(None, max_length=255)
    strain: str | None = Field(None, max_length=255)
    chromosome: str | None = Field(None, max_length=50)
    start_position: int | None = Field(None, ge=0)
    end_position: int | None = Field(None, ge=0)
    length: int | None = Field(None, ge=0)
    gc_content: float | None = Field(None, ge=0, le=1)
    n50: int | None = Field(None, ge=0)
    scaffold_count: int | None = Field(None, ge=0)
    source: str | None = Field(None, max_length=255)
    assembly_level: str | None = Field(None, max_length=50)
    genome_build: str | None = Field(None, max_length=50)
    tags: list[str] | None = Field(None, max_length=20)


class UpdateSequenceRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    sequence_type: str | None = Field(
        None,
        pattern="^(genome|exome|transcriptome|amplicon|metagenome)$",
    )
    organism: str | None = Field(None, max_length=255)
    strain: str | None = Field(None, max_length=255)
    chromosome: str | None = Field(None, max_length=50)
    start_position: int | None = Field(None, ge=0)
    end_position: int | None = Field(None, ge=0)
    length: int | None = Field(None, ge=0)
    gc_content: float | None = Field(None, ge=0, le=1)
    n50: int | None = Field(None, ge=0)
    scaffold_count: int | None = Field(None, ge=0)
    source: str | None = Field(None, max_length=255)
    assembly_level: str | None = Field(None, max_length=50)
    genome_build: str | None = Field(None, max_length=50)
    tags: list[str] | None = Field(None, max_length=20)


class SequenceResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    sequence_type: str
    species_id: str | None = None
    project_id: str | None = None
    accession_id: str | None = None
    organism: str | None = None
    strain: str | None = None
    chromosome: str | None = None
    start_position: int | None = None
    end_position: int | None = None
    length: int | None = None
    gc_content: float | None = None
    n50: int | None = None
    scaffold_count: int | None = None
    source: str | None = None
    assembly_level: str | None = None
    genome_build: str | None = None
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedSequencesResponse(BaseModel):
    items: list[SequenceResponse]
    total: int
    skip: int
    limit: int


class CreateVariantRequest(BaseModel):
    sequence_id: str
    chromosome: str = Field(..., min_length=1, max_length=50)
    position: int = Field(..., ge=0)
    reference_allele: str = Field(..., min_length=1)
    alternate_allele: str = Field(..., min_length=1)
    variant_type: str = Field(
        ...,
        pattern="^(SNP|indel|structural|CNV|MNV)$",
    )
    quality: float | None = Field(None, ge=0)
    filter_status: str | None = Field(None, max_length=50)
    depth: int | None = Field(None, ge=0)
    allele_frequency: float | None = Field(None, ge=0, le=1)
    gene_name: str | None = Field(None, max_length=255)
    impact: str | None = Field(None, max_length=50)
    tags: list[str] | None = Field(None, max_length=20)


class BulkCreateVariantItem(BaseModel):
    chromosome: str = Field(..., min_length=1, max_length=50)
    position: int = Field(..., ge=0)
    reference_allele: str = Field(..., min_length=1)
    alternate_allele: str = Field(..., min_length=1)
    variant_type: str = Field(
        ...,
        pattern="^(SNP|indel|structural|CNV|MNV)$",
    )
    quality: float | None = Field(None, ge=0)
    filter_status: str | None = Field(None, max_length=50)
    depth: int | None = Field(None, ge=0)
    allele_frequency: float | None = Field(None, ge=0, le=1)
    gene_name: str | None = Field(None, max_length=255)
    impact: str | None = Field(None, max_length=50)


class BulkCreateVariantsRequest(BaseModel):
    sequence_id: str
    variants: list[BulkCreateVariantItem] = Field(..., min_length=1, max_length=10000)


class VariantResponse(BaseModel):
    id: str
    sequence_id: str
    chromosome: str
    position: int
    reference_allele: str
    alternate_allele: str
    variant_type: str
    quality: float | None = None
    filter_status: str | None = None
    depth: int | None = None
    allele_frequency: float | None = None
    gene_name: str | None = None
    impact: str | None = None
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedVariantsResponse(BaseModel):
    items: list[VariantResponse]
    total: int
    skip: int
    limit: int


class CreateAnnotationRequest(BaseModel):
    sequence_id: str
    gene_symbol: str = Field(..., min_length=1, max_length=100)
    gene_name: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=5000)
    chromosome: str | None = Field(None, max_length=50)
    start_position: int | None = Field(None, ge=0)
    end_position: int | None = Field(None, ge=0)
    strand: str | None = Field(None, pattern="^(\\+|-|1|-1)$")
    biotype: str | None = Field(None, max_length=50)
    go_terms: list[str] | None = None
    pfam_domains: list[str] | None = None
    kegg_pathways: list[str] | None = None


class UpdateAnnotationRequest(BaseModel):
    gene_name: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=5000)
    chromosome: str | None = Field(None, max_length=50)
    start_position: int | None = Field(None, ge=0)
    end_position: int | None = Field(None, ge=0)
    strand: str | None = Field(None, pattern="^(\\+|-|1|-1)$")
    biotype: str | None = Field(None, max_length=50)
    go_terms: list[str] | None = None
    pfam_domains: list[str] | None = None
    kegg_pathways: list[str] | None = None


class AnnotationResponse(BaseModel):
    id: str
    sequence_id: str
    gene_symbol: str
    gene_name: str | None = None
    description: str | None = None
    chromosome: str | None = None
    start_position: int | None = None
    end_position: int | None = None
    strand: str | None = None
    biotype: str | None = None
    go_terms: list[str] | None = None
    pfam_domains: list[str] | None = None
    kegg_pathways: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedAnnotationsResponse(BaseModel):
    items: list[AnnotationResponse]
    total: int
    skip: int
    limit: int
