from datetime import UTC, datetime

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.molecular.domain.interfaces import (
    ConstructRepositoryInterface,
    MoleculeExperimentRepositoryInterface,
    PrimerRepositoryInterface,
)
from app.modules.molecular.domain.models import (
    ConstructModel,
    MoleculeExperimentModel,
    PrimerModel,
)


class CreateMoleculeExperimentUseCase:
    def __init__(self, experiment_repo: MoleculeExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        name: str,
        user_id: str,
        description: str | None = None,
        experiment_type: str = "PCR",
        project_id: str | None = None,
        species_id: str | None = None,
        protocol: str | None = None,
        start_date=None,
        end_date=None,
        notes: str | None = None,
        tags: list[str] | None = None,
    ) -> MoleculeExperimentModel:
        if not name or not name.strip():
            raise ValidationException("Experiment name is required")
        if len(name.strip()) > 255:
            raise ValidationException("Experiment name must be less than 255 characters")

        valid_types = (
            "PCR", "qPCR", "RT-PCR", "RNA-Seq", "DNA_Extraction",
            "RNA_Extraction", "ChIP-Seq", "ATAC-Seq", "Proteomics",
            "Metabolomics", "CRISPR", "Transformation", "Cloning",
        )
        if experiment_type not in valid_types:
            raise ValidationException(f"Invalid experiment type. Must be one of: {', '.join(valid_types)}")

        if start_date and end_date and end_date < start_date:
            raise ValidationException("End date must be after start date")

        experiment = MoleculeExperimentModel(
            name=name.strip(),
            description=description.strip() if description else None,
            experiment_type=experiment_type,
            project_id=project_id,
            species_id=species_id,
            protocol=protocol.strip() if protocol else None,
            status="planned",
            start_date=start_date,
            end_date=end_date,
            notes=notes.strip() if notes else None,
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.experiment_repo.create(experiment)


class GetMoleculeExperimentUseCase:
    def __init__(self, experiment_repo: MoleculeExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(self, experiment_id: str) -> MoleculeExperimentModel:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Molecular experiment", experiment_id)
        return experiment


class ListMoleculeExperimentsUseCase:
    def __init__(self, experiment_repo: MoleculeExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        experiment_type: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        experiments = await self.experiment_repo.list_experiments(
            skip=skip,
            limit=limit,
            experiment_type=experiment_type,
            project_id=project_id,
            status=status,
            search=search,
            user_id=user_id,
        )
        total = await self.experiment_repo.count_experiments(
            experiment_type=experiment_type,
            project_id=project_id,
            status=status,
            search=search,
            user_id=user_id,
        )

        return {
            "items": [
                {
                    "id": str(e.id),
                    "name": e.name,
                    "description": e.description,
                    "experiment_type": e.experiment_type,
                    "project_id": str(e.project_id) if e.project_id else None,
                    "species_id": str(e.species_id) if e.species_id else None,
                    "status": e.status,
                    "start_date": e.start_date.isoformat() if e.start_date else None,
                    "end_date": e.end_date.isoformat() if e.end_date else None,
                    "tags": e.tags,
                    "created_by": str(e.created_by),
                    "created_at": e.created_at.isoformat(),
                    "updated_at": e.updated_at.isoformat(),
                }
                for e in experiments
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateMoleculeExperimentUseCase:
    def __init__(self, experiment_repo: MoleculeExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        experiment_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        experiment_type: str | None = None,
        protocol: str | None = None,
        start_date=None,
        end_date=None,
        status: str | None = None,
        result_summary: str | None = None,
        notes: str | None = None,
        tags: list[str] | None = None,
    ) -> MoleculeExperimentModel:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Molecular experiment", experiment_id)

        if str(experiment.created_by) != user_id:
            raise ValidationException("Only the creator can update this experiment")

        if name is not None:
            if not name.strip():
                raise ValidationException("Experiment name cannot be empty")
            experiment.name = name.strip()
        if description is not None:
            experiment.description = description.strip() if description else None
        if experiment_type is not None:
            valid_types = (
                "PCR", "qPCR", "RT-PCR", "RNA-Seq", "DNA_Extraction",
                "RNA_Extraction", "ChIP-Seq", "ATAC-Seq", "Proteomics",
                "Metabolomics", "CRISPR", "Transformation", "Cloning",
            )
            if experiment_type not in valid_types:
                raise ValidationException("Invalid experiment type")
            experiment.experiment_type = experiment_type
        if protocol is not None:
            experiment.protocol = protocol.strip() if protocol else None
        if start_date is not None:
            experiment.start_date = start_date
        if end_date is not None:
            experiment.end_date = end_date
        if status is not None:
            valid_statuses = ("planned", "in_progress", "completed", "archived")
            if status not in valid_statuses:
                raise ValidationException("Invalid status")
            experiment.status = status
        if result_summary is not None:
            experiment.result_summary = result_summary.strip() if result_summary else None
        if notes is not None:
            experiment.notes = notes.strip() if notes else None
        if tags is not None:
            experiment.tags = tags

        experiment.updated_at = datetime.now(UTC)
        return await self.experiment_repo.update(experiment)


class DeleteMoleculeExperimentUseCase:
    def __init__(self, experiment_repo: MoleculeExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(self, experiment_id: str, user_id: str) -> bool:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Molecular experiment", experiment_id)

        if str(experiment.created_by) != user_id:
            raise ValidationException("Only the creator can delete this experiment")

        return await self.experiment_repo.delete(experiment_id)


class CreatePrimerUseCase:
    def __init__(
        self,
        primer_repo: PrimerRepositoryInterface,
        experiment_repo: MoleculeExperimentRepositoryInterface,
    ):
        self.primer_repo = primer_repo
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        experiment_id: str,
        name: str,
        sequence: str,
        user_id: str,
        description: str | None = None,
        primer_type: str = "forward",
        target_gene: str | None = None,
        target_organism: str | None = None,
        tm: float | None = None,
        amplicon_size: int | None = None,
        notes: str | None = None,
    ) -> PrimerModel:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Molecular experiment", experiment_id)

        if not name or not name.strip():
            raise ValidationException("Primer name is required")
        if not sequence or not sequence.strip():
            raise ValidationException("Primer sequence is required")

        valid_sequence_chars = set("ATCGNatcgn")
        cleaned_seq = sequence.strip().upper()
        if not all(c in valid_sequence_chars for c in cleaned_seq):
            raise ValidationException("Primer sequence can only contain A, T, C, G, N")

        valid_types = ("forward", "reverse", "probe", "nested", "universal")
        if primer_type not in valid_types:
            raise ValidationException(f"Invalid primer type. Must be one of: {', '.join(valid_types)}")

        if tm is not None and (tm < 0 or tm > 100):
            raise ValidationException("Melting temperature must be between 0 and 100")

        primer = PrimerModel(
            experiment_id=experiment_id,
            name=name.strip(),
            description=description.strip() if description else None,
            sequence=cleaned_seq,
            primer_type=primer_type,
            target_gene=target_gene.strip() if target_gene else None,
            target_organism=target_organism.strip() if target_organism else None,
            length=len(cleaned_seq),
            tm=tm,
            gc_percent=round((cleaned_seq.count("G") + cleaned_seq.count("C")) / len(cleaned_seq) * 100, 2),
            amplicon_size=amplicon_size,
            notes=notes.strip() if notes else None,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.primer_repo.create(primer)


class GetPrimerUseCase:
    def __init__(self, primer_repo: PrimerRepositoryInterface):
        self.primer_repo = primer_repo

    async def execute(self, primer_id: str) -> PrimerModel:
        primer = await self.primer_repo.get_by_id(primer_id)
        if not primer:
            raise NotFoundException("Primer", primer_id)
        return primer


class ListPrimersUseCase:
    def __init__(self, primer_repo: PrimerRepositoryInterface):
        self.primer_repo = primer_repo

    async def execute(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        primer_type: str | None = None,
        search: str | None = None,
    ) -> dict:
        primers = await self.primer_repo.list_by_experiment(
            experiment_id=experiment_id,
            skip=skip,
            limit=limit,
            primer_type=primer_type,
            search=search,
        )
        total = await self.primer_repo.count_by_experiment(
            experiment_id=experiment_id,
            primer_type=primer_type,
            search=search,
        )

        return {
            "items": [
                {
                    "id": str(p.id),
                    "experiment_id": str(p.experiment_id),
                    "name": p.name,
                    "description": p.description,
                    "sequence": p.sequence,
                    "primer_type": p.primer_type,
                    "target_gene": p.target_gene,
                    "target_organism": p.target_organism,
                    "length": p.length,
                    "tm": p.tm,
                    "gc_percent": p.gc_percent,
                    "amplicon_size": p.amplicon_size,
                    "is_validated": p.is_validated,
                    "created_by": str(p.created_by),
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in primers
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdatePrimerUseCase:
    def __init__(self, primer_repo: PrimerRepositoryInterface):
        self.primer_repo = primer_repo

    async def execute(
        self,
        primer_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        sequence: str | None = None,
        primer_type: str | None = None,
        target_gene: str | None = None,
        target_organism: str | None = None,
        tm: float | None = None,
        amplicon_size: int | None = None,
        is_validated: bool | None = None,
        notes: str | None = None,
    ) -> PrimerModel:
        primer = await self.primer_repo.get_by_id(primer_id)
        if not primer:
            raise NotFoundException("Primer", primer_id)

        if str(primer.created_by) != user_id:
            raise ValidationException("Only the creator can update this primer")

        if name is not None:
            if not name.strip():
                raise ValidationException("Primer name cannot be empty")
            primer.name = name.strip()
        if description is not None:
            primer.description = description.strip() if description else None
        if sequence is not None:
            cleaned_seq = sequence.strip().upper()
            valid_chars = set("ATCGNatcgn")
            if not all(c in valid_chars for c in cleaned_seq):
                raise ValidationException("Primer sequence can only contain A, T, C, G, N")
            primer.sequence = cleaned_seq
            primer.length = len(cleaned_seq)
            primer.gc_percent = round((cleaned_seq.count("G") + cleaned_seq.count("C")) / len(cleaned_seq) * 100, 2)
        if primer_type is not None:
            valid_types = ("forward", "reverse", "probe", "nested", "universal")
            if primer_type not in valid_types:
                raise ValidationException("Invalid primer type")
            primer.primer_type = primer_type
        if target_gene is not None:
            primer.target_gene = target_gene.strip() if target_gene else None
        if target_organism is not None:
            primer.target_organism = target_organism.strip() if target_organism else None
        if tm is not None:
            primer.tm = tm
        if amplicon_size is not None:
            primer.amplicon_size = amplicon_size
        if is_validated is not None:
            primer.is_validated = is_validated
        if notes is not None:
            primer.notes = notes.strip() if notes else None

        primer.updated_at = datetime.now(UTC)
        return await self.primer_repo.update(primer)


class DeletePrimerUseCase:
    def __init__(self, primer_repo: PrimerRepositoryInterface):
        self.primer_repo = primer_repo

    async def execute(self, primer_id: str, user_id: str) -> bool:
        primer = await self.primer_repo.get_by_id(primer_id)
        if not primer:
            raise NotFoundException("Primer", primer_id)

        if str(primer.created_by) != user_id:
            raise ValidationException("Only the creator can delete this primer")

        return await self.primer_repo.delete(primer_id)


class CreateConstructUseCase:
    def __init__(
        self,
        construct_repo: ConstructRepositoryInterface,
        experiment_repo: MoleculeExperimentRepositoryInterface,
    ):
        self.construct_repo = construct_repo
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        experiment_id: str,
        name: str,
        user_id: str,
        description: str | None = None,
        construct_type: str = "plasmid",
        vector_backbone: str | None = None,
        insert_sequence: str | None = None,
        insert_name: str | None = None,
        selection_marker: str | None = None,
        promoter: str | None = None,
        resistance: str | None = None,
        species_id: str | None = None,
        notes: str | None = None,
        tags: list[str] | None = None,
    ) -> ConstructModel:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Molecular experiment", experiment_id)

        if not name or not name.strip():
            raise ValidationException("Construct name is required")

        valid_types = ("plasmid", "binary_vector", "expression_construct", "reporter", "crispr_construct")
        if construct_type not in valid_types:
            raise ValidationException(f"Invalid construct type. Must be one of: {', '.join(valid_types)}")

        insert_size = len(insert_sequence.strip()) if insert_sequence else None

        construct = ConstructModel(
            experiment_id=experiment_id,
            name=name.strip(),
            description=description.strip() if description else None,
            construct_type=construct_type,
            vector_backbone=vector_backbone.strip() if vector_backbone else None,
            insert_sequence=insert_sequence.strip() if insert_sequence else None,
            insert_name=insert_name.strip() if insert_name else None,
            insert_size=insert_size,
            selection_marker=selection_marker.strip() if selection_marker else None,
            promoter=promoter.strip() if promoter else None,
            resistance=resistance.strip() if resistance else None,
            species_id=species_id,
            notes=notes.strip() if notes else None,
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.construct_repo.create(construct)


class GetConstructUseCase:
    def __init__(self, construct_repo: ConstructRepositoryInterface):
        self.construct_repo = construct_repo

    async def execute(self, construct_id: str) -> ConstructModel:
        construct = await self.construct_repo.get_by_id(construct_id)
        if not construct:
            raise NotFoundException("Construct", construct_id)
        return construct


class ListConstructsUseCase:
    def __init__(self, construct_repo: ConstructRepositoryInterface):
        self.construct_repo = construct_repo

    async def execute(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        construct_type: str | None = None,
        search: str | None = None,
    ) -> dict:
        constructs = await self.construct_repo.list_by_experiment(
            experiment_id=experiment_id,
            skip=skip,
            limit=limit,
            construct_type=construct_type,
            search=search,
        )
        total = await self.construct_repo.count_by_experiment(
            experiment_id=experiment_id,
            construct_type=construct_type,
            search=search,
        )

        return {
            "items": [
                {
                    "id": str(c.id),
                    "experiment_id": str(c.experiment_id),
                    "name": c.name,
                    "description": c.description,
                    "construct_type": c.construct_type,
                    "vector_backbone": c.vector_backbone,
                    "insert_name": c.insert_name,
                    "insert_size": c.insert_size,
                    "selection_marker": c.selection_marker,
                    "promoter": c.promoter,
                    "resistance": c.resistance,
                    "is_validated": c.is_validated,
                    "tags": c.tags,
                    "created_by": str(c.created_by),
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                }
                for c in constructs
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateConstructUseCase:
    def __init__(self, construct_repo: ConstructRepositoryInterface):
        self.construct_repo = construct_repo

    async def execute(
        self,
        construct_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        construct_type: str | None = None,
        vector_backbone: str | None = None,
        insert_sequence: str | None = None,
        insert_name: str | None = None,
        selection_marker: str | None = None,
        promoter: str | None = None,
        resistance: str | None = None,
        is_validated: bool | None = None,
        notes: str | None = None,
        tags: list[str] | None = None,
    ) -> ConstructModel:
        construct = await self.construct_repo.get_by_id(construct_id)
        if not construct:
            raise NotFoundException("Construct", construct_id)

        if str(construct.created_by) != user_id:
            raise ValidationException("Only the creator can update this construct")

        if name is not None:
            if not name.strip():
                raise ValidationException("Construct name cannot be empty")
            construct.name = name.strip()
        if description is not None:
            construct.description = description.strip() if description else None
        if construct_type is not None:
            valid_types = ("plasmid", "binary_vector", "expression_construct", "reporter", "crispr_construct")
            if construct_type not in valid_types:
                raise ValidationException("Invalid construct type")
            construct.construct_type = construct_type
        if vector_backbone is not None:
            construct.vector_backbone = vector_backbone.strip() if vector_backbone else None
        if insert_sequence is not None:
            construct.insert_sequence = insert_sequence.strip() if insert_sequence else None
            construct.insert_size = len(insert_sequence.strip()) if insert_sequence else None
        if insert_name is not None:
            construct.insert_name = insert_name.strip() if insert_name else None
        if selection_marker is not None:
            construct.selection_marker = selection_marker.strip() if selection_marker else None
        if promoter is not None:
            construct.promoter = promoter.strip() if promoter else None
        if resistance is not None:
            construct.resistance = resistance.strip() if resistance else None
        if is_validated is not None:
            construct.is_validated = is_validated
        if notes is not None:
            construct.notes = notes.strip() if notes else None
        if tags is not None:
            construct.tags = tags

        construct.updated_at = datetime.now(UTC)
        return await self.construct_repo.update(construct)


class DeleteConstructUseCase:
    def __init__(self, construct_repo: ConstructRepositoryInterface):
        self.construct_repo = construct_repo

    async def execute(self, construct_id: str, user_id: str) -> bool:
        construct = await self.construct_repo.get_by_id(construct_id)
        if not construct:
            raise NotFoundException("Construct", construct_id)

        if str(construct.created_by) != user_id:
            raise ValidationException("Only the creator can delete this construct")

        return await self.construct_repo.delete(construct_id)
