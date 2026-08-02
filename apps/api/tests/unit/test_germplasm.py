import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.germplasm.domain.interfaces import (
    AccessionRepositoryInterface,
    PassportDataRepositoryInterface,
    PedigreeRepositoryInterface,
    SeedStorageRepositoryInterface,
    SpeciesRepositoryInterface,
)
from app.modules.germplasm.domain.models import (
    AccessionModel,
    PassportDataModel,
    PedigreeModel,
    SeedStorageModel,
    SpeciesModel,
)
from app.modules.germplasm.domain.use_cases import (
    CreateAccessionUseCase,
    CreatePassportDataUseCase,
    CreatePedigreeUseCase,
    CreateSeedStorageUseCase,
    CreateSpeciesUseCase,
    DeleteAccessionUseCase,
    DeleteSpeciesUseCase,
    GetAccessionUseCase,
    GetSpeciesUseCase,
    ListAccessionsUseCase,
    ListSpeciesUseCase,
    SearchAccessionsUseCase,
    UpdateAccessionUseCase,
    UpdateSpeciesUseCase,
)


class TestCreateSpeciesUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=SpeciesRepositoryInterface)
        self.use_case = CreateSpeciesUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_create_species_success(self):
        self.repo.get_by_scientific_name = AsyncMock(return_value=None)
        self.repo.create = AsyncMock(return_value=SpeciesModel(
            id="sp-1",
            common_name="Common wheat",
            scientific_name="Triticum aestivum",
            family="Poaceae",
        ))
        result = await self.use_case.execute(common_name="Common wheat", scientific_name="Triticum aestivum", family="Poaceae")
        assert result.common_name == "Common wheat"
        self.repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_species_duplicate_scientific_name(self):
        self.repo.get_by_scientific_name = AsyncMock(return_value=SpeciesModel(id="existing"))
        with pytest.raises(ConflictException):
            await self.use_case.execute(common_name="Wheat", scientific_name="Triticum aestivum")

    @pytest.mark.asyncio
    async def test_create_species_empty_common_name(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(common_name="", scientific_name="Triticum aestivum")

    @pytest.mark.asyncio
    async def test_create_species_empty_scientific_name(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(common_name="Wheat", scientific_name="")


class TestGetSpeciesUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=SpeciesRepositoryInterface)
        self.use_case = GetSpeciesUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_get_species_success(self):
        self.repo.get_by_id = AsyncMock(return_value=SpeciesModel(id="sp-1", common_name="Wheat"))
        result = await self.use_case.execute("sp-1")
        assert result.id == "sp-1"

    @pytest.mark.asyncio
    async def test_get_species_not_found(self):
        self.repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("nonexistent")


class TestListSpeciesUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=SpeciesRepositoryInterface)
        self.use_case = ListSpeciesUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_list_species_success(self):
        self.repo.list_species = AsyncMock(return_value=[])
        self.repo.count_species = AsyncMock(return_value=0)
        result = await self.use_case.execute()
        assert result["items"] == []
        assert result["total"] == 0


class TestUpdateSpeciesUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=SpeciesRepositoryInterface)
        self.use_case = UpdateSpeciesUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_update_species_success(self):
        species = SpeciesModel(id="sp-1", common_name="Wheat", scientific_name="Triticum aestivum")
        self.repo.get_by_id = AsyncMock(return_value=species)
        self.repo.get_by_scientific_name = AsyncMock(return_value=None)
        self.repo.update = AsyncMock(return_value=species)
        result = await self.use_case.execute("sp-1", common_name="Updated Wheat")
        assert result.common_name == "Updated Wheat"

    @pytest.mark.asyncio
    async def test_update_species_not_found(self):
        self.repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("nonexistent", common_name="X")


class TestDeleteSpeciesUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=SpeciesRepositoryInterface)
        self.use_case = DeleteSpeciesUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_delete_species_success(self):
        self.repo.get_by_id = AsyncMock(return_value=SpeciesModel(id="sp-1"))
        self.repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute("sp-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_species_not_found(self):
        self.repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("nonexistent")


class TestCreateAccessionUseCase:
    def setup_method(self):
        self.accession_repo = MagicMock(spec=AccessionRepositoryInterface)
        self.species_repo = MagicMock(spec=SpeciesRepositoryInterface)
        self.use_case = CreateAccessionUseCase(self.accession_repo, self.species_repo)

    @pytest.mark.asyncio
    async def test_create_accession_success(self):
        self.species_repo.get_by_id = AsyncMock(return_value=SpeciesModel(id="sp-1"))
        self.accession_repo.get_by_accession_number = AsyncMock(return_value=None)
        self.accession_repo.create = AsyncMock(return_value=AccessionModel(
            id="acc-1", accession_number="PI 123456", name="Wheat landrace",
            species_id="sp-1", availability_status="available", created_by="user-1",
        ))
        result = await self.use_case.execute(accession_number="PI 123456", species_id="sp-1", name="Wheat landrace", user_id="user-1")
        assert result.accession_number == "PI 123456"

    @pytest.mark.asyncio
    async def test_create_accession_duplicate_number(self):
        self.species_repo.get_by_id = AsyncMock(return_value=SpeciesModel(id="sp-1"))
        self.accession_repo.get_by_accession_number = AsyncMock(return_value=AccessionModel(id="existing"))
        with pytest.raises(ConflictException):
            await self.use_case.execute(accession_number="PI 123456", species_id="sp-1", name="Wheat", user_id="user-1")

    @pytest.mark.asyncio
    async def test_create_accession_species_not_found(self):
        self.species_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(accession_number="PI 123456", species_id="nonexistent", name="Wheat", user_id="user-1")

    @pytest.mark.asyncio
    async def test_create_accession_empty_number(self):
        self.species_repo.get_by_id = AsyncMock(return_value=SpeciesModel(id="sp-1"))
        with pytest.raises(ValidationException):
            await self.use_case.execute(accession_number="", species_id="sp-1", name="Wheat", user_id="user-1")


class TestGetAccessionUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=AccessionRepositoryInterface)
        self.use_case = GetAccessionUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_get_accession_success(self):
        self.repo.get_by_id = AsyncMock(return_value=AccessionModel(id="acc-1"))
        result = await self.use_case.execute("acc-1")
        assert result.id == "acc-1"

    @pytest.mark.asyncio
    async def test_get_accession_not_found(self):
        self.repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("nonexistent")


class TestListAccessionsUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=AccessionRepositoryInterface)
        self.use_case = ListAccessionsUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_list_accessions_success(self):
        self.repo.list_accessions = AsyncMock(return_value=[])
        self.repo.count_accessions = AsyncMock(return_value=0)
        result = await self.use_case.execute()
        assert result["items"] == []
        assert result["total"] == 0


class TestUpdateAccessionUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=AccessionRepositoryInterface)
        self.use_case = UpdateAccessionUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_update_accession_success(self):
        accession = AccessionModel(id="acc-1", created_by="user-1", name="Test")
        self.repo.get_by_id = AsyncMock(return_value=accession)
        self.repo.update = AsyncMock(return_value=accession)
        result = await self.use_case.execute("acc-1", "user-1", name="Updated")
        assert result.name == "Updated"

    @pytest.mark.asyncio
    async def test_update_accession_not_found(self):
        self.repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("nonexistent", "user-1", name="X")

    @pytest.mark.asyncio
    async def test_update_accession_forbidden(self):
        accession = AccessionModel(id="acc-1", created_by="user-2", name="Test")
        self.repo.get_by_id = AsyncMock(return_value=accession)
        with pytest.raises(ValidationException):
            await self.use_case.execute("acc-1", "user-1", name="X")


class TestDeleteAccessionUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=AccessionRepositoryInterface)
        self.use_case = DeleteAccessionUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_delete_accession_success(self):
        accession = AccessionModel(id="acc-1", created_by="user-1")
        self.repo.get_by_id = AsyncMock(return_value=accession)
        self.repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute("acc-1", "user-1")
        assert result is True


class TestSearchAccessionsUseCase:
    def setup_method(self):
        self.repo = MagicMock(spec=AccessionRepositoryInterface)
        self.use_case = SearchAccessionsUseCase(self.repo)

    @pytest.mark.asyncio
    async def test_search_accessions_success(self):
        self.repo.search = AsyncMock(return_value=[])
        result = await self.use_case.execute("wheat")
        assert result["items"] == []

    @pytest.mark.asyncio
    async def test_search_accessions_empty_query(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute("")


class TestCreatePassportDataUseCase:
    def setup_method(self):
        self.passport_repo = MagicMock(spec=PassportDataRepositoryInterface)
        self.accession_repo = MagicMock(spec=AccessionRepositoryInterface)
        self.use_case = CreatePassportDataUseCase(self.passport_repo, self.accession_repo)

    @pytest.mark.asyncio
    async def test_create_passport_success(self):
        self.accession_repo.get_by_id = AsyncMock(return_value=AccessionModel(id="acc-1"))
        self.passport_repo.get_by_accession_id = AsyncMock(return_value=None)
        self.passport_repo.create = AsyncMock(return_value=PassportDataModel(id="pp-1", accession_id="acc-1", institute_code="IRRI"))
        result = await self.use_case.execute(accession_id="acc-1", institute_code="IRRI")
        assert result.institute_code == "IRRI"

    @pytest.mark.asyncio
    async def test_create_passport_already_exists(self):
        self.accession_repo.get_by_id = AsyncMock(return_value=AccessionModel(id="acc-1"))
        self.passport_repo.get_by_accession_id = AsyncMock(return_value=PassportDataModel(id="existing"))
        with pytest.raises(ConflictException):
            await self.use_case.execute(accession_id="acc-1")


class TestCreatePedigreeUseCase:
    def setup_method(self):
        self.pedigree_repo = MagicMock(spec=PedigreeRepositoryInterface)
        self.accession_repo = MagicMock(spec=AccessionRepositoryInterface)
        self.use_case = CreatePedigreeUseCase(self.pedigree_repo, self.accession_repo)

    @pytest.mark.asyncio
    async def test_create_pedigree_success(self):
        self.accession_repo.get_by_id = AsyncMock(return_value=AccessionModel(id="acc-1"))
        self.pedigree_repo.get_by_accession_id = AsyncMock(return_value=None)
        self.pedigree_repo.create = AsyncMock(return_value=PedigreeModel(id="ped-1", accession_id="acc-1"))
        result = await self.use_case.execute(accession_id="acc-1")
        assert result.accession_id == "acc-1"


class TestCreateSeedStorageUseCase:
    def setup_method(self):
        self.storage_repo = MagicMock(spec=SeedStorageRepositoryInterface)
        self.accession_repo = MagicMock(spec=AccessionRepositoryInterface)
        self.use_case = CreateSeedStorageUseCase(self.storage_repo, self.accession_repo)

    @pytest.mark.asyncio
    async def test_create_storage_success(self):
        self.accession_repo.get_by_id = AsyncMock(return_value=AccessionModel(id="acc-1"))
        self.storage_repo.create = AsyncMock(return_value=SeedStorageModel(id="st-1", accession_id="acc-1", location="Vault A"))
        result = await self.use_case.execute(accession_id="acc-1", location="Vault A")
        assert result.location == "Vault A"

    @pytest.mark.asyncio
    async def test_create_storage_empty_location(self):
        self.accession_repo.get_by_id = AsyncMock(return_value=AccessionModel(id="acc-1"))
        with pytest.raises(ValidationException):
            await self.use_case.execute(accession_id="acc-1", location="")
