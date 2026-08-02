from abc import ABC, abstractmethod

from app.modules.phenotyping.domain.models import (
    ExperimentModel,
    MeasurementModel,
    TraitModel,
)


class ExperimentRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, experiment: ExperimentModel) -> ExperimentModel:
        pass

    @abstractmethod
    async def get_by_id(self, experiment_id: str) -> ExperimentModel | None:
        pass

    @abstractmethod
    async def list_experiments(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[ExperimentModel]:
        pass

    @abstractmethod
    async def count_experiments(
        self,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, experiment: ExperimentModel) -> ExperimentModel:
        pass

    @abstractmethod
    async def delete(self, experiment_id: str) -> bool:
        pass


class TraitRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, trait: TraitModel) -> TraitModel:
        pass

    @abstractmethod
    async def get_by_id(self, trait_id: str) -> TraitModel | None:
        pass

    @abstractmethod
    async def list_by_experiment(
        self, experiment_id: str, skip: int = 0, limit: int = 100
    ) -> list[TraitModel]:
        pass

    @abstractmethod
    async def count_by_experiment(self, experiment_id: str) -> int:
        pass

    @abstractmethod
    async def update(self, trait: TraitModel) -> TraitModel:
        pass

    @abstractmethod
    async def delete(self, trait_id: str) -> bool:
        pass


class MeasurementRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, measurement: MeasurementModel) -> MeasurementModel:
        pass

    @abstractmethod
    async def bulk_create(self, measurements: list[MeasurementModel]) -> list[MeasurementModel]:
        pass

    @abstractmethod
    async def get_by_id(self, measurement_id: str) -> MeasurementModel | None:
        pass

    @abstractmethod
    async def list_by_experiment(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        trait_id: str | None = None,
        accession_id: str | None = None,
    ) -> list[MeasurementModel]:
        pass

    @abstractmethod
    async def count_by_experiment(
        self,
        experiment_id: str,
        trait_id: str | None = None,
        accession_id: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, measurement: MeasurementModel) -> MeasurementModel:
        pass

    @abstractmethod
    async def delete(self, measurement_id: str) -> bool:
        pass

    @abstractmethod
    async def get_experiment_summary(self, experiment_id: str) -> dict:
        pass
