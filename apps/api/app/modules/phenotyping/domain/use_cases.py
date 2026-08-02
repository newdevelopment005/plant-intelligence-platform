from datetime import UTC, datetime

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.phenotyping.domain.interfaces import (
    ExperimentRepositoryInterface,
    MeasurementRepositoryInterface,
    TraitRepositoryInterface,
)
from app.modules.phenotyping.domain.models import (
    ExperimentModel,
    MeasurementModel,
    TraitModel,
)


class CreateExperimentUseCase:
    def __init__(self, experiment_repo: ExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        name: str,
        user_id: str,
        description: str | None = None,
        experiment_type: str = "field",
        project_id: str | None = None,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        altitude: float | None = None,
        start_date=None,
        end_date=None,
        tags: list[str] | None = None,
    ) -> ExperimentModel:
        if not name or not name.strip():
            raise ValidationException("Experiment name is required")
        if len(name.strip()) > 255:
            raise ValidationException("Experiment name must be less than 255 characters")

        valid_types = ("field", "greenhouse", "controlled_environment", "growth_chamber")
        if experiment_type not in valid_types:
            raise ValidationException(f"Invalid experiment type. Must be one of: {', '.join(valid_types)}")

        if start_date and end_date and end_date < start_date:
            raise ValidationException("End date must be after start date")

        experiment = ExperimentModel(
            name=name.strip(),
            description=description.strip() if description else None,
            experiment_type=experiment_type,
            project_id=project_id,
            location=location.strip() if location else None,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            start_date=start_date,
            end_date=end_date,
            status="planned",
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.experiment_repo.create(experiment)


class GetExperimentUseCase:
    def __init__(self, experiment_repo: ExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(self, experiment_id: str) -> ExperimentModel:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Experiment", experiment_id)
        return experiment


class ListExperimentsUseCase:
    def __init__(self, experiment_repo: ExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        experiments = await self.experiment_repo.list_experiments(
            skip=skip,
            limit=limit,
            project_id=project_id,
            status=status,
            search=search,
            user_id=user_id,
        )
        total = await self.experiment_repo.count_experiments(
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
                    "location": e.location,
                    "latitude": e.latitude,
                    "longitude": e.longitude,
                    "start_date": e.start_date.isoformat() if e.start_date else None,
                    "end_date": e.end_date.isoformat() if e.end_date else None,
                    "status": e.status,
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


class UpdateExperimentUseCase:
    def __init__(self, experiment_repo: ExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        experiment_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        experiment_type: str | None = None,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        altitude: float | None = None,
        start_date=None,
        end_date=None,
        status: str | None = None,
        tags: list[str] | None = None,
    ) -> ExperimentModel:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Experiment", experiment_id)

        if str(experiment.created_by) != user_id:
            raise ValidationException("Only the creator can update this experiment")

        if name is not None:
            if not name.strip():
                raise ValidationException("Experiment name cannot be empty")
            experiment.name = name.strip()
        if description is not None:
            experiment.description = description.strip() if description else None
        if experiment_type is not None:
            valid_types = ("field", "greenhouse", "controlled_environment", "growth_chamber")
            if experiment_type not in valid_types:
                raise ValidationException(f"Invalid experiment type. Must be one of: {', '.join(valid_types)}")
            experiment.experiment_type = experiment_type
        if location is not None:
            experiment.location = location.strip() if location else None
        if latitude is not None:
            experiment.latitude = latitude
        if longitude is not None:
            experiment.longitude = longitude
        if altitude is not None:
            experiment.altitude = altitude
        if start_date is not None:
            experiment.start_date = start_date
        if end_date is not None:
            experiment.end_date = end_date
        if status is not None:
            valid_statuses = ("planned", "in_progress", "completed", "archived")
            if status not in valid_statuses:
                raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            experiment.status = status
        if tags is not None:
            experiment.tags = tags

        experiment.updated_at = datetime.now(UTC)
        return await self.experiment_repo.update(experiment)


class DeleteExperimentUseCase:
    def __init__(self, experiment_repo: ExperimentRepositoryInterface):
        self.experiment_repo = experiment_repo

    async def execute(self, experiment_id: str, user_id: str) -> bool:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Experiment", experiment_id)

        if str(experiment.created_by) != user_id:
            raise ValidationException("Only the creator can delete this experiment")

        return await self.experiment_repo.delete(experiment_id)


class CreateTraitUseCase:
    def __init__(
        self,
        trait_repo: TraitRepositoryInterface,
        experiment_repo: ExperimentRepositoryInterface,
    ):
        self.trait_repo = trait_repo
        self.experiment_repo = experiment_repo

    async def execute(
        self,
        experiment_id: str,
        name: str,
        description: str | None = None,
        trait_category: str | None = None,
        unit: str | None = None,
        data_type: str = "numeric",
        min_value: float | None = None,
        max_value: float | None = None,
        allowed_values: list[str] | None = None,
        is_required: bool = False,
    ) -> TraitModel:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Experiment", experiment_id)

        if not name or not name.strip():
            raise ValidationException("Trait name is required")
        if len(name.strip()) > 255:
            raise ValidationException("Trait name must be less than 255 characters")

        valid_data_types = ("numeric", "text", "categorical", "date", "boolean")
        if data_type not in valid_data_types:
            raise ValidationException(f"Invalid data type. Must be one of: {', '.join(valid_data_types)}")

        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValidationException("Min value cannot be greater than max value")

        trait = TraitModel(
            experiment_id=experiment_id,
            name=name.strip(),
            description=description.strip() if description else None,
            trait_category=trait_category.strip() if trait_category else None,
            unit=unit.strip() if unit else None,
            data_type=data_type,
            min_value=min_value,
            max_value=max_value,
            allowed_values=allowed_values,
            is_required=is_required,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.trait_repo.create(trait)


class GetTraitUseCase:
    def __init__(self, trait_repo: TraitRepositoryInterface):
        self.trait_repo = trait_repo

    async def execute(self, trait_id: str) -> TraitModel:
        trait = await self.trait_repo.get_by_id(trait_id)
        if not trait:
            raise NotFoundException("Trait", trait_id)
        return trait


class ListTraitsUseCase:
    def __init__(self, trait_repo: TraitRepositoryInterface):
        self.trait_repo = trait_repo

    async def execute(
        self, experiment_id: str, skip: int = 0, limit: int = 100
    ) -> dict:
        traits = await self.trait_repo.list_by_experiment(
            experiment_id, skip=skip, limit=limit
        )
        total = await self.trait_repo.count_by_experiment(experiment_id)

        return {
            "items": [
                {
                    "id": str(t.id),
                    "experiment_id": str(t.experiment_id),
                    "name": t.name,
                    "description": t.description,
                    "trait_category": t.trait_category,
                    "unit": t.unit,
                    "data_type": t.data_type,
                    "min_value": t.min_value,
                    "max_value": t.max_value,
                    "allowed_values": t.allowed_values,
                    "is_required": t.is_required,
                    "created_at": t.created_at.isoformat(),
                    "updated_at": t.updated_at.isoformat(),
                }
                for t in traits
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateTraitUseCase:
    def __init__(self, trait_repo: TraitRepositoryInterface):
        self.trait_repo = trait_repo

    async def execute(
        self,
        trait_id: str,
        name: str | None = None,
        description: str | None = None,
        trait_category: str | None = None,
        unit: str | None = None,
        data_type: str | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        allowed_values: list[str] | None = None,
        is_required: bool | None = None,
    ) -> TraitModel:
        trait = await self.trait_repo.get_by_id(trait_id)
        if not trait:
            raise NotFoundException("Trait", trait_id)

        if name is not None:
            if not name.strip():
                raise ValidationException("Trait name cannot be empty")
            trait.name = name.strip()
        if description is not None:
            trait.description = description.strip() if description else None
        if trait_category is not None:
            trait.trait_category = trait_category.strip() if trait_category else None
        if unit is not None:
            trait.unit = unit.strip() if unit else None
        if data_type is not None:
            valid_data_types = ("numeric", "text", "categorical", "date", "boolean")
            if data_type not in valid_data_types:
                raise ValidationException(f"Invalid data type. Must be one of: {', '.join(valid_data_types)}")
            trait.data_type = data_type
        if min_value is not None:
            trait.min_value = min_value
        if max_value is not None:
            trait.max_value = max_value
        if allowed_values is not None:
            trait.allowed_values = allowed_values
        if is_required is not None:
            trait.is_required = is_required

        trait.updated_at = datetime.now(UTC)
        return await self.trait_repo.update(trait)


class DeleteTraitUseCase:
    def __init__(self, trait_repo: TraitRepositoryInterface):
        self.trait_repo = trait_repo

    async def execute(self, trait_id: str) -> bool:
        trait = await self.trait_repo.get_by_id(trait_id)
        if not trait:
            raise NotFoundException("Trait", trait_id)

        return await self.trait_repo.delete(trait_id)


class CreateMeasurementUseCase:
    def __init__(
        self,
        measurement_repo: MeasurementRepositoryInterface,
        experiment_repo: ExperimentRepositoryInterface,
        trait_repo: TraitRepositoryInterface,
    ):
        self.measurement_repo = measurement_repo
        self.experiment_repo = experiment_repo
        self.trait_repo = trait_repo

    async def execute(
        self,
        experiment_id: str,
        trait_id: str,
        value_numeric: float | None = None,
        value_text: str | None = None,
        value_date=None,
        accession_id: str | None = None,
        rep: int | None = None,
        block: str | None = None,
        plot: str | None = None,
        plant_id: str | None = None,
        notes: str | None = None,
        measured_at=None,
        measured_by: str | None = None,
        image_url: str | None = None,
    ) -> MeasurementModel:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Experiment", experiment_id)

        trait = await self.trait_repo.get_by_id(trait_id)
        if not trait:
            raise NotFoundException("Trait", trait_id)

        if str(trait.experiment_id) != experiment_id:
            raise ValidationException("Trait does not belong to this experiment")

        if trait.data_type == "numeric" and value_numeric is None:
            raise ValidationException("Numeric value is required for numeric traits")
        if trait.data_type == "text" and value_text is None:
            raise ValidationException("Text value is required for text traits")
        if (
            trait.data_type == "categorical"
            and value_text is not None
            and trait.allowed_values
            and value_text not in trait.allowed_values
        ):
            raise ValidationException(
                f"Value '{value_text}' is not in allowed values: {', '.join(trait.allowed_values)}"
            )

        measurement = MeasurementModel(
            experiment_id=experiment_id,
            trait_id=trait_id,
            accession_id=accession_id,
            value_numeric=value_numeric,
            value_text=value_text,
            value_date=value_date,
            rep=rep,
            block=block,
            plot=plot,
            plant_id=plant_id,
            notes=notes.strip() if notes else None,
            measured_at=measured_at,
            measured_by=measured_by,
            image_url=image_url,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.measurement_repo.create(measurement)


class BulkCreateMeasurementsUseCase:
    def __init__(
        self,
        measurement_repo: MeasurementRepositoryInterface,
        experiment_repo: ExperimentRepositoryInterface,
        trait_repo: TraitRepositoryInterface,
    ):
        self.measurement_repo = measurement_repo
        self.experiment_repo = experiment_repo
        self.trait_repo = trait_repo

    async def execute(
        self,
        experiment_id: str,
        measurements_data: list[dict],
    ) -> list[MeasurementModel]:
        experiment = await self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise NotFoundException("Experiment", experiment_id)

        if not measurements_data:
            raise ValidationException("Measurements data cannot be empty")

        trait_ids = set()
        for m in measurements_data:
            if "trait_id" not in m:
                raise ValidationException("Each measurement must have a trait_id")
            trait_ids.add(m["trait_id"])

        for trait_id in trait_ids:
            trait = await self.trait_repo.get_by_id(trait_id)
            if not trait:
                raise NotFoundException("Trait", trait_id)
            if str(trait.experiment_id) != experiment_id:
                raise ValidationException(f"Trait {trait_id} does not belong to this experiment")

        measurements = []
        for m in measurements_data:
            measurement = MeasurementModel(
                experiment_id=experiment_id,
                trait_id=m["trait_id"],
                accession_id=m.get("accession_id"),
                value_numeric=m.get("value_numeric"),
                value_text=m.get("value_text"),
                value_date=m.get("value_date"),
                rep=m.get("rep"),
                block=m.get("block"),
                plot=m.get("plot"),
                plant_id=m.get("plant_id"),
                notes=m.get("notes"),
                measured_at=m.get("measured_at"),
                measured_by=m.get("measured_by"),
                image_url=m.get("image_url"),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            measurements.append(measurement)

        return await self.measurement_repo.bulk_create(measurements)


class GetMeasurementUseCase:
    def __init__(self, measurement_repo: MeasurementRepositoryInterface):
        self.measurement_repo = measurement_repo

    async def execute(self, measurement_id: str) -> MeasurementModel:
        measurement = await self.measurement_repo.get_by_id(measurement_id)
        if not measurement:
            raise NotFoundException("Measurement", measurement_id)
        return measurement


class ListMeasurementsUseCase:
    def __init__(self, measurement_repo: MeasurementRepositoryInterface):
        self.measurement_repo = measurement_repo

    async def execute(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        trait_id: str | None = None,
        accession_id: str | None = None,
    ) -> dict:
        measurements = await self.measurement_repo.list_by_experiment(
            experiment_id=experiment_id,
            skip=skip,
            limit=limit,
            trait_id=trait_id,
            accession_id=accession_id,
        )
        total = await self.measurement_repo.count_by_experiment(
            experiment_id=experiment_id,
            trait_id=trait_id,
            accession_id=accession_id,
        )

        return {
            "items": [
                {
                    "id": str(m.id),
                    "experiment_id": str(m.experiment_id),
                    "trait_id": str(m.trait_id),
                    "accession_id": str(m.accession_id) if m.accession_id else None,
                    "value_numeric": m.value_numeric,
                    "value_text": m.value_text,
                    "value_date": m.value_date.isoformat() if m.value_date else None,
                    "rep": m.rep,
                    "block": m.block,
                    "plot": m.plot,
                    "plant_id": m.plant_id,
                    "notes": m.notes,
                    "measured_at": m.measured_at.isoformat() if m.measured_at else None,
                    "measured_by": str(m.measured_by) if m.measured_by else None,
                    "image_url": m.image_url,
                    "created_at": m.created_at.isoformat(),
                    "updated_at": m.updated_at.isoformat(),
                }
                for m in measurements
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateMeasurementUseCase:
    def __init__(self, measurement_repo: MeasurementRepositoryInterface):
        self.measurement_repo = measurement_repo

    async def execute(
        self,
        measurement_id: str,
        value_numeric: float | None = None,
        value_text: str | None = None,
        value_date=None,
        rep: int | None = None,
        block: str | None = None,
        plot: str | None = None,
        plant_id: str | None = None,
        notes: str | None = None,
        measured_at=None,
        image_url: str | None = None,
    ) -> MeasurementModel:
        measurement = await self.measurement_repo.get_by_id(measurement_id)
        if not measurement:
            raise NotFoundException("Measurement", measurement_id)

        if value_numeric is not None:
            measurement.value_numeric = value_numeric
        if value_text is not None:
            measurement.value_text = value_text
        if value_date is not None:
            measurement.value_date = value_date
        if rep is not None:
            measurement.rep = rep
        if block is not None:
            measurement.block = block
        if plot is not None:
            measurement.plot = plot
        if plant_id is not None:
            measurement.plant_id = plant_id
        if notes is not None:
            measurement.notes = notes.strip() if notes else None
        if measured_at is not None:
            measurement.measured_at = measured_at
        if image_url is not None:
            measurement.image_url = image_url

        measurement.updated_at = datetime.now(UTC)
        return await self.measurement_repo.update(measurement)


class DeleteMeasurementUseCase:
    def __init__(self, measurement_repo: MeasurementRepositoryInterface):
        self.measurement_repo = measurement_repo

    async def execute(self, measurement_id: str) -> bool:
        measurement = await self.measurement_repo.get_by_id(measurement_id)
        if not measurement:
            raise NotFoundException("Measurement", measurement_id)

        return await self.measurement_repo.delete(measurement_id)


class GetExperimentSummaryUseCase:
    def __init__(self, measurement_repo: MeasurementRepositoryInterface):
        self.measurement_repo = measurement_repo

    async def execute(self, experiment_id: str) -> dict:
        return await self.measurement_repo.get_experiment_summary(experiment_id)
