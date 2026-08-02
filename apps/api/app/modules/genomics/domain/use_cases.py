from datetime import UTC, datetime

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.genomics.domain.interfaces import (
    GeneAnnotationRepositoryInterface,
    SequenceRepositoryInterface,
    VariantRepositoryInterface,
)
from app.modules.genomics.domain.models import (
    GeneAnnotationModel,
    SequenceModel,
    VariantModel,
)


class CreateSequenceUseCase:
    def __init__(self, sequence_repo: SequenceRepositoryInterface):
        self.sequence_repo = sequence_repo

    async def execute(
        self,
        name: str,
        user_id: str,
        description: str | None = None,
        sequence_type: str = "genome",
        species_id: str | None = None,
        project_id: str | None = None,
        accession_id: str | None = None,
        organism: str | None = None,
        strain: str | None = None,
        chromosome: str | None = None,
        start_position: int | None = None,
        end_position: int | None = None,
        length: int | None = None,
        gc_content: float | None = None,
        n50: int | None = None,
        scaffold_count: int | None = None,
        source: str | None = None,
        assembly_level: str | None = None,
        genome_build: str | None = None,
        tags: list[str] | None = None,
    ) -> SequenceModel:
        if not name or not name.strip():
            raise ValidationException("Sequence name is required")
        if len(name.strip()) > 255:
            raise ValidationException("Sequence name must be less than 255 characters")

        valid_types = ("genome", "exome", "transcriptome", "amplicon", "metagenome")
        if sequence_type not in valid_types:
            raise ValidationException(f"Invalid sequence type. Must be one of: {', '.join(valid_types)}")

        if gc_content is not None and (gc_content < 0 or gc_content > 1):
            raise ValidationException("GC content must be between 0 and 1")

        if start_position is not None and end_position is not None and start_position > end_position:
            raise ValidationException("Start position cannot be greater than end position")

        sequence = SequenceModel(
            name=name.strip(),
            description=description.strip() if description else None,
            sequence_type=sequence_type,
            species_id=species_id,
            project_id=project_id,
            accession_id=accession_id,
            organism=organism.strip() if organism else None,
            strain=strain.strip() if strain else None,
            chromosome=chromosome.strip() if chromosome else None,
            start_position=start_position,
            end_position=end_position,
            length=length,
            gc_content=gc_content,
            n50=n50,
            scaffold_count=scaffold_count,
            source=source.strip() if source else None,
            assembly_level=assembly_level.strip() if assembly_level else None,
            genome_build=genome_build.strip() if genome_build else None,
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.sequence_repo.create(sequence)


class GetSequenceUseCase:
    def __init__(self, sequence_repo: SequenceRepositoryInterface):
        self.sequence_repo = sequence_repo

    async def execute(self, sequence_id: str) -> SequenceModel:
        sequence = await self.sequence_repo.get_by_id(sequence_id)
        if not sequence:
            raise NotFoundException("Sequence", sequence_id)
        return sequence


class ListSequencesUseCase:
    def __init__(self, sequence_repo: SequenceRepositoryInterface):
        self.sequence_repo = sequence_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        sequence_type: str | None = None,
        species_id: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        sequences = await self.sequence_repo.list_sequences(
            skip=skip,
            limit=limit,
            sequence_type=sequence_type,
            species_id=species_id,
            project_id=project_id,
            search=search,
            user_id=user_id,
        )
        total = await self.sequence_repo.count_sequences(
            sequence_type=sequence_type,
            species_id=species_id,
            project_id=project_id,
            search=search,
            user_id=user_id,
        )

        return {
            "items": [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "description": s.description,
                    "sequence_type": s.sequence_type,
                    "species_id": str(s.species_id) if s.species_id else None,
                    "project_id": str(s.project_id) if s.project_id else None,
                    "organism": s.organism,
                    "chromosome": s.chromosome,
                    "length": s.length,
                    "gc_content": s.gc_content,
                    "assembly_level": s.assembly_level,
                    "genome_build": s.genome_build,
                    "tags": s.tags,
                    "created_by": str(s.created_by),
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                }
                for s in sequences
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateSequenceUseCase:
    def __init__(self, sequence_repo: SequenceRepositoryInterface):
        self.sequence_repo = sequence_repo

    async def execute(
        self,
        sequence_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        sequence_type: str | None = None,
        organism: str | None = None,
        strain: str | None = None,
        chromosome: str | None = None,
        start_position: int | None = None,
        end_position: int | None = None,
        length: int | None = None,
        gc_content: float | None = None,
        n50: int | None = None,
        scaffold_count: int | None = None,
        source: str | None = None,
        assembly_level: str | None = None,
        genome_build: str | None = None,
        tags: list[str] | None = None,
    ) -> SequenceModel:
        sequence = await self.sequence_repo.get_by_id(sequence_id)
        if not sequence:
            raise NotFoundException("Sequence", sequence_id)

        if str(sequence.created_by) != user_id:
            raise ValidationException("Only the creator can update this sequence")

        if name is not None:
            if not name.strip():
                raise ValidationException("Sequence name cannot be empty")
            sequence.name = name.strip()
        if description is not None:
            sequence.description = description.strip() if description else None
        if sequence_type is not None:
            valid_types = ("genome", "exome", "transcriptome", "amplicon", "metagenome")
            if sequence_type not in valid_types:
                raise ValidationException(f"Invalid sequence type. Must be one of: {', '.join(valid_types)}")
            sequence.sequence_type = sequence_type
        if organism is not None:
            sequence.organism = organism.strip() if organism else None
        if strain is not None:
            sequence.strain = strain.strip() if strain else None
        if chromosome is not None:
            sequence.chromosome = chromosome.strip() if chromosome else None
        if start_position is not None:
            sequence.start_position = start_position
        if end_position is not None:
            sequence.end_position = end_position
        if length is not None:
            sequence.length = length
        if gc_content is not None:
            sequence.gc_content = gc_content
        if n50 is not None:
            sequence.n50 = n50
        if scaffold_count is not None:
            sequence.scaffold_count = scaffold_count
        if source is not None:
            sequence.source = source.strip() if source else None
        if assembly_level is not None:
            sequence.assembly_level = assembly_level.strip() if assembly_level else None
        if genome_build is not None:
            sequence.genome_build = genome_build.strip() if genome_build else None
        if tags is not None:
            sequence.tags = tags

        sequence.updated_at = datetime.now(UTC)
        return await self.sequence_repo.update(sequence)


class DeleteSequenceUseCase:
    def __init__(self, sequence_repo: SequenceRepositoryInterface):
        self.sequence_repo = sequence_repo

    async def execute(self, sequence_id: str, user_id: str) -> bool:
        sequence = await self.sequence_repo.get_by_id(sequence_id)
        if not sequence:
            raise NotFoundException("Sequence", sequence_id)

        if str(sequence.created_by) != user_id:
            raise ValidationException("Only the creator can delete this sequence")

        return await self.sequence_repo.delete(sequence_id)


class CreateVariantUseCase:
    def __init__(
        self,
        variant_repo: VariantRepositoryInterface,
        sequence_repo: SequenceRepositoryInterface,
    ):
        self.variant_repo = variant_repo
        self.sequence_repo = sequence_repo

    async def execute(
        self,
        sequence_id: str,
        chromosome: str,
        position: int,
        reference_allele: str,
        alternate_allele: str,
        variant_type: str,
        user_id: str,
        quality: float | None = None,
        filter_status: str | None = None,
        depth: int | None = None,
        allele_frequency: float | None = None,
        gene_name: str | None = None,
        impact: str | None = None,
        annotations: dict | None = None,
        tags: list[str] | None = None,
    ) -> VariantModel:
        sequence = await self.sequence_repo.get_by_id(sequence_id)
        if not sequence:
            raise NotFoundException("Sequence", sequence_id)

        if not chromosome or not chromosome.strip():
            raise ValidationException("Chromosome is required")
        if position < 0:
            raise ValidationException("Position must be non-negative")
        if not reference_allele or not reference_allele.strip():
            raise ValidationException("Reference allele is required")
        if not alternate_allele or not alternate_allele.strip():
            raise ValidationException("Alternate allele is required")

        valid_types = ("SNP", "indel", "structural", "CNV", "MNV")
        if variant_type not in valid_types:
            raise ValidationException(f"Invalid variant type. Must be one of: {', '.join(valid_types)}")

        if allele_frequency is not None and (allele_frequency < 0 or allele_frequency > 1):
            raise ValidationException("Allele frequency must be between 0 and 1")

        variant = VariantModel(
            sequence_id=sequence_id,
            chromosome=chromosome.strip(),
            position=position,
            reference_allele=reference_allele.strip(),
            alternate_allele=alternate_allele.strip(),
            variant_type=variant_type,
            quality=quality,
            filter_status=filter_status.strip() if filter_status else None,
            depth=depth,
            allele_frequency=allele_frequency,
            gene_name=gene_name.strip() if gene_name else None,
            impact=impact.strip() if impact else None,
            annotations=annotations,
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.variant_repo.create(variant)


class BulkCreateVariantsUseCase:
    def __init__(
        self,
        variant_repo: VariantRepositoryInterface,
        sequence_repo: SequenceRepositoryInterface,
    ):
        self.variant_repo = variant_repo
        self.sequence_repo = sequence_repo

    async def execute(
        self,
        sequence_id: str,
        variants_data: list[dict],
        user_id: str,
    ) -> list[VariantModel]:
        sequence = await self.sequence_repo.get_by_id(sequence_id)
        if not sequence:
            raise NotFoundException("Sequence", sequence_id)

        if not variants_data:
            raise ValidationException("Variants data cannot be empty")

        valid_types = ("SNP", "indel", "structural", "CNV", "MNV")
        variants = []
        for v in variants_data:
            if "chromosome" not in v or "position" not in v:
                raise ValidationException("Each variant must have chromosome and position")
            if "reference_allele" not in v or "alternate_allele" not in v:
                raise ValidationException("Each variant must have reference_allele and alternate_allele")
            if "variant_type" not in v:
                raise ValidationException("Each variant must have variant_type")
            if v["variant_type"] not in valid_types:
                raise ValidationException(f"Invalid variant type: {v['variant_type']}")

            variant = VariantModel(
                sequence_id=sequence_id,
                chromosome=v["chromosome"],
                position=v["position"],
                reference_allele=v["reference_allele"],
                alternate_allele=v["alternate_allele"],
                variant_type=v["variant_type"],
                quality=v.get("quality"),
                filter_status=v.get("filter_status"),
                depth=v.get("depth"),
                allele_frequency=v.get("allele_frequency"),
                gene_name=v.get("gene_name"),
                impact=v.get("impact"),
                annotations=v.get("annotations"),
                tags=v.get("tags"),
                created_by=user_id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            variants.append(variant)

        return await self.variant_repo.bulk_create(variants)


class GetVariantUseCase:
    def __init__(self, variant_repo: VariantRepositoryInterface):
        self.variant_repo = variant_repo

    async def execute(self, variant_id: str) -> VariantModel:
        variant = await self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise NotFoundException("Variant", variant_id)
        return variant


class ListVariantsUseCase:
    def __init__(self, variant_repo: VariantRepositoryInterface):
        self.variant_repo = variant_repo

    async def execute(
        self,
        sequence_id: str,
        skip: int = 0,
        limit: int = 100,
        chromosome: str | None = None,
        variant_type: str | None = None,
        gene_name: str | None = None,
    ) -> dict:
        variants = await self.variant_repo.list_by_sequence(
            sequence_id=sequence_id,
            skip=skip,
            limit=limit,
            chromosome=chromosome,
            variant_type=variant_type,
            gene_name=gene_name,
        )
        total = await self.variant_repo.count_by_sequence(
            sequence_id=sequence_id,
            chromosome=chromosome,
            variant_type=variant_type,
            gene_name=gene_name,
        )

        return {
            "items": [
                {
                    "id": str(v.id),
                    "sequence_id": str(v.sequence_id),
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
                    "tags": v.tags,
                    "created_by": str(v.created_by),
                    "created_at": v.created_at.isoformat(),
                    "updated_at": v.updated_at.isoformat(),
                }
                for v in variants
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class SearchVariantsUseCase:
    def __init__(self, variant_repo: VariantRepositoryInterface):
        self.variant_repo = variant_repo

    async def execute(
        self,
        sequence_id: str,
        chromosome: str | None = None,
        start: int | None = None,
        end: int | None = None,
        variant_type: str | None = None,
        gene_name: str | None = None,
        min_quality: float | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        variants = await self.variant_repo.search(
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

        return {
            "items": [
                {
                    "id": str(v.id),
                    "sequence_id": str(v.sequence_id),
                    "chromosome": v.chromosome,
                    "position": v.position,
                    "reference_allele": v.reference_allele,
                    "alternate_allele": v.alternate_allele,
                    "variant_type": v.variant_type,
                    "quality": v.quality,
                    "depth": v.depth,
                    "allele_frequency": v.allele_frequency,
                    "gene_name": v.gene_name,
                    "impact": v.impact,
                    "created_at": v.created_at.isoformat(),
                }
                for v in variants
            ],
            "total": len(variants),
            "skip": skip,
            "limit": limit,
        }


class DeleteVariantUseCase:
    def __init__(self, variant_repo: VariantRepositoryInterface):
        self.variant_repo = variant_repo

    async def execute(self, variant_id: str) -> bool:
        variant = await self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise NotFoundException("Variant", variant_id)

        return await self.variant_repo.delete(variant_id)


class CreateAnnotationUseCase:
    def __init__(
        self,
        annotation_repo: GeneAnnotationRepositoryInterface,
        sequence_repo: SequenceRepositoryInterface,
    ):
        self.annotation_repo = annotation_repo
        self.sequence_repo = sequence_repo

    async def execute(
        self,
        sequence_id: str,
        gene_symbol: str,
        user_id: str,
        gene_name: str | None = None,
        description: str | None = None,
        chromosome: str | None = None,
        start_position: int | None = None,
        end_position: int | None = None,
        strand: str | None = None,
        biotype: str | None = None,
        go_terms: list[str] | None = None,
        pfam_domains: list[str] | None = None,
        kegg_pathways: list[str] | None = None,
        orthologs: dict | None = None,
        expression_data: dict | None = None,
    ) -> GeneAnnotationModel:
        sequence = await self.sequence_repo.get_by_id(sequence_id)
        if not sequence:
            raise NotFoundException("Sequence", sequence_id)

        if not gene_symbol or not gene_symbol.strip():
            raise ValidationException("Gene symbol is required")

        existing = await self.annotation_repo.search_by_gene(sequence_id, gene_symbol.strip())
        if existing:
            raise ConflictException(f"Annotation for gene '{gene_symbol}' already exists in this sequence")

        if strand is not None and strand not in ("+", "-", "1", "-1"):
            raise ValidationException("Strand must be '+', '-', '1', or '-1'")

        annotation = GeneAnnotationModel(
            sequence_id=sequence_id,
            gene_symbol=gene_symbol.strip(),
            gene_name=gene_name.strip() if gene_name else None,
            description=description.strip() if description else None,
            chromosome=chromosome.strip() if chromosome else None,
            start_position=start_position,
            end_position=end_position,
            strand=strand,
            biotype=biotype.strip() if biotype else None,
            go_terms=go_terms,
            pfam_domains=pfam_domains,
            kegg_pathways=kegg_pathways,
            orthologs=orthologs,
            expression_data=expression_data,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.annotation_repo.create(annotation)


class GetAnnotationUseCase:
    def __init__(self, annotation_repo: GeneAnnotationRepositoryInterface):
        self.annotation_repo = annotation_repo

    async def execute(self, annotation_id: str) -> GeneAnnotationModel:
        annotation = await self.annotation_repo.get_by_id(annotation_id)
        if not annotation:
            raise NotFoundException("Gene annotation", annotation_id)
        return annotation


class ListAnnotationsUseCase:
    def __init__(self, annotation_repo: GeneAnnotationRepositoryInterface):
        self.annotation_repo = annotation_repo

    async def execute(
        self,
        sequence_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> dict:
        annotations = await self.annotation_repo.list_by_sequence(
            sequence_id=sequence_id,
            skip=skip,
            limit=limit,
            search=search,
        )
        total = await self.annotation_repo.count_by_sequence(
            sequence_id=sequence_id,
            search=search,
        )

        return {
            "items": [
                {
                    "id": str(a.id),
                    "sequence_id": str(a.sequence_id),
                    "gene_symbol": a.gene_symbol,
                    "gene_name": a.gene_name,
                    "description": a.description,
                    "chromosome": a.chromosome,
                    "start_position": a.start_position,
                    "end_position": a.end_position,
                    "strand": a.strand,
                    "biotype": a.biotype,
                    "go_terms": a.go_terms,
                    "pfam_domains": a.pfam_domains,
                    "kegg_pathways": a.kegg_pathways,
                    "created_by": str(a.created_by),
                    "created_at": a.created_at.isoformat(),
                    "updated_at": a.updated_at.isoformat(),
                }
                for a in annotations
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateAnnotationUseCase:
    def __init__(self, annotation_repo: GeneAnnotationRepositoryInterface):
        self.annotation_repo = annotation_repo

    async def execute(
        self,
        annotation_id: str,
        gene_name: str | None = None,
        description: str | None = None,
        chromosome: str | None = None,
        start_position: int | None = None,
        end_position: int | None = None,
        strand: str | None = None,
        biotype: str | None = None,
        go_terms: list[str] | None = None,
        pfam_domains: list[str] | None = None,
        kegg_pathways: list[str] | None = None,
        orthologs: dict | None = None,
        expression_data: dict | None = None,
    ) -> GeneAnnotationModel:
        annotation = await self.annotation_repo.get_by_id(annotation_id)
        if not annotation:
            raise NotFoundException("Gene annotation", annotation_id)

        if gene_name is not None:
            annotation.gene_name = gene_name.strip() if gene_name else None
        if description is not None:
            annotation.description = description.strip() if description else None
        if chromosome is not None:
            annotation.chromosome = chromosome.strip() if chromosome else None
        if start_position is not None:
            annotation.start_position = start_position
        if end_position is not None:
            annotation.end_position = end_position
        if strand is not None:
            annotation.strand = strand
        if biotype is not None:
            annotation.biotype = biotype.strip() if biotype else None
        if go_terms is not None:
            annotation.go_terms = go_terms
        if pfam_domains is not None:
            annotation.pfam_domains = pfam_domains
        if kegg_pathways is not None:
            annotation.kegg_pathways = kegg_pathways
        if orthologs is not None:
            annotation.orthologs = orthologs
        if expression_data is not None:
            annotation.expression_data = expression_data

        annotation.updated_at = datetime.now(UTC)
        return await self.annotation_repo.update(annotation)


class DeleteAnnotationUseCase:
    def __init__(self, annotation_repo: GeneAnnotationRepositoryInterface):
        self.annotation_repo = annotation_repo

    async def execute(self, annotation_id: str) -> bool:
        annotation = await self.annotation_repo.get_by_id(annotation_id)
        if not annotation:
            raise NotFoundException("Gene annotation", annotation_id)

        return await self.annotation_repo.delete(annotation_id)
