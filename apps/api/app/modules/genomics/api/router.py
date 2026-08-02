import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.genomics.api.schemas import (
    BulkCreateVariantsRequest,
    CreateAnnotationRequest,
    CreateSequenceRequest,
    CreateVariantRequest,
    UpdateAnnotationRequest,
    UpdateSequenceRequest,
)
from app.modules.genomics.domain.use_cases import (
    BulkCreateVariantsUseCase,
    CreateAnnotationUseCase,
    CreateSequenceUseCase,
    CreateVariantUseCase,
    DeleteAnnotationUseCase,
    DeleteSequenceUseCase,
    DeleteVariantUseCase,
    GetAnnotationUseCase,
    GetSequenceUseCase,
    GetVariantUseCase,
    ListAnnotationsUseCase,
    ListSequencesUseCase,
    ListVariantsUseCase,
    SearchVariantsUseCase,
    UpdateAnnotationUseCase,
    UpdateSequenceUseCase,
)
from app.modules.genomics.infrastructure.annotation_repository import GeneAnnotationRepository
from app.modules.genomics.infrastructure.sequence_repository import SequenceRepository
from app.modules.genomics.infrastructure.variant_repository import VariantRepository

logger = structlog.get_logger()
router = APIRouter()


def _get_repos(db: AsyncSession):
    return {
        "sequence": SequenceRepository(db),
        "variant": VariantRepository(db),
        "annotation": GeneAnnotationRepository(db),
    }


@router.get("/sequences", response_model=None)
async def list_sequences(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sequence_type: str | None = Query(
        None,
        pattern="^(genome|exome|transcriptome|amplicon|metagenome)$",
    ),
    species_id: str | None = Query(None),
    project_id: str | None = Query(None),
    search: str | None = Query(None, max_length=255),
):
    repos = _get_repos(db)
    use_case = ListSequencesUseCase(repos["sequence"])
    return await use_case.execute(
        skip=skip,
        limit=limit,
        sequence_type=sequence_type,
        species_id=species_id,
        project_id=project_id,
        search=search,
        user_id=str(current_user["id"]),
    )


