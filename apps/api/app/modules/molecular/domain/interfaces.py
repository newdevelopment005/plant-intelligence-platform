from abc import ABC, abstractmethod

from app.modules.molecular.domain.models import (
    ConstructModel,
    MoleculeExperimentModel,
    PrimerModel,
)


class MoleculeExperimentRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, experiment: MoleculeExperimentModel) -> MoleculeExperimentModel:
        pass

    @abstractmethod
    async def get_by_id(self, experiment_id: str) -> MoleculeExperimentModel | None:
        pass

    @abstractmethod
    async def list_experiments(
        self,
        skip: int = 0,
        limit: int = 20,
        experiment_type: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[MoleculeExperimentModel]:
        pass

    @abstractmethod
    async def count_experiments(
        self,
        experiment_type: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, experiment: MoleculeExperimentModel) -> MoleculeExperimentModel:
        pass

    @abstractmethod
    async def delete(self, experiment_id: str) -> bool:
        pass


class PrimerRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, primer: PrimerModel) -> PrimerModel:
        pass

    @abstractmethod
    async def get_by_id(self, primer_id: str) -> PrimerModel | None:
        pass

    @abstractmethod
    async def list_by_experiment(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        primer_type: str | None = None,
        search: str | None = None,
    ) -> list[PrimerModel]:
        pass

    @abstractmethod
    async def count_by_experiment(
        self,
        experiment_id: str,
        primer_type: str | None = None,
        search: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, primer: PrimerModel) -> PrimerModel:
        pass

    @abstractmethod
    async def delete(self, primer_id: str) -> bool:
        pass


class ConstructRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, construct: ConstructModel) -> ConstructModel:
        pass

    @abstractmethod
    async def get_by_id(self, construct_id: str) -> ConstructModel | None:
        pass

    @abstractmethod
    async def list_by_experiment(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        construct_type: str | None = None,
        search: str | None = None,
    ) -> list[ConstructModel]:
        pass

    @abstractmethod
    async def count_by_experiment(
        self,
        experiment_id: str,
        construct_type: str | None = None,
        search: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, construct: ConstructModel) -> ConstructModel:
        pass

    @abstractmethod
    async def delete(self, construct_id: str) -> bool:
        pass
