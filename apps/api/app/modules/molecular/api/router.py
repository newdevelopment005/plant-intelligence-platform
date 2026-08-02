from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.molecular.api.schemas import (
    ConstructResponse,
    CreateConstructRequest,
    CreateMoleculeExperimentRequest,
    CreatePrimerRequest,
    MoleculeExperimentResponse,
    PaginatedConstructsResponse,
    PaginatedMoleculeExperimentsResponse,
    PaginatedPrimersResponse,
    PrimerResponse,
    UpdateConstructRequest,
    UpdateMoleculeExperimentRequest,
    UpdatePrimerRequest,
)
from app.modules.molecular.domain.use_cases import (
    CreateConstructUseCase,
    CreateMoleculeExperimentUseCase,
    CreatePrimerUseCase,
    DeleteConstructUseCase,
    DeleteMoleculeExperimentUseCase,
    DeletePrimerUseCase,
    GetConstructUseCase,
    GetMoleculeExperimentUseCase,
    GetPrimerUseCase,
    ListConstructsUseCase,
    ListMoleculeExperimentsUseCase,
    ListPrimersUseCase,
    UpdateConstructUseCase,
    UpdateMoleculeExperimentUseCase,
    UpdatePrimerUseCase,
)

router = APIRouter()


# ────────────────────────── Experiments ────────────────────────────────
@router.post("/experiments", response_model=MoleculeExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    request: CreateMoleculeExperimentRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.experiment_repository import (
        MoleculeExperimentRepository,
    )
    repo = MoleculeExperimentRepository(db)
    uc = CreateMoleculeExperimentUseCase(experiment_repo=repo)
    return await uc.execute(
        name=request.name,
        user_id=current_user["id"],
        description=request.description,
        experiment_type=request.experiment_type,
        project_id=request.project_id,
        species_id=request.species_id,
        protocol=request.protocol,
        start_date=request.start_date,
        end_date=request.end_date,
        notes=request.notes,
        tags=request.tags,
    )


@router.get("/experiments", response_model=PaginatedMoleculeExperimentsResponse)
async def list_experiments(
    skip: int = 0,
    limit: int = 20,
    experiment_type: str | None = None,
    project_id: str | None = None,
    status: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.experiment_repository import (
        MoleculeExperimentRepository,
    )
    repo = MoleculeExperimentRepository(db)
    uc = ListMoleculeExperimentsUseCase(experiment_repo=repo)
    result = await uc.execute(
        skip=skip,
        limit=limit,
        experiment_type=experiment_type,
        project_id=project_id,
        status=status,
        search=search,
        user_id=current_user["id"],
    )
    return PaginatedMoleculeExperimentsResponse(**result)


@router.get("/experiments/{experiment_id}", response_model=MoleculeExperimentResponse)
async def get_experiment(
    experiment_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.experiment_repository import (
        MoleculeExperimentRepository,
    )
    repo = MoleculeExperimentRepository(db)
    uc = GetMoleculeExperimentUseCase(experiment_repo=repo)
    return await uc.execute(experiment_id)


@router.put("/experiments/{experiment_id}", response_model=MoleculeExperimentResponse)
async def update_experiment(
    experiment_id: str,
    request: UpdateMoleculeExperimentRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.experiment_repository import (
        MoleculeExperimentRepository,
    )
    repo = MoleculeExperimentRepository(db)
    uc = UpdateMoleculeExperimentUseCase(experiment_repo=repo)
    return await uc.execute(
        experiment_id=experiment_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        experiment_type=request.experiment_type,
        protocol=request.protocol,
        start_date=request.start_date,
        end_date=request.end_date,
        status=request.status,
        result_summary=request.result_summary,
        notes=request.notes,
        tags=request.tags,
    )


@router.delete("/experiments/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(
    experiment_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.experiment_repository import (
        MoleculeExperimentRepository,
    )
    repo = MoleculeExperimentRepository(db)
    uc = DeleteMoleculeExperimentUseCase(experiment_repo=repo)
    await uc.execute(experiment_id=experiment_id, user_id=current_user["id"])


# ────────────────────────── Primers ────────────────────────────────────
@router.post(
    "/experiments/{experiment_id}/primers",
    response_model=PrimerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_primer(
    experiment_id: str,
    request: CreatePrimerRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.experiment_repository import (
        MoleculeExperimentRepository,
    )
    from app.modules.molecular.infrastructure.primer_repository import PrimerRepository
    primer_repo = PrimerRepository(db)
    exp_repo = MoleculeExperimentRepository(db)
    uc = CreatePrimerUseCase(primer_repo=primer_repo, experiment_repo=exp_repo)
    return await uc.execute(
        experiment_id=experiment_id,
        name=request.name,
        sequence=request.sequence,
        user_id=current_user["id"],
        description=request.description,
        primer_type=request.primer_type,
        target_gene=request.target_gene,
        target_organism=request.target_organism,
        tm=request.tm,
        amplicon_size=request.amplicon_size,
        notes=request.notes,
    )


@router.get("/experiments/{experiment_id}/primers", response_model=PaginatedPrimersResponse)
async def list_primers(
    experiment_id: str,
    skip: int = 0,
    limit: int = 100,
    primer_type: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.primer_repository import PrimerRepository
    repo = PrimerRepository(db)
    uc = ListPrimersUseCase(primer_repo=repo)
    result = await uc.execute(
        experiment_id=experiment_id,
        skip=skip,
        limit=limit,
        primer_type=primer_type,
        search=search,
    )
    return PaginatedPrimersResponse(**result)


@router.get("/experiments/{experiment_id}/primers/{primer_id}", response_model=PrimerResponse)
async def get_primer(
    experiment_id: str,
    primer_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.primer_repository import PrimerRepository
    repo = PrimerRepository(db)
    uc = GetPrimerUseCase(primer_repo=repo)
    return await uc.execute(primer_id)


@router.put("/experiments/{experiment_id}/primers/{primer_id}", response_model=PrimerResponse)
async def update_primer(
    experiment_id: str,
    primer_id: str,
    request: UpdatePrimerRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.primer_repository import PrimerRepository
    repo = PrimerRepository(db)
    uc = UpdatePrimerUseCase(primer_repo=repo)
    return await uc.execute(
        primer_id=primer_id,
        name=request.name,
        description=request.description,
        sequence=request.sequence,
        primer_type=request.primer_type,
        target_gene=request.target_gene,
        target_organism=request.target_organism,
        tm=request.tm,
        amplicon_size=request.amplicon_size,
        is_validated=request.is_validated,
        notes=request.notes,
    )


@router.delete("/experiments/{experiment_id}/primers/{primer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_primer(
    experiment_id: str,
    primer_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.primer_repository import PrimerRepository
    repo = PrimerRepository(db)
    uc = DeletePrimerUseCase(primer_repo=repo)
    await uc.execute(primer_id)


# ────────────────────────── Constructs ─────────────────────────────────
@router.post(
    "/experiments/{experiment_id}/constructs",
    response_model=ConstructResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_construct(
    experiment_id: str,
    request: CreateConstructRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.construct_repository import ConstructRepository
    from app.modules.molecular.infrastructure.experiment_repository import (
        MoleculeExperimentRepository,
    )
    construct_repo = ConstructRepository(db)
    exp_repo = MoleculeExperimentRepository(db)
    uc = CreateConstructUseCase(construct_repo=construct_repo, experiment_repo=exp_repo)
    return await uc.execute(
        experiment_id=experiment_id,
        name=request.name,
        user_id=current_user["id"],
        description=request.description,
        construct_type=request.construct_type,
        vector_backbone=request.vector_backbone,
        insert_sequence=request.insert_sequence,
        insert_name=request.insert_name,
        selection_marker=request.selection_marker,
        promoter=request.promoter,
        resistance=request.resistance,
        species_id=request.species_id,
        notes=request.notes,
        tags=request.tags,
    )


@router.get("/experiments/{experiment_id}/constructs", response_model=PaginatedConstructsResponse)
async def list_constructs(
    experiment_id: str,
    skip: int = 0,
    limit: int = 100,
    construct_type: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.construct_repository import ConstructRepository
    repo = ConstructRepository(db)
    uc = ListConstructsUseCase(construct_repo=repo)
    result = await uc.execute(
        experiment_id=experiment_id,
        skip=skip,
        limit=limit,
        construct_type=construct_type,
        search=search,
    )
    return PaginatedConstructsResponse(**result)


@router.get(
    "/experiments/{experiment_id}/constructs/{construct_id}",
    response_model=ConstructResponse,
)
async def get_construct(
    experiment_id: str,
    construct_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.construct_repository import ConstructRepository
    repo = ConstructRepository(db)
    uc = GetConstructUseCase(construct_repo=repo)
    return await uc.execute(construct_id)


@router.put(
    "/experiments/{experiment_id}/constructs/{construct_id}",
    response_model=ConstructResponse,
)
async def update_construct(
    experiment_id: str,
    construct_id: str,
    request: UpdateConstructRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.construct_repository import ConstructRepository
    repo = ConstructRepository(db)
    uc = UpdateConstructUseCase(construct_repo=repo)
    return await uc.execute(
        construct_id=construct_id,
        name=request.name,
        description=request.description,
        construct_type=request.construct_type,
        vector_backbone=request.vector_backbone,
        insert_sequence=request.insert_sequence,
        insert_name=request.insert_name,
        selection_marker=request.selection_marker,
        promoter=request.promoter,
        resistance=request.resistance,
        is_validated=request.is_validated,
        notes=request.notes,
        tags=request.tags,
    )


@router.delete(
    "/experiments/{experiment_id}/constructs/{construct_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_construct(
    experiment_id: str,
    construct_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.molecular.infrastructure.construct_repository import ConstructRepository
    repo = ConstructRepository(db)
    uc = DeleteConstructUseCase(construct_repo=repo)
    await uc.execute(construct_id)