@router.post("/sequences", status_code=201)
async def create_sequence(
    body: CreateSequenceRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateSequenceUseCase(repos["sequence"])
    sequence = await use_case.execute(
        name=body.name,
        description=body.description,
        sequence_type=body.sequence_type,
        species_id=body.species_id,
        project_id=body.project_id,
        accession_id=body.accession_id,
        organism=body.organism,
        strain=body.strain,
        chromosome=body.chromosome,
        start_position=body.start_position,
        end_position=body.end_position,
        length=body.length,
        gc_content=body.gc_content,
        n50=body.n50,
        scaffold_count=body.scaffold_count,
        source=body.source,
        assembly_level=body.assembly_level,
        genome_build=body.genome_build,
        tags=body.tags,
        user_id=str(current_user["id"]),
    )
    logger.info("sequence_created", sequence_id=str(sequence.id))
    return {
        "id": str(sequence.id),
        "name": sequence.name,
        "description": sequence.description,
        "sequence_type": sequence.sequence_type,
        "species_id": str(sequence.species_id) if sequence.species_id else None,
        "project_id": str(sequence.project_id) if sequence.project_id else None,
        "organism": sequence.organism,
        "chromosome": sequence.chromosome,
        "length": sequence.length,
        "gc_content": sequence.gc_content,
        "assembly_level": sequence.assembly_level,
        "genome_build": sequence.genome_build,
        "tags": sequence.tags,
        "created_by": str(sequence.created_by),
        "created_at": sequence.created_at.isoformat(),
        "updated_at": sequence.updated_at.isoformat(),
    }


@router.get("/sequences/{sequence_id}")
async def get_sequence(
    sequence_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetSequenceUseCase(repos["sequence"])
    sequence = await use_case.execute(sequence_id)
    return {
        "id": str(sequence.id),
        "name": sequence.name,
        "description": sequence.description,
        "sequence_type": sequence.sequence_type,
        "species_id": str(sequence.species_id) if sequence.species_id else None,
        "project_id": str(sequence.project_id) if sequence.project_id else None,
        "accession_id": str(sequence.accession_id) if sequence.accession_id else None,
        "organism": sequence.organism,
        "strain": sequence.strain,
        "chromosome": sequence.chromosome,
        "start_position": sequence.start_position,
        "end_position": sequence.end_position,
        "length": sequence.length,
        "gc_content": sequence.gc_content,
        "n50": sequence.n50,
        "scaffold_count": sequence.scaffold_count,
        "source": sequence.source,
        "assembly_level": sequence.assembly_level,
        "genome_build": sequence.genome_build,
        "tags": sequence.tags,
        "metadata": sequence.metadata_json,
        "created_by": str(sequence.created_by),
        "created_at": sequence.created_at.isoformat(),
        "updated_at": sequence.updated_at.isoformat(),
    }


@router.put("/sequences/{sequence_id}")
async def update_sequence(
    sequence_id: str,
    body: UpdateSequenceRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdateSequenceUseCase(repos["sequence"])
    sequence = await use_case.execute(
        sequence_id=sequence_id,
        user_id=str(current_user["id"]),
        name=body.name,
        description=body.description,
        sequence_type=body.sequence_type,
        organism=body.organism,
        strain=body.strain,
        chromosome=body.chromosome,
        start_position=body.start_position,
        end_position=body.end_position,
        length=body.length,
        gc_content=body.gc_content,
        n50=body.n50,
        scaffold_count=body.scaffold_count,
        source=body.source,
        assembly_level=body.assembly_level,
        genome_build=body.genome_build,
        tags=body.tags,
    )
    return {
        "id": str(sequence.id),
        "name": sequence.name,
        "description": sequence.description,
        "sequence_type": sequence.sequence_type,
        "organism": sequence.organism,
        "chromosome": sequence.chromosome,
        "length": sequence.length,
        "gc_content": sequence.gc_content,
        "assembly_level": sequence.assembly_level,
        "genome_build": sequence.genome_build,
        "tags": sequence.tags,
        "created_at": sequence.created_at.isoformat(),
        "updated_at": sequence.updated_at.isoformat(),
    }


@router.delete("/sequences/{sequence_id}")
async def delete_sequence(
    sequence_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteSequenceUseCase(repos["sequence"])
    await use_case.execute(sequence_id, str(current_user["id"]))
    return {"message": "Sequence deleted successfully"}


@router.get("/sequences/{sequence_id}/variants", response_model=None)
async def list_variants(
    sequence_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    chromosome: str | None = Query(None, max_length=50),
    variant_type: str | None = Query(
        None,
        pattern="^(SNP|indel|structural|CNV|MNV)$",
    ),
    gene_name: str | None = Query(None, max_length=255),
):
    repos = _get_repos(db)
    use_case = ListVariantsUseCase(repos["variant"])
    return await use_case.execute(
        sequence_id=sequence_id,
        skip=skip,
        limit=limit,
        chromosome=chromosome,
        variant_type=variant_type,
        gene_name=gene_name,
    )


@router.post("/sequences/{sequence_id}/variants", status_code=201)
async def create_variant(
    sequence_id: str,
    body: CreateVariantRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateVariantUseCase(repos["variant"], repos["sequence"])
    variant = await use_case.execute(
        sequence_id=sequence_id,
        chromosome=body.chromosome,
        position=body.position,
        reference_allele=body.reference_allele,
        alternate_allele=body.alternate_allele,
        variant_type=body.variant_type,
        quality=body.quality,
        filter_status=body.filter_status,
        depth=body.depth,
        allele_frequency=body.allele_frequency,
        gene_name=body.gene_name,
        impact=body.impact,
        tags=body.tags,
        user_id=str(current_user["id"]),
    )
    logger.info("variant_created", variant_id=str(variant.id))
    return {
        "id": str(variant.id),
        "sequence_id": str(variant.sequence_id),
        "chromosome": variant.chromosome,
        "position": variant.position,
        "reference_allele": variant.reference_allele,
        "alternate_allele": variant.alternate_allele,
        "variant_type": variant.variant_type,
        "quality": variant.quality,
        "depth": variant.depth,
        "allele_frequency": variant.allele_frequency,
        "gene_name": variant.gene_name,
        "impact": variant.impact,
        "created_by": str(variant.created_by),
        "created_at": variant.created_at.isoformat(),
        "updated_at": variant.updated_at.isoformat(),
    }


@router.post("/sequences/{sequence_id}/variants/bulk", status_code=201)
async def bulk_create_variants(
    sequence_id: str,
    body: BulkCreateVariantsRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = BulkCreateVariantsUseCase(repos["variant"], repos["sequence"])
    variants_data = []
    for v in body.variants:
        variants_data.append({
            "chromosome": v.chromosome,
            "position": v.position,
            "reference_allele": v.reference_allele,
            "alternate_allele": v.alternate_allele,
            "variant_type": v.variant_type,
            "quality": v.quality,
            "filter_status": v.filter_status,
            "depth": v.depth,
            "allele_frequency": v.allele_frequency,
            "gene_name": v.gene_name,
            "impact": v.impact,
        })
    variants = await use_case.execute(
        sequence_id=sequence_id,
        variants_data=variants_data,
        user_id=str(current_user["id"]),
    )
    logger.info("variants_bulk_created", count=len(variants))
    return {
        "message": f"{len(variants)} variants created successfully",
        "count": len(variants),
    }


@router.get("/variants/search")
async def search_variants(
    sequence_id: str = Query(...),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    chromosome: str | None = Query(None, max_length=50),
    start: int | None = Query(None, ge=0),
    end: int | None = Query(None, ge=0),
    variant_type: str | None = Query(
        None,
        pattern="^(SNP|indel|structural|CNV|MNV)$",
    ),
    gene_name: str | None = Query(None, max_length=255),
    min_quality: float | None = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    repos = _get_repos(db)
    use_case = SearchVariantsUseCase(repos["variant"])
    return await use_case.execute(
        sequence_id=sequence_id,
        chromosome=chromosome,
        start=start,
        end=end,
        variant_type=variant_type,
        gene_name=gene_name,
        min_quality=min_quality,
        skip=skip,
        limit=limit,
    )


@router.get("/variants/{variant_id}")
async def get_variant(
    variant_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetVariantUseCase(repos["variant"])
    variant = await use_case.execute(variant_id)
    return {
        "id": str(variant.id),
        "sequence_id": str(variant.sequence_id),
        "chromosome": variant.chromosome,
        "position": variant.position,
        "reference_allele": variant.reference_allele,
        "alternate_allele": variant.alternate_allele,
        "variant_type": variant.variant_type,
        "quality": variant.quality,
        "filter_status": variant.filter_status,
        "depth": variant.depth,
        "allele_frequency": variant.allele_frequency,
        "gene_name": variant.gene_name,
        "impact": variant.impact,
        "annotations": variant.annotations,
        "tags": variant.tags,
        "created_by": str(variant.created_by),
        "created_at": variant.created_at.isoformat(),
        "updated_at": variant.updated_at.isoformat(),
    }


@router.delete("/variants/{variant_id}")
async def delete_variant(
    variant_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteVariantUseCase(repos["variant"])
    await use_case.execute(variant_id)
    return {"message": "Variant deleted successfully"}


@router.get("/sequences/{sequence_id}/annotations", response_model=None)
async def list_annotations(
    sequence_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
):
    repos = _get_repos(db)
    use_case = ListAnnotationsUseCase(repos["annotation"])
    return await use_case.execute(
        sequence_id=sequence_id,
        skip=skip,
        limit=limit,
        search=search,
    )


@router.post("/sequences/{sequence_id}/annotations", status_code=201)
async def create_annotation(
    sequence_id: str,
    body: CreateAnnotationRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateAnnotationUseCase(repos["annotation"], repos["sequence"])
    annotation = await use_case.execute(
        sequence_id=sequence_id,
        gene_symbol=body.gene_symbol,
        gene_name=body.gene_name,
        description=body.description,
        chromosome=body.chromosome,
        start_position=body.start_position,
        end_position=body.end_position,
        strand=body.strand,
        biotype=body.biotype,
        go_terms=body.go_terms,
        pfam_domains=body.pfam_domains,
        kegg_pathways=body.kegg_pathways,
        user_id=str(current_user["id"]),
    )
    logger.info("annotation_created", annotation_id=str(annotation.id))
    return {
        "id": str(annotation.id),
        "sequence_id": str(annotation.sequence_id),
        "gene_symbol": annotation.gene_symbol,
        "gene_name": annotation.gene_name,
        "description": annotation.description,
        "chromosome": annotation.chromosome,
        "start_position": annotation.start_position,
        "end_position": annotation.end_position,
        "strand": annotation.strand,
        "biotype": annotation.biotype,
        "go_terms": annotation.go_terms,
        "pfam_domains": annotation.pfam_domains,
        "kegg_pathways": annotation.kegg_pathways,
        "created_by": str(annotation.created_by),
        "created_at": annotation.created_at.isoformat(),
        "updated_at": annotation.updated_at.isoformat(),
    }


@router.get("/annotations/{annotation_id}")
async def get_annotation(
    annotation_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetAnnotationUseCase(repos["annotation"])
    annotation = await use_case.execute(annotation_id)
    return {
        "id": str(annotation.id),
        "sequence_id": str(annotation.sequence_id),
        "gene_symbol": annotation.gene_symbol,
        "gene_name": annotation.gene_name,
        "description": annotation.description,
        "chromosome": annotation.chromosome,
        "start_position": annotation.start_position,
        "end_position": annotation.end_position,
        "strand": annotation.strand,
        "biotype": annotation.biotype,
        "go_terms": annotation.go_terms,
        "pfam_domains": annotation.pfam_domains,
        "kegg_pathways": annotation.kegg_pathways,
        "orthologs": annotation.orthologs,
        "expression_data": annotation.expression_data,
        "created_by": str(annotation.created_by),
        "created_at": annotation.created_at.isoformat(),
        "updated_at": annotation.updated_at.isoformat(),
    }


@router.put("/annotations/{annotation_id}")
async def update_annotation(
    annotation_id: str,
    body: UpdateAnnotationRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdateAnnotationUseCase(repos["annotation"])
    annotation = await use_case.execute(
        annotation_id=annotation_id,
        gene_name=body.gene_name,
        description=body.description,
        chromosome=body.chromosome,
        start_position=body.start_position,
        end_position=body.end_position,
        strand=body.strand,
        biotype=body.biotype,
        go_terms=body.go_terms,
        pfam_domains=body.pfam_domains,
        kegg_pathways=body.kegg_pathways,
    )
    return {
        "id": str(annotation.id),
        "sequence_id": str(annotation.sequence_id),
        "gene_symbol": annotation.gene_symbol,
        "gene_name": annotation.gene_name,
        "description": annotation.description,
        "chromosome": annotation.chromosome,
        "start_position": annotation.start_position,
        "end_position": annotation.end_position,
        "strand": annotation.strand,
        "biotype": annotation.biotype,
        "go_terms": annotation.go_terms,
        "pfam_domains": annotation.pfam_domains,
        "kegg_pathways": annotation.kegg_pathways,
        "created_at": annotation.created_at.isoformat(),
        "updated_at": annotation.updated_at.isoformat(),
    }


@router.delete("/annotations/{annotation_id}")
async def delete_annotation(
    annotation_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteAnnotationUseCase(repos["annotation"])
    await use_case.execute(annotation_id)
    return {"message": "Annotation deleted successfully"}
