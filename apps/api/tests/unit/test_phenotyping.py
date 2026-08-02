import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import UTC, date, datetime

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
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


class TestCreateExperimentUseCase:
    def setup_method(self):
        self.experiment_repo = MagicMock()
        self.use_case = CreateExperimentUseCase(self.experiment_repo)

    @pytest.mark.asyncio
    async def test_create_experiment_success(self):
        mock_exp = MagicMock()
        mock_exp.id = "exp-1"
        mock_exp.name = "Drought Trial"
        mock_exp.experiment_type = "field"
        mock_exp.status = "planned"
        mock_exp.created_at = datetime.now(UTC)
        mock_exp.updated_at = datetime.now(UTC)
        self.experiment_repo.create = AsyncMock(return_value=mock_exp)
        result = await self.use_case.execute(
            name="Drought Trial",
            user_id="user-1",
            experiment_type="field",
            location="Field A",
        )
        assert result.name == "Drought Trial"
        self.experiment_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_experiment_empty_name(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(name="", user_id="user-1")

    @pytest.mark.asyncio
    async def test_create_experiment_invalid_type(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(name="Test", user_id="user-1", experiment_type="invalid")

    @pytest.mark.asyncio
    async def test_create_experiment_invalid_dates(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                name="Test",
                user_id="user-1",
                start_date=date(2025, 12, 31),
                end_date=date(2025, 1, 1),
            )


class TestGetExperimentUseCase:
    def setup_method(self):
        self.experiment_repo = MagicMock()
        self.use_case = GetExperimentUseCase(self.experiment_repo)

    @pytest.mark.asyncio
    async def test_get_experiment_success(self):
        mock_exp = MagicMock()
        mock_exp.id = "exp-1"
        mock_exp.name = "Test"
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        result = await self.use_case.execute("exp-1")
        assert result.name == "Test"

    @pytest.mark.asyncio
    async def test_get_experiment_not_found(self):
        self.experiment_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("exp-999")


class TestListExperimentsUseCase:
    def setup_method(self):
        self.experiment_repo = MagicMock()
        self.use_case = ListExperimentsUseCase(self.experiment_repo)

    @pytest.mark.asyncio
    async def test_list_experiments_success(self):
        self.experiment_repo.list_experiments = AsyncMock(return_value=[])
        self.experiment_repo.count_experiments = AsyncMock(return_value=0)
        result = await self.use_case.execute(user_id="user-1")
        assert result["items"] == []
        assert result["total"] == 0


class TestUpdateExperimentUseCase:
    def setup_method(self):
        self.experiment_repo = MagicMock()
        self.use_case = UpdateExperimentUseCase(self.experiment_repo)

    @pytest.mark.asyncio
    async def test_update_experiment_success(self):
        mock_exp = MagicMock(id="exp-1", created_by="user-1", name="Original")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.experiment_repo.update = AsyncMock(return_value=mock_exp)
        result = await self.use_case.execute("exp-1", "user-1", name="Updated")
        assert result.name == "Updated"

    @pytest.mark.asyncio
    async def test_update_experiment_not_found(self):
        self.experiment_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("exp-999", "user-1", name="X")

    @pytest.mark.asyncio
    async def test_update_experiment_forbidden(self):
        mock_exp = MagicMock(id="exp-1", created_by="user-2")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute("exp-1", "user-1", name="X")

    @pytest.mark.asyncio
    async def test_update_experiment_empty_name(self):
        mock_exp = MagicMock(id="exp-1", created_by="user-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute("exp-1", "user-1", name="")

    @pytest.mark.asyncio
    async def test_update_experiment_invalid_status(self):
        mock_exp = MagicMock(id="exp-1", created_by="user-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute("exp-1", "user-1", status="invalid")


class TestDeleteExperimentUseCase:
    def setup_method(self):
        self.experiment_repo = MagicMock()
        self.use_case = DeleteExperimentUseCase(self.experiment_repo)

    @pytest.mark.asyncio
    async def test_delete_experiment_success(self):
        mock_exp = MagicMock(id="exp-1", created_by="user-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.experiment_repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute("exp-1", "user-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_experiment_not_found(self):
        self.experiment_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("exp-999", "user-1")

    @pytest.mark.asyncio
    async def test_delete_experiment_forbidden(self):
        mock_exp = MagicMock(id="exp-1", created_by="user-2")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute("exp-1", "user-1")


class TestCreateTraitUseCase:
    def setup_method(self):
        self.trait_repo = MagicMock()
        self.experiment_repo = MagicMock()
        self.use_case = CreateTraitUseCase(self.trait_repo, self.experiment_repo)

    @pytest.mark.asyncio
    async def test_create_trait_success(self):
        mock_exp = MagicMock()
        mock_exp.id = "exp-1"
        mock_trait = MagicMock()
        mock_trait.id = "t-1"
        mock_trait.name = "Plant Height"
        mock_trait.created_at = datetime.now(UTC)
        mock_trait.updated_at = datetime.now(UTC)
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.trait_repo.create = AsyncMock(return_value=mock_trait)
        result = await self.use_case.execute(
            experiment_id="exp-1",
            name="Plant Height",
            unit="cm",
            data_type="numeric",
        )
        assert result.name == "Plant Height"

    @pytest.mark.asyncio
    async def test_create_trait_experiment_not_found(self):
        self.experiment_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(experiment_id="exp-999", name="Test")

    @pytest.mark.asyncio
    async def test_create_trait_empty_name(self):
        mock_exp = MagicMock(id="exp-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute(experiment_id="exp-1", name="")

    @pytest.mark.asyncio
    async def test_create_trait_invalid_data_type(self):
        mock_exp = MagicMock(id="exp-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                experiment_id="exp-1", name="Test", data_type="invalid"
            )

    @pytest.mark.asyncio
    async def test_create_trait_invalid_range(self):
        mock_exp = MagicMock(id="exp-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                experiment_id="exp-1", name="Test", min_value=100, max_value=10
            )


class TestGetTraitUseCase:
    def setup_method(self):
        self.trait_repo = MagicMock()
        self.use_case = GetTraitUseCase(self.trait_repo)

    @pytest.mark.asyncio
    async def test_get_trait_success(self):
        mock_trait = MagicMock()
        mock_trait.id = "t-1"
        mock_trait.name = "Height"
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        result = await self.use_case.execute("t-1")
        assert result.name == "Height"

    @pytest.mark.asyncio
    async def test_get_trait_not_found(self):
        self.trait_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("t-999")


class TestListTraitsUseCase:
    def setup_method(self):
        self.trait_repo = MagicMock()
        self.use_case = ListTraitsUseCase(self.trait_repo)

    @pytest.mark.asyncio
    async def test_list_traits_success(self):
        self.trait_repo.list_by_experiment = AsyncMock(return_value=[])
        self.trait_repo.count_by_experiment = AsyncMock(return_value=0)
        result = await self.use_case.execute("exp-1")
        assert result["items"] == []
        assert result["total"] == 0


class TestUpdateTraitUseCase:
    def setup_method(self):
        self.trait_repo = MagicMock()
        self.use_case = UpdateTraitUseCase(self.trait_repo)

    @pytest.mark.asyncio
    async def test_update_trait_success(self):
        mock_trait = MagicMock(id="t-1", name="Original")
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        self.trait_repo.update = AsyncMock(return_value=mock_trait)
        result = await self.use_case.execute("t-1", name="Updated")
        assert result.name == "Updated"

    @pytest.mark.asyncio
    async def test_update_trait_not_found(self):
        self.trait_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("t-999", name="X")

    @pytest.mark.asyncio
    async def test_update_trait_empty_name(self):
        mock_trait = MagicMock(id="t-1")
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        with pytest.raises(ValidationException):
            await self.use_case.execute("t-1", name="")

    @pytest.mark.asyncio
    async def test_update_trait_invalid_data_type(self):
        mock_trait = MagicMock(id="t-1")
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        with pytest.raises(ValidationException):
            await self.use_case.execute("t-1", data_type="invalid")


class TestDeleteTraitUseCase:
    def setup_method(self):
        self.trait_repo = MagicMock()
        self.use_case = DeleteTraitUseCase(self.trait_repo)

    @pytest.mark.asyncio
    async def test_delete_trait_success(self):
        mock_trait = MagicMock(id="t-1")
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        self.trait_repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute("t-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_trait_not_found(self):
        self.trait_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("t-999")


class TestCreateMeasurementUseCase:
    def setup_method(self):
        self.measurement_repo = MagicMock()
        self.experiment_repo = MagicMock()
        self.trait_repo = MagicMock()
        self.use_case = CreateMeasurementUseCase(
            self.measurement_repo, self.experiment_repo, self.trait_repo
        )

    @pytest.mark.asyncio
    async def test_create_measurement_success(self):
        mock_exp = MagicMock(id="exp-1")
        mock_trait = MagicMock(id="t-1", experiment_id="exp-1", data_type="numeric")
        mock_measurement = MagicMock(id="m-1", created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        self.measurement_repo.create = AsyncMock(return_value=mock_measurement)
        result = await self.use_case.execute(
            experiment_id="exp-1",
            trait_id="t-1",
            value_numeric=42.5,
        )
        assert result.id == "m-1"

    @pytest.mark.asyncio
    async def test_create_measurement_experiment_not_found(self):
        self.experiment_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(experiment_id="exp-999", trait_id="t-1")

    @pytest.mark.asyncio
    async def test_create_measurement_trait_not_found(self):
        mock_exp = MagicMock(id="exp-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.trait_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(experiment_id="exp-1", trait_id="t-999")

    @pytest.mark.asyncio
    async def test_create_measurement_wrong_experiment(self):
        mock_exp = MagicMock(id="exp-1")
        mock_trait = MagicMock(id="t-1", experiment_id="exp-2", data_type="numeric")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                experiment_id="exp-1", trait_id="t-1", value_numeric=10
            )

    @pytest.mark.asyncio
    async def test_create_measurement_missing_numeric(self):
        mock_exp = MagicMock(id="exp-1")
        mock_trait = MagicMock(id="t-1", experiment_id="exp-1", data_type="numeric")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        with pytest.raises(ValidationException):
            await self.use_case.execute(experiment_id="exp-1", trait_id="t-1")

    @pytest.mark.asyncio
    async def test_create_measurement_invalid_categorical(self):
        mock_exp = MagicMock(id="exp-1")
        mock_trait = MagicMock(
            id="t-1", experiment_id="exp-1", data_type="categorical",
            allowed_values=["low", "medium", "high"],
        )
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                experiment_id="exp-1", trait_id="t-1", value_text="invalid"
            )


class TestBulkCreateMeasurementsUseCase:
    def setup_method(self):
        self.measurement_repo = MagicMock()
        self.experiment_repo = MagicMock()
        self.trait_repo = MagicMock()
        self.use_case = BulkCreateMeasurementsUseCase(
            self.measurement_repo, self.experiment_repo, self.trait_repo
        )

    @pytest.mark.asyncio
    async def test_bulk_create_success(self):
        mock_exp = MagicMock(id="exp-1")
        mock_trait = MagicMock(id="t-1", experiment_id="exp-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        self.trait_repo.get_by_id = AsyncMock(return_value=mock_trait)
        self.measurement_repo.bulk_create = AsyncMock(return_value=[MagicMock(), MagicMock()])
        result = await self.use_case.execute(
            experiment_id="exp-1",
            measurements_data=[
                {"trait_id": "t-1", "value_numeric": 10},
                {"trait_id": "t-1", "value_numeric": 20},
            ],
        )
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_bulk_create_empty_data(self):
        mock_exp = MagicMock(id="exp-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute(experiment_id="exp-1", measurements_data=[])

    @pytest.mark.asyncio
    async def test_bulk_create_experiment_not_found(self):
        self.experiment_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(
                experiment_id="exp-999",
                measurements_data=[{"trait_id": "t-1", "value_numeric": 10}],
            )

    @pytest.mark.asyncio
    async def test_bulk_create_missing_trait_id(self):
        mock_exp = MagicMock(id="exp-1")
        self.experiment_repo.get_by_id = AsyncMock(return_value=mock_exp)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                experiment_id="exp-1",
                measurements_data=[{"value_numeric": 10}],
            )


class TestGetMeasurementUseCase:
    def setup_method(self):
        self.measurement_repo = MagicMock()
        self.use_case = GetMeasurementUseCase(self.measurement_repo)

    @pytest.mark.asyncio
    async def test_get_measurement_success(self):
        mock_m = MagicMock(id="m-1")
        self.measurement_repo.get_by_id = AsyncMock(return_value=mock_m)
        result = await self.use_case.execute("m-1")
        assert result.id == "m-1"

    @pytest.mark.asyncio
    async def test_get_measurement_not_found(self):
        self.measurement_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("m-999")


class TestListMeasurementsUseCase:
    def setup_method(self):
        self.measurement_repo = MagicMock()
        self.use_case = ListMeasurementsUseCase(self.measurement_repo)

    @pytest.mark.asyncio
    async def test_list_measurements_success(self):
        self.measurement_repo.list_by_experiment = AsyncMock(return_value=[])
        self.measurement_repo.count_by_experiment = AsyncMock(return_value=0)
        result = await self.use_case.execute(experiment_id="exp-1")
        assert result["items"] == []
        assert result["total"] == 0


class TestUpdateMeasurementUseCase:
    def setup_method(self):
        self.measurement_repo = MagicMock()
        self.use_case = UpdateMeasurementUseCase(self.measurement_repo)

    @pytest.mark.asyncio
    async def test_update_measurement_success(self):
        mock_m = MagicMock(id="m-1", value_numeric=10)
        self.measurement_repo.get_by_id = AsyncMock(return_value=mock_m)
        self.measurement_repo.update = AsyncMock(return_value=mock_m)
        result = await self.use_case.execute("m-1", value_numeric=42)
        assert result.value_numeric == 42

    @pytest.mark.asyncio
    async def test_update_measurement_not_found(self):
        self.measurement_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("m-999", value_numeric=10)


class TestDeleteMeasurementUseCase:
    def setup_method(self):
        self.measurement_repo = MagicMock()
        self.use_case = DeleteMeasurementUseCase(self.measurement_repo)

    @pytest.mark.asyncio
    async def test_delete_measurement_success(self):
        mock_m = MagicMock(id="m-1")
        self.measurement_repo.get_by_id = AsyncMock(return_value=mock_m)
        self.measurement_repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute("m-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_measurement_not_found(self):
        self.measurement_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("m-999")


class TestGetExperimentSummaryUseCase:
    def setup_method(self):
        self.measurement_repo = MagicMock()
        self.use_case = GetExperimentSummaryUseCase(self.measurement_repo)

    @pytest.mark.asyncio
    async def test_get_summary_success(self):
        summary = {
            "experiment_id": "exp-1",
            "total_measurements": 100,
            "trait_count": 5,
            "accession_count": 10,
            "traits_summary": [],
        }
        self.measurement_repo.get_experiment_summary = AsyncMock(return_value=summary)
        result = await self.use_case.execute("exp-1")
        assert result["total_measurements"] == 100
        assert result["trait_count"] == 5
