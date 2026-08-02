import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.phenotyping.api.schemas import (
    BulkCreateMeasurementsRequest,
    CreateExperimentRequest,
    CreateMeasurementRequest,
    CreateTraitRequest,
    UpdateExperimentRequest,
    UpdateMeasurementRequest,
    UpdateTraitRequest,
)
from app.modules.phenotyping.domain.use_cases import (
    BulkCreateMeasurementsUseCase,
    CreateExperimentUseCase,
    CreateMeasurementUseCase,
    CreateTraitUseCase,
    DeleteExperimentUseCase,
    DeleteMeasurementUseCase,
    DeleteTraitUseCase,
    GetExperimentSummaryUseCase,
    GetExperimentUseCase,
    GetMeasurementUseCase,
    GetTraitUseCase,
    ListExperimentsUseCase,
    ListMeasurementsUseCase,
    ListTraitsUseCase,
    UpdateExperimentUseCase,
    UpdateMeasurementUseCase,
    UpdateTraitUseCase,
)
from app.modules.phenotyping.infrastructure.experiment_repository import ExperimentRepository
from app.modules.phenotyping.infrastructure.measurement_repository import MeasurementRepository
from app.modules.phenotyping.infrastructure.trait_repository import TraitRepository

logger = structlog.get_logger()
router = APIRouter()


def _get_repos(db: AsyncSession):
    return {
        "experiment": ExperimentRepository(db),
        "trait": TraitRepository(db),
        "measurement": MeasurementRepository(db),
    }


@router.get("/experiments", response_model=None)
async def list_experiments(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    project_id: str | None = Query(None),
    status: str | None = Query(
        None,
        pattern="^(planned|in_progress|completed|archived)$",
    ),
    search: str | None = Query(None, max_length=255),
):
    repos = _get_repos(db)
    use_case = ListExperimentsUseCase(repos["experiment"])
    return await use_case.execute(
        skip=skip,
        limit=limit,
        project_id=project_id,
        status=status,
        search=search,
        user_id=str(current_user["id"]),
    )


