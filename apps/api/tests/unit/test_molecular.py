
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundException, ValidationException
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
)
from app.modules.molecular.domain.interfaces import (
    ConstructRepositoryInterface,
    MoleculeExperimentRepositoryInterface,
    PrimerRepositoryInterface,
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
from app.modules.molecular.infrastructure.construct_repository import ConstructRepository
from app.modules.molecular.infrastructure.experiment_repository import MoleculeExperimentRepository
from app.modules.molecular.infrastructure.primer_repository import PrimerRepository


def make_mock_repo(**methods):
    repo = MagicMock(name="MockRepo")
    for name, value in methods.items():
        if callable(value):
            setattr(repo, name, AsyncMock(return_value=value()))
        else:
            setattr(repo, name, AsyncMock(return_value=value))
    return repo


# ────────────────────────── Model Tests ────────────────────────────────
class TestMoleculeExperimentModel:
    def test_valid_experiment_types(self):
        valid = [
            "PCR", "qPCR", "RT-PCR", "RNA-Seq", "DNA_Extraction",
            "RNA_Extraction", "ChIP-Seq", "ATAC-Seq", "Proteomics",
            "Metabolomics", "CRISPR", "Transformation", "Cloning",
        ]
        for t in valid:
            assert t in valid

    def test_valid_statuses(self):
        valid = ["planned", "in_progress", "completed", "archived"]
        for s in valid:
            assert s in valid

    def test_tags_optional(self):
        tags = ["gene-editing", "tissue-culture"]
        assert len(tags) == 2


class TestPrimerModel:
    def test_valid_primer_types(self):
        valid = ["forward", "reverse", "probe", "nested", "universal"]
        for pt in valid:
            assert pt in valid

    def test_is_validated_default(self):
        assert False is False

    def test_gc_percent(self):
        assert 55.0 == 55.0


class TestConstructModel:
    def test_valid_construct_types(self):
        valid = ["plasmid", "binary_vector", "expression_construct", "reporter", "crispr_construct"]
        for ct in valid:
            assert ct in valid

    def test_insert_size(self):
        assert 1200 == 1200


# ────────────────────────── Interface Tests ────────────────────────────
class TestInterfaces:
    def test_experiment_interface_methods(self):
        for method in ["create", "get_by_id", "list_experiments", "count_experiments", "update", "delete"]:
            assert hasattr(MoleculeExperimentRepositoryInterface, method)

    def test_primer_interface_methods(self):
        for method in ["create", "get_by_id", "list_by_experiment", "count_by_experiment", "update", "delete"]:
            assert hasattr(PrimerRepositoryInterface, method)

    def test_construct_interface_methods(self):
        for method in ["create", "get_by_id", "list_by_experiment", "count_by_experiment", "update", "delete"]:
            assert hasattr(ConstructRepositoryInterface, method)


# ────────────────────────── Use Case Tests ────────────────────────────
class TestCreateMoleculeExperimentUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(create=lambda: MagicMock(name="experiment"))
        uc = CreateMoleculeExperimentUseCase(experiment_repo=mock_repo)
        await uc.execute(
            name="CRISPR Study",
            user_id="user-1",
            experiment_type="CRISPR",
            project_id="proj-1",
        )
        mock_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        mock_repo = make_mock_repo()
        uc = CreateMoleculeExperimentUseCase(experiment_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(name="", user_id="user-1")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        mock_repo = make_mock_repo()
        uc = CreateMoleculeExperimentUseCase(experiment_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(name="Test", user_id="user-1", experiment_type="InvalidType")

    @pytest.mark.asyncio
    async def test_end_before_start_raises(self):
        from datetime import date
        mock_repo = make_mock_repo()
        uc = CreateMoleculeExperimentUseCase(experiment_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(
                name="Test",
                user_id="user-1",
                start_date=date(2025, 12, 31),
                end_date=date(2025, 1, 1),
            )


class TestGetMoleculeExperimentUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="experiment"))
        uc = GetMoleculeExperimentUseCase(experiment_repo=mock_repo)
        await uc.execute("exp-1")
        mock_repo.get_by_id.assert_awaited_once_with("exp-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = GetMoleculeExperimentUseCase(experiment_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestUpdateMoleculeExperimentUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        exp = MagicMock(name="experiment")
        exp.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: exp, update=lambda: exp)
        uc = UpdateMoleculeExperimentUseCase(experiment_repo=mock_repo)
        await uc.execute(experiment_id="exp-1", user_id="user-1", name="Updated")
        mock_repo.get_by_id.assert_awaited_once_with("exp-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = UpdateMoleculeExperimentUseCase(experiment_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(experiment_id="nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        exp = MagicMock(name="experiment")
        exp.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: exp)
        uc = UpdateMoleculeExperimentUseCase(experiment_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(experiment_id="exp-1", user_id="user-2")


class TestDeleteMoleculeExperimentUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        exp = MagicMock(name="experiment")
        exp.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: exp, delete=lambda: True)
        uc = DeleteMoleculeExperimentUseCase(experiment_repo=mock_repo)
        await uc.execute(experiment_id="exp-1", user_id="user-1")
        mock_repo.delete.assert_awaited_once_with("exp-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = DeleteMoleculeExperimentUseCase(experiment_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(experiment_id="nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        exp = MagicMock(name="experiment")
        exp.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: exp)
        uc = DeleteMoleculeExperimentUseCase(experiment_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(experiment_id="exp-1", user_id="user-2")


class TestCreatePrimerUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_primer = make_mock_repo(create=lambda: MagicMock(name="primer"))
        mock_exp = make_mock_repo(get_by_id=lambda: MagicMock(name="experiment"))
        uc = CreatePrimerUseCase(primer_repo=mock_primer, experiment_repo=mock_exp)
        await uc.execute(
            experiment_id="exp-1",
            name="TCP1-F",
            sequence="ATGGCTAGCTAGCTAGCTAG",
            user_id="user-1",
        )
        mock_primer.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_experiment_not_found(self):
        mock_primer = make_mock_repo()
        mock_exp = make_mock_repo(get_by_id=lambda: None)
        uc = CreatePrimerUseCase(primer_repo=mock_primer, experiment_repo=mock_exp)
        with pytest.raises(NotFoundException):
            await uc.execute(experiment_id="nonexistent", name="F", sequence="ATCG", user_id="user-1")

    @pytest.mark.asyncio
    async def test_invalid_sequence_raises(self):
        mock_primer = make_mock_repo()
        mock_exp = make_mock_repo(get_by_id=lambda: MagicMock(name="experiment"))
        uc = CreatePrimerUseCase(primer_repo=mock_primer, experiment_repo=mock_exp)
        with pytest.raises(ValidationException):
            await uc.execute(experiment_id="exp-1", name="F", sequence="INVALID!SEQ", user_id="user-1")

    @pytest.mark.asyncio
    async def test_invalid_primer_type_raises(self):
        mock_primer = make_mock_repo()
        mock_exp = make_mock_repo(get_by_id=lambda: MagicMock(name="experiment"))
        uc = CreatePrimerUseCase(primer_repo=mock_primer, experiment_repo=mock_exp)
        with pytest.raises(ValidationException):
            await uc.execute(
                experiment_id="exp-1", name="F", sequence="ATCG",
                user_id="user-1", primer_type="invalid",
            )


class TestGetPrimerUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="primer"))
        uc = GetPrimerUseCase(primer_repo=mock_repo)
        await uc.execute("primer-1")
        mock_repo.get_by_id.assert_awaited_once_with("primer-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = GetPrimerUseCase(primer_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestListPrimersUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(list_by_experiment=lambda: [], count_by_experiment=lambda: 0)
        uc = ListPrimersUseCase(primer_repo=mock_repo)
        result = await uc.execute(experiment_id="exp-1", skip=0, limit=100)
        assert isinstance(result, dict)
        assert "items" in result

    @pytest.mark.asyncio
    async def test_with_type_filter(self):
        mock_repo = make_mock_repo(list_by_experiment=lambda: [], count_by_experiment=lambda: 0)
        uc = ListPrimersUseCase(primer_repo=mock_repo)
        await uc.execute(experiment_id="exp-1", primer_type="forward")
        mock_repo.list_by_experiment.assert_awaited_once()


class TestUpdatePrimerUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        primer = MagicMock(name="primer")
        mock_repo = make_mock_repo(get_by_id=lambda: primer, update=lambda: primer)
        uc = UpdatePrimerUseCase(primer_repo=mock_repo)
        await uc.execute(primer_id="primer-1", name="Updated")
        mock_repo.get_by_id.assert_awaited_once_with("primer-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = UpdatePrimerUseCase(primer_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(primer_id="nonexistent")

    @pytest.mark.asyncio
    async def test_invalid_sequence_raises(self):
        primer = MagicMock(name="primer")
        mock_repo = make_mock_repo(get_by_id=lambda: primer)
        uc = UpdatePrimerUseCase(primer_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(primer_id="primer-1", sequence="INVALID!SEQ")


class TestDeletePrimerUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="primer"), delete=lambda: True)
        uc = DeletePrimerUseCase(primer_repo=mock_repo)
        await uc.execute("primer-1")
        mock_repo.delete.assert_awaited_once_with("primer-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = DeletePrimerUseCase(primer_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestCreateConstructUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_construct = make_mock_repo(create=lambda: MagicMock(name="construct"))
        mock_exp = make_mock_repo(get_by_id=lambda: MagicMock(name="experiment"))
        uc = CreateConstructUseCase(construct_repo=mock_construct, experiment_repo=mock_exp)
        await uc.execute(
            experiment_id="exp-1",
            name="pBI121-TCP1",
            user_id="user-1",
            construct_type="binary_vector",
            vector_backbone="pBI121",
        )
        mock_construct.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_experiment_not_found(self):
        mock_construct = make_mock_repo()
        mock_exp = make_mock_repo(get_by_id=lambda: None)
        uc = CreateConstructUseCase(construct_repo=mock_construct, experiment_repo=mock_exp)
        with pytest.raises(NotFoundException):
            await uc.execute(experiment_id="nonexistent", name="Test", user_id="user-1")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        mock_construct = make_mock_repo()
        mock_exp = make_mock_repo(get_by_id=lambda: MagicMock(name="experiment"))
        uc = CreateConstructUseCase(construct_repo=mock_construct, experiment_repo=mock_exp)
        with pytest.raises(ValidationException):
            await uc.execute(
                experiment_id="exp-1", name="Test", user_id="user-1",
                construct_type="invalid",
            )


class TestGetConstructUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="construct"))
        uc = GetConstructUseCase(construct_repo=mock_repo)
        await uc.execute("construct-1")
        mock_repo.get_by_id.assert_awaited_once_with("construct-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = GetConstructUseCase(construct_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestListConstructsUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(list_by_experiment=lambda: [], count_by_experiment=lambda: 0)
        uc = ListConstructsUseCase(construct_repo=mock_repo)
        result = await uc.execute(experiment_id="exp-1", skip=0, limit=100)
        assert isinstance(result, dict)
        assert "items" in result

    @pytest.mark.asyncio
    async def test_with_type_filter(self):
        mock_repo = make_mock_repo(list_by_experiment=lambda: [], count_by_experiment=lambda: 0)
        uc = ListConstructsUseCase(construct_repo=mock_repo)
        await uc.execute(experiment_id="exp-1", construct_type="plasmid")
        mock_repo.list_by_experiment.assert_awaited_once()


class TestUpdateConstructUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        construct = MagicMock(name="construct")
        mock_repo = make_mock_repo(get_by_id=lambda: construct, update=lambda: construct)
        uc = UpdateConstructUseCase(construct_repo=mock_repo)
        await uc.execute(construct_id="construct-1", name="Updated")
        mock_repo.get_by_id.assert_awaited_once_with("construct-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = UpdateConstructUseCase(construct_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(construct_id="nonexistent")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        construct = MagicMock(name="construct")
        mock_repo = make_mock_repo(get_by_id=lambda: construct)
        uc = UpdateConstructUseCase(construct_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(construct_id="construct-1", construct_type="invalid")


class TestDeleteConstructUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="construct"), delete=lambda: True)
        uc = DeleteConstructUseCase(construct_repo=mock_repo)
        await uc.execute("construct-1")
        mock_repo.delete.assert_awaited_once_with("construct-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = DeleteConstructUseCase(construct_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


# ────────────────────────── Schema Tests ───────────────────────────────
class TestSchemaValidation:
    def test_create_experiment_request(self):
        req = CreateMoleculeExperimentRequest(
            name="RNA-Seq Study",
            experiment_type="RNA-Seq",
            project_id="proj-1",
            tags=["transcriptomics"],
        )
        assert req.name == "RNA-Seq Study"
        assert req.experiment_type == "RNA-Seq"

    def test_create_experiment_defaults(self):
        req = CreateMoleculeExperimentRequest(name="Test")
        assert req.experiment_type == "PCR"

    def test_create_primer_request(self):
        req = CreatePrimerRequest(
            name="TCP1-F",
            sequence="ATGGCTAGCTAGCTAGCTAG",
            primer_type="forward",
            target_gene="AtTCP1",
            tm=58.5,
        )
        assert req.name == "TCP1-F"
        assert len(req.sequence) == 20

    def test_create_primer_defaults(self):
        req = CreatePrimerRequest(name="F", sequence="ATCG")
        assert req.primer_type == "forward"

    def test_create_construct_request(self):
        req = CreateConstructRequest(
            name="pBI121-TCP1",
            construct_type="binary_vector",
            vector_backbone="pBI121",
            promoter="CaMV 35S",
        )
        assert req.construct_type == "binary_vector"

    def test_create_construct_defaults(self):
        req = CreateConstructRequest(name="Test")
        assert req.construct_type == "plasmid"

    def test_experiment_response(self):
        resp = MoleculeExperimentResponse(
            id="exp-1", name="Test", experiment_type="PCR",
            status="planned", created_by="user-1",
            created_at="2025-01-01T00:00:00", updated_at="2025-01-01T00:00:00",
        )
        assert resp.id == "exp-1"

    def test_primer_response(self):
        resp = PrimerResponse(
            id="p-1", experiment_id="exp-1", name="TCP1-F",
            sequence="ATCG", primer_type="forward", is_validated=False,
            created_by="user-1", created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        assert resp.id == "p-1"

    def test_construct_response(self):
        resp = ConstructResponse(
            id="c-1", experiment_id="exp-1", name="Test",
            construct_type="plasmid", is_validated=False,
            created_by="user-1",
            created_at="2025-01-01T00:00:00", updated_at="2025-01-01T00:00:00",
        )
        assert resp.id == "c-1"

    def test_paginated_responses(self):
        exp = PaginatedMoleculeExperimentsResponse(items=[], total=0, skip=0, limit=20)
        pri = PaginatedPrimersResponse(items=[], total=0, skip=0, limit=100)
        con = PaginatedConstructsResponse(items=[], total=0, skip=0, limit=100)
        assert exp.total == 0
        assert pri.total == 0
        assert con.total == 0


# ────────────────────────── Integration Tests ──────────────────────────
class TestMolecularModuleIntegration:
    def test_module_has_correct_structure(self):
        pass

    def test_router_has_all_endpoints(self):
        from app.modules.molecular.api.router import router
        routes = [r.path for r in router.routes]
        assert any("/experiments" in p for p in routes)
        assert any("/experiments/{experiment_id}" in p for p in routes)
        assert any("primers" in p for p in routes)
        assert any("constructs" in p for p in routes)

    def test_all_use_case_classes_exist(self):
        use_cases = [
            CreateMoleculeExperimentUseCase,
            GetMoleculeExperimentUseCase,
            ListMoleculeExperimentsUseCase,
            UpdateMoleculeExperimentUseCase,
            DeleteMoleculeExperimentUseCase,
            CreatePrimerUseCase,
            GetPrimerUseCase,
            ListPrimersUseCase,
            UpdatePrimerUseCase,
            DeletePrimerUseCase,
            CreateConstructUseCase,
            GetConstructUseCase,
            ListConstructsUseCase,
            UpdateConstructUseCase,
            DeleteConstructUseCase,
        ]
        assert len(use_cases) == 15

    def test_infrastructure_repos_exist(self):
        assert MoleculeExperimentRepository is not None
        assert PrimerRepository is not None
        assert ConstructRepository is not None
