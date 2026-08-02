from abc import ABC, abstractmethod

from app.modules.reporting.domain.models import ReportModel, ReportTemplateModel


class ReportRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, report: ReportModel) -> ReportModel: ...

    @abstractmethod
    async def get_by_id(self, report_id: str) -> ReportModel | None: ...

    @abstractmethod
    async def list_reports(
        self,
        skip: int = 0,
        limit: int = 20,
        report_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[ReportModel]: ...

    @abstractmethod
    async def count_reports(
        self,
        report_type: str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, report: ReportModel) -> ReportModel: ...

    @abstractmethod
    async def delete(self, report_id: str) -> bool: ...


class ReportTemplateRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, template: ReportTemplateModel) -> ReportTemplateModel: ...

    @abstractmethod
    async def get_by_id(self, template_id: str) -> ReportTemplateModel | None: ...

    @abstractmethod
    async def list_templates(
        self,
        skip: int = 0,
        limit: int = 20,
        report_type: str | None = None,
        search: str | None = None,
    ) -> list[ReportTemplateModel]: ...

    @abstractmethod
    async def count_templates(
        self,
        report_type: str | None = None,
        search: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, template: ReportTemplateModel) -> ReportTemplateModel: ...

    @abstractmethod
    async def delete(self, template_id: str) -> bool: ...