@router.post("/experiments", status_code=201)
async def create_experiment(
    body: CreateExperimentRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateExperimentUseCase(repos["experiment"])
    experiment = await use_case.execute(
        name=body.name,
        description=body.description,
        experiment_type=body.experiment_type,
        project_id=body.project_id,
        location=body.location,
        latitude=body.latitude,
        longitude=body.longitude,
        altitude=body.altitude,
        start_date=body.start_date,
        end_date=body.end_date,
        tags=body.tags,
        user_id=str(current_user["id"]),
    )
    logger.info("experiment_created", experiment_id=str(experiment.id))
    return {
        "id": str(experiment.id),
        "name": experiment.name,
        "description": experiment.description,
        "experiment_type": experiment.experiment_type,
        "project_id": str(experiment.project_id) if experiment.project_id else None,
        "location": experiment.location,
        "latitude": experiment.latitude,
        "longitude": experiment.longitude,
        "altitude": experiment.altitude,
        "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
        "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
        "status": experiment.status,
        "tags": experiment.tags,
        "created_by": str(experiment.created_by),
        "created_at": experiment.created_at.isoformat(),
        "updated_at": experiment.updated_at.isoformat(),
    }


@router.get("/experiments/{experiment_id}")
async def get_experiment(
    experiment_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetExperimentUseCase(repos["experiment"])
    experiment = await use_case.execute(experiment_id)
    return {
        "id": str(experiment.id),
        "name": experiment.name,
        "description": experiment.description,
        "experiment_type": experiment.experiment_type,
        "project_id": str(experiment.project_id) if experiment.project_id else None,
        "location": experiment.location,
        "latitude": experiment.latitude,
        "longitude": experiment.longitude,
        "altitude": experiment.altitude,
        "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
        "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
        "status": experiment.status,
        "tags": experiment.tags,
        "metadata": experiment.metadata_json,
        "created_by": str(experiment.created_by),
        "created_at": experiment.created_at.isoformat(),
        "updated_at": experiment.updated_at.isoformat(),
    }


@router.put("/experiments/{experiment_id}")
async def update_experiment(
    experiment_id: str,
    body: UpdateExperimentRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdateExperimentUseCase(repos["experiment"])
    experiment = await use_case.execute(
        experiment_id=experiment_id,
        user_id=str(current_user["id"]),
        name=body.name,
        description=body.description,
        experiment_type=body.experiment_type,
        location=body.location,
        latitude=body.latitude,
        longitude=body.longitude,
        altitude=body.altitude,
        start_date=body.start_date,
        end_date=body.end_date,
        status=body.status,
        tags=body.tags,
    )
    return {
        "id": str(experiment.id),
        "name": experiment.name,
        "description": experiment.description,
        "experiment_type": experiment.experiment_type,
        "location": experiment.location,
        "latitude": experiment.latitude,
        "longitude": experiment.longitude,
        "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
        "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
        "status": experiment.status,
        "tags": experiment.tags,
        "created_at": experiment.created_at.isoformat(),
        "updated_at": experiment.updated_at.isoformat(),
    }


@router.delete("/experiments/{experiment_id}")
async def delete_experiment(
    experiment_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteExperimentUseCase(repos["experiment"])
    await use_case.execute(experiment_id, str(current_user["id"]))
    return {"message": "Experiment deleted successfully"}


@router.get("/experiments/{experiment_id}/traits", response_model=None)
async def list_traits(
    experiment_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    repos = _get_repos(db)
    use_case = ListTraitsUseCase(repos["trait"])
    return await use_case.execute(experiment_id, skip=skip, limit=limit)


@router.post("/experiments/{experiment_id}/traits", status_code=201)
async def create_trait(
    experiment_id: str,
    body: CreateTraitRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateTraitUseCase(repos["trait"], repos["experiment"])
    trait = await use_case.execute(
        experiment_id=experiment_id,
        name=body.name,
        description=body.description,
        trait_category=body.trait_category,
        unit=body.unit,
        data_type=body.data_type,
        min_value=body.min_value,
        max_value=body.max_value,
        allowed_values=body.allowed_values,
        is_required=body.is_required,
    )
    logger.info("trait_created", trait_id=str(trait.id))
    return {
        "id": str(trait.id),
        "experiment_id": str(trait.experiment_id),
        "name": trait.name,
        "description": trait.description,
        "trait_category": trait.trait_category,
        "unit": trait.unit,
        "data_type": trait.data_type,
        "min_value": trait.min_value,
        "max_value": trait.max_value,
        "allowed_values": trait.allowed_values,
        "is_required": trait.is_required,
        "created_at": trait.created_at.isoformat(),
        "updated_at": trait.updated_at.isoformat(),
    }


@router.get("/traits/{trait_id}")
async def get_trait(
    trait_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetTraitUseCase(repos["trait"])
    trait = await use_case.execute(trait_id)
    return {
        "id": str(trait.id),
        "experiment_id": str(trait.experiment_id),
        "name": trait.name,
        "description": trait.description,
        "trait_category": trait.trait_category,
        "unit": trait.unit,
        "data_type": trait.data_type,
        "min_value": trait.min_value,
        "max_value": trait.max_value,
        "allowed_values": trait.allowed_values,
        "is_required": trait.is_required,
        "created_at": trait.created_at.isoformat(),
        "updated_at": trait.updated_at.isoformat(),
    }


@router.put("/traits/{trait_id}")
async def update_trait(
    trait_id: str,
    body: UpdateTraitRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdateTraitUseCase(repos["trait"])
    trait = await use_case.execute(
        trait_id=trait_id,
        name=body.name,
        description=body.description,
        trait_category=body.trait_category,
        unit=body.unit,
        data_type=body.data_type,
        min_value=body.min_value,
        max_value=body.max_value,
        allowed_values=body.allowed_values,
        is_required=body.is_required,
    )
    return {
        "id": str(trait.id),
        "experiment_id": str(trait.experiment_id),
        "name": trait.name,
        "description": trait.description,
        "trait_category": trait.trait_category,
        "unit": trait.unit,
        "data_type": trait.data_type,
        "min_value": trait.min_value,
        "max_value": trait.max_value,
        "allowed_values": trait.allowed_values,
        "is_required": trait.is_required,
        "created_at": trait.created_at.isoformat(),
        "updated_at": trait.updated_at.isoformat(),
    }


@router.delete("/traits/{trait_id}")
async def delete_trait(
    trait_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteTraitUseCase(repos["trait"])
    await use_case.execute(trait_id)
    return {"message": "Trait deleted successfully"}


@router.get("/experiments/{experiment_id}/measurements", response_model=None)
async def list_measurements(
    experiment_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    trait_id: str | None = Query(None),
    accession_id: str | None = Query(None),
):
    repos = _get_repos(db)
    use_case = ListMeasurementsUseCase(repos["measurement"])
    return await use_case.execute(
        experiment_id=experiment_id,
        skip=skip,
        limit=limit,
        trait_id=trait_id,
        accession_id=accession_id,
    )


@router.post("/experiments/{experiment_id}/measurements", status_code=201)
async def create_measurement(
    experiment_id: str,
    body: CreateMeasurementRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = CreateMeasurementUseCase(
        repos["measurement"], repos["experiment"], repos["trait"]
    )
    measurement = await use_case.execute(
        experiment_id=experiment_id,
        trait_id=body.trait_id,
        accession_id=body.accession_id,
        value_numeric=body.value_numeric,
        value_text=body.value_text,
        value_date=body.value_date,
        rep=body.rep,
        block=body.block,
        plot=body.plot,
        plant_id=body.plant_id,
        notes=body.notes,
        measured_at=body.measured_at,
        measured_by=str(current_user["id"]),
        image_url=body.image_url,
    )
    logger.info("measurement_created", measurement_id=str(measurement.id))
    return {
        "id": str(measurement.id),
        "experiment_id": str(measurement.experiment_id),
        "trait_id": str(measurement.trait_id),
        "accession_id": str(measurement.accession_id) if measurement.accession_id else None,
        "value_numeric": measurement.value_numeric,
        "value_text": measurement.value_text,
        "value_date": measurement.value_date.isoformat() if measurement.value_date else None,
        "rep": measurement.rep,
        "block": measurement.block,
        "plot": measurement.plot,
        "plant_id": measurement.plant_id,
        "notes": measurement.notes,
        "measured_at": measurement.measured_at.isoformat() if measurement.measured_at else None,
        "measured_by": str(measurement.measured_by) if measurement.measured_by else None,
        "image_url": measurement.image_url,
        "created_at": measurement.created_at.isoformat(),
        "updated_at": measurement.updated_at.isoformat(),
    }


@router.post("/experiments/{experiment_id}/measurements/bulk", status_code=201)
async def bulk_create_measurements(
    experiment_id: str,
    body: BulkCreateMeasurementsRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = BulkCreateMeasurementsUseCase(
        repos["measurement"], repos["experiment"], repos["trait"]
    )
    measurements_data = []
    for m in body.measurements:
        measurements_data.append({
            "trait_id": m.trait_id,
            "accession_id": m.accession_id,
            "value_numeric": m.value_numeric,
            "value_text": m.value_text,
            "value_date": m.value_date,
            "rep": m.rep,
            "block": m.block,
            "plot": m.plot,
            "plant_id": m.plant_id,
            "notes": m.notes,
            "measured_at": m.measured_at,
            "measured_by": str(current_user["id"]),
            "image_url": m.image_url,
        })

    measurements = await use_case.execute(
        experiment_id=experiment_id,
        measurements_data=measurements_data,
    )
    logger.info("measurements_bulk_created", count=len(measurements))
    return {
        "message": f"{len(measurements)} measurements created successfully",
        "count": len(measurements),
    }


@router.get("/measurements/{measurement_id}")
async def get_measurement(
    measurement_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetMeasurementUseCase(repos["measurement"])
    measurement = await use_case.execute(measurement_id)
    return {
        "id": str(measurement.id),
        "experiment_id": str(measurement.experiment_id),
        "trait_id": str(measurement.trait_id),
        "accession_id": str(measurement.accession_id) if measurement.accession_id else None,
        "value_numeric": measurement.value_numeric,
        "value_text": measurement.value_text,
        "value_date": measurement.value_date.isoformat() if measurement.value_date else None,
        "rep": measurement.rep,
        "block": measurement.block,
        "plot": measurement.plot,
        "plant_id": measurement.plant_id,
        "notes": measurement.notes,
        "measured_at": measurement.measured_at.isoformat() if measurement.measured_at else None,
        "measured_by": str(measurement.measured_by) if measurement.measured_by else None,
        "image_url": measurement.image_url,
        "created_at": measurement.created_at.isoformat(),
        "updated_at": measurement.updated_at.isoformat(),
    }


@router.put("/measurements/{measurement_id}")
async def update_measurement(
    measurement_id: str,
    body: UpdateMeasurementRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = UpdateMeasurementUseCase(repos["measurement"])
    measurement = await use_case.execute(
        measurement_id=measurement_id,
        value_numeric=body.value_numeric,
        value_text=body.value_text,
        value_date=body.value_date,
        rep=body.rep,
        block=body.block,
        plot=body.plot,
        plant_id=body.plant_id,
        notes=body.notes,
        measured_at=body.measured_at,
        image_url=body.image_url,
    )
    return {
        "id": str(measurement.id),
        "experiment_id": str(measurement.experiment_id),
        "trait_id": str(measurement.trait_id),
        "accession_id": str(measurement.accession_id) if measurement.accession_id else None,
        "value_numeric": measurement.value_numeric,
        "value_text": measurement.value_text,
        "value_date": measurement.value_date.isoformat() if measurement.value_date else None,
        "rep": measurement.rep,
        "block": measurement.block,
        "plot": measurement.plot,
        "plant_id": measurement.plant_id,
        "notes": measurement.notes,
        "measured_at": measurement.measured_at.isoformat() if measurement.measured_at else None,
        "measured_by": str(measurement.measured_by) if measurement.measured_by else None,
        "image_url": measurement.image_url,
        "created_at": measurement.created_at.isoformat(),
        "updated_at": measurement.updated_at.isoformat(),
    }


@router.delete("/measurements/{measurement_id}")
async def delete_measurement(
    measurement_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = DeleteMeasurementUseCase(repos["measurement"])
    await use_case.execute(measurement_id)
    return {"message": "Measurement deleted successfully"}


@router.get("/experiments/{experiment_id}/summary")
async def get_experiment_summary(
    experiment_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repos = _get_repos(db)
    use_case = GetExperimentSummaryUseCase(repos["measurement"])
    return await use_case.execute(experiment_id)
