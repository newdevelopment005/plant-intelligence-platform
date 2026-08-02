from abc import ABC, abstractmethod

from app.modules.genomics.domain.models import (
    GeneAnnotationModel,
    SequenceModel,
    VariantModel,
)


class SequenceRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, sequence: SequenceModel) -> SequenceModel:
        pass

    @abstractmethod
    async def get_by_id(self, sequence_id: str) -> SequenceModel | None:
        pass

    @abstractmethod
    async def list_sequences(
        self,
        skip: int = 0,
        limit: int = 20,
        sequence_type: str | None = None,
        species_id: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[SequenceModel]:
        pass

    @abstractmethod
    async def count_sequences(
        self,
        sequence_type: str | None = None,
        species_id: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, sequence: SequenceModel) -> SequenceModel:
        pass

    @abstractmethod
    async def delete(self, sequence_id: str) -> bool:
        pass


class VariantRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, variant: VariantModel) -> VariantModel:
        pass

    @abstractmethod
    async def bulk_create(self, variants: list[VariantModel]) -> list[VariantModel]:
        pass

    @abstractmethod
    async def get_by_id(self, variant_id: str) -> VariantModel | None:
        pass

    @abstractmethod
    async def list_by_sequence(
        self,
        sequence_id: str,
        skip: int = 0,
        limit: int = 100,
        chromosome: str | None = None,
        variant_type: str | None = None,
        gene_name: str | None = None,
    ) -> list[VariantModel]:
        pass

    @abstractmethod
    async def count_by_sequence(
        self,
        sequence_id: str,
        chromosome: str | None = None,
        variant_type: str | None = None,
        gene_name: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def search(
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
    ) -> list[VariantModel]:
        pass

    @abstractmethod
    async def update(self, variant: VariantModel) -> VariantModel:
        pass

    @abstractmethod
    async def delete(self, variant_id: str) -> bool:
        pass


class GeneAnnotationRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, annotation: GeneAnnotationModel) -> GeneAnnotationModel:
        pass

    @abstractmethod
    async def get_by_id(self, annotation_id: str) -> GeneAnnotationModel | None:
        pass

    @abstractmethod
    async def list_by_sequence(
        self,
        sequence_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> list[GeneAnnotationModel]:
        pass

    @abstractmethod
    async def count_by_sequence(
        self,
        sequence_id: str,
        search: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def search_by_gene(
        self,
        sequence_id: str,
        gene_symbol: str,
    ) -> GeneAnnotationModel | None:
        pass

    @abstractmethod
    async def update(self, annotation: GeneAnnotationModel) -> GeneAnnotationModel:
        pass

    @abstractmethod
    async def delete(self, annotation_id: str) -> bool:
        pass
