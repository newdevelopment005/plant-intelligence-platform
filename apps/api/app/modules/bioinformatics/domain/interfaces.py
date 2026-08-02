from abc import ABC, abstractmethod

from app.modules.bioinformatics.domain.models import AnalysisJobModel, PipelineTemplateModel


class AnalysisJobRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, job: AnalysisJobModel) -> AnalysisJobModel: ...

    @abstractmethod
    async def get_by_id(self, job_id: str) -> AnalysisJobModel | None: ...

    @abstractmethod
    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 20,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[AnalysisJobModel]: ...

    @abstractmethod
    async def count_jobs(
        self,
        analysis_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, job: AnalysisJobModel) -> AnalysisJobModel: ...

    @abstractmethod
    async def delete(self, job_id: str) -> bool: ...


class PipelineTemplateRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, template: PipelineTemplateModel) -> PipelineTemplateModel: ...

    @abstractmethod
    async def get_by_id(self, template_id: str) -> PipelineTemplateModel | None: ...

    @abstractmethod
    async def list_templates(
        self,
        skip: int = 0,
        limit: int = 20,
        analysis_type: str | None = None,
        search: str | None = None,
    ) -> list[PipelineTemplateModel]: ...

    @abstractmethod
    async def count_templates(
        self,
        analysis_type: str | None = None,
        search: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, template: PipelineTemplateModel) -> PipelineTemplateModel: ...

    @abstractmethod
    async def delete(self, template_id: str) -> bool: ...
