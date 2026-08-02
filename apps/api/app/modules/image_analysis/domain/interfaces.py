from abc import ABC, abstractmethod

from app.modules.image_analysis.domain.models import (
    AnalysisResultModel,
    ImageAnalysisJobModel,
    PlantImageModel,
)


class PlantImageRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, image: PlantImageModel) -> PlantImageModel: ...

    @abstractmethod
    async def get_by_id(self, image_id: str) -> PlantImageModel | None: ...

    @abstractmethod
    async def list_images(
        self,
        skip: int = 0,
        limit: int = 20,
        image_type: str | None = None,
        species: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[PlantImageModel]: ...

    @abstractmethod
    async def count_images(
        self,
        image_type: str | None = None,
        species: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, image: PlantImageModel) -> PlantImageModel: ...

    @abstractmethod
    async def delete(self, image_id: str) -> bool: ...


class ImageAnalysisJobRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, job: ImageAnalysisJobModel) -> ImageAnalysisJobModel: ...

    @abstractmethod
    async def get_by_id(self, job_id: str) -> ImageAnalysisJobModel | None: ...

    @abstractmethod
    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 20,
        image_id: str | None = None,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
    ) -> list[ImageAnalysisJobModel]: ...

    @abstractmethod
    async def count_jobs(
        self,
        image_id: str | None = None,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, job: ImageAnalysisJobModel) -> ImageAnalysisJobModel: ...

    @abstractmethod
    async def delete(self, job_id: str) -> bool: ...


class AnalysisResultRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, result: AnalysisResultModel) -> AnalysisResultModel: ...

    @abstractmethod
    async def get_by_id(self, result_id: str) -> AnalysisResultModel | None: ...

    @abstractmethod
    async def list_by_job(
        self, job_id: str, skip: int = 0, limit: int = 100
    ) -> list[AnalysisResultModel]: ...

    @abstractmethod
    async def count_by_job(self, job_id: str) -> int: ...

    @abstractmethod
    async def delete(self, result_id: str) -> bool: ...
