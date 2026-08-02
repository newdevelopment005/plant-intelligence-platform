from abc import ABC, abstractmethod

from app.modules.germplasm.domain.models import (
    AccessionModel,
    GermplasmFileModel,
    GermplasmImageModel,
    PassportDataModel,
    PedigreeModel,
    SeedStorageModel,
    SpeciesModel,
)


class SpeciesRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, species: SpeciesModel) -> SpeciesModel:
        pass

    @abstractmethod
    async def get_by_id(self, species_id: str) -> SpeciesModel | None:
        pass

    @abstractmethod
    async def get_by_scientific_name(self, scientific_name: str) -> SpeciesModel | None:
        pass

    @abstractmethod
    async def list_species(
        self, skip: int = 0, limit: int = 20, search: str | None = None
    ) -> list[SpeciesModel]:
        pass

    @abstractmethod
    async def count_species(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def update(self, species: SpeciesModel) -> SpeciesModel:
        pass

    @abstractmethod
    async def delete(self, species_id: str) -> bool:
        pass


class AccessionRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, accession: AccessionModel) -> AccessionModel:
        pass

    @abstractmethod
    async def get_by_id(self, accession_id: str) -> AccessionModel | None:
        pass

    @abstractmethod
    async def get_by_accession_number(self, accession_number: str) -> AccessionModel | None:
        pass

    @abstractmethod
    async def list_accessions(
        self,
        skip: int = 0,
        limit: int = 20,
        species_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[AccessionModel]:
        pass

    @abstractmethod
    async def count_accessions(
        self,
        species_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, accession: AccessionModel) -> AccessionModel:
        pass

    @abstractmethod
    async def delete(self, accession_id: str) -> bool:
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
        filters: dict | None = None,
    ) -> list[AccessionModel]:
        pass


class PassportDataRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, passport: PassportDataModel) -> PassportDataModel:
        pass

    @abstractmethod
    async def get_by_accession_id(self, accession_id: str) -> PassportDataModel | None:
        pass

    @abstractmethod
    async def update(self, passport: PassportDataModel) -> PassportDataModel:
        pass

    @abstractmethod
    async def delete(self, accession_id: str) -> bool:
        pass


class PedigreeRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, pedigree: PedigreeModel) -> PedigreeModel:
        pass

    @abstractmethod
    async def get_by_accession_id(self, accession_id: str) -> PedigreeModel | None:
        pass

    @abstractmethod
    async def get_ancestors(self, accession_id: str, depth: int = 3) -> list[PedigreeModel]:
        pass

    @abstractmethod
    async def get_descendants(self, accession_id: str, depth: int = 3) -> list[PedigreeModel]:
        pass

    @abstractmethod
    async def update(self, pedigree: PedigreeModel) -> PedigreeModel:
        pass

    @abstractmethod
    async def delete(self, accession_id: str) -> bool:
        pass


class SeedStorageRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, storage: SeedStorageModel) -> SeedStorageModel:
        pass

    @abstractmethod
    async def get_by_id(self, storage_id: str) -> SeedStorageModel | None:
        pass

    @abstractmethod
    async def list_by_accession(self, accession_id: str) -> list[SeedStorageModel]:
        pass

    @abstractmethod
    async def update(self, storage: SeedStorageModel) -> SeedStorageModel:
        pass

    @abstractmethod
    async def delete(self, storage_id: str) -> bool:
        pass


class GermplasmImageRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, image: GermplasmImageModel) -> GermplasmImageModel:
        pass

    @abstractmethod
    async def get_by_id(self, image_id: str) -> GermplasmImageModel | None:
        pass

    @abstractmethod
    async def list_by_accession(self, accession_id: str) -> list[GermplasmImageModel]:
        pass

    @abstractmethod
    async def delete(self, image_id: str) -> bool:
        pass


class GermplasmFileRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, file: GermplasmFileModel) -> GermplasmFileModel:
        pass

    @abstractmethod
    async def get_by_id(self, file_id: str) -> GermplasmFileModel | None:
        pass

    @abstractmethod
    async def list_by_accession(self, accession_id: str) -> list[GermplasmFileModel]:
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        pass
