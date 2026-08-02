from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.reporting.api.schemas import (
    CreateReportRequest,
    CreateTemplateRequest,
    PaginatedReportsResponse,
    PaginatedTemplatesResponse,
    ReportResponse,
    TemplateResponse,
    UpdateReportRequest,
    UpdateTemplateRequest,
)
from app.modules.reporting.domain.interfaces import (
    ReportRepositoryInterface,
    ReportTemplateRepositoryInterface,
)
from app.modules.reporting.domain.use_cases import (
    CreateReportUseCase,
    CreateTemplateUseCase,
    DeleteReportUseCase,
    DeleteTemplateUseCase,
    GetReportUseCase,
    GetTemplateUseCase,
    ListReportsUseCase,
    ListTemplatesUseCase,
    UpdateReportUseCase,
    UpdateTemplateUseCase,
)


def make_mock_repo(**methods):
    repo = MagicMock(name="MockRepo")
    for method_name, value in methods.items():
        if callable(value):
            try:
                result = value()
                setattr(repo, method_name, AsyncMock(return_value=result))
            except TypeError:
                setattr(repo, method_name, AsyncMock(side_effect=value))
        else:
            setattr(repo, method_name, AsyncMock(return_value=value))
    return repo


def _make_report(**overrides):
    defaults = {
        "id": "rpt-1",
        "name": "Test Report",
        "description": "A report",
        "report_type": "phenotyping",
        "status": "pending",
        "format": "pdf",
        "data_source": "phenotyping",
        "parameters": None,
        "file_url": None,
        "file_size_bytes": None,
        "error_message": None,
        "tags": ["test"],
        "project_id": "proj-1",
        "created_by": "user-1",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _make_template(**overrides):
    defaults = {
        "id": "tpl-1",
        "name": "Default Report",
        "description": "Standard report",
        "report_type": "phenotyping",
        "default_format": "pdf",
        "data_source": "phenotyping",
        "layout": None,
        "default_parameters": None,
        "is_active": True,
        "tags": ["default"],
        "created_by": "user-1",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


# ────────────────────────── Interfaces ────────────────────────────────
class TestInterfaces:
    def test_report_interface_methods(self):
        methods = ["create", "get_by_id", "list_reports", "count_reports", "update", "delete"]
        for m in methods:
            assert hasattr(ReportRepositoryInterface, m)

    def test_template_interface_methods(self):
        methods = ["create", "get_by_id", "list_templates", "count_templates", "update", "delete"]
        for m in methods:
            assert hasattr(ReportTemplateRepositoryInterface, m)


# ────────────────────────── CreateReportUseCase ──────────────────────
class TestCreateReportUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        rpt = _make_report()
        repo = make_mock_repo(create=lambda: rpt)
        uc = CreateReportUseCase(report_repo=repo)
        result = await uc.execute(
            name="My Report", report_type="phenotyping", user_id="user-1",
            format="pdf", project_id="proj-1",
        )
        assert result.name == "Test Report"
        repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        repo = make_mock_repo()
        uc = CreateReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="name is required"):
            await uc.execute(name="  ", report_type="phenotyping", user_id="u1")

    @pytest.mark.asyncio
    async def test_long_name_raises(self):
        repo = make_mock_repo()
        uc = CreateReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="less than 500"):
            await uc.execute(name="x" * 501, report_type="phenotyping", user_id="u1")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        repo = make_mock_repo()
        uc = CreateReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="Invalid report type"):
            await uc.execute(name="Report", report_type="invalid", user_id="u1")

    @pytest.mark.asyncio
    async def test_invalid_format_raises(self):
        repo = make_mock_repo()
        uc = CreateReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="Invalid format"):
            await uc.execute(name="Report", report_type="phenotyping", user_id="u1", format="bogus")


# ────────────────────────── GetReportUseCase ──────────────────────────
class TestGetReportUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        rpt = _make_report()
        repo = make_mock_repo(get_by_id=lambda eid: rpt)
        uc = GetReportUseCase(report_repo=repo)
        result = await uc.execute("rpt-1")
        assert result.id == "rpt-1"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = GetReportUseCase(report_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing")


# ────────────────────────── ListReportsUseCase ────────────────────────
class TestListReportsUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        rpt = _make_report()
        repo = make_mock_repo(list_reports=lambda: [rpt], count_reports=lambda: 1)
        uc = ListReportsUseCase(report_repo=repo)
        result = await uc.execute(user_id="user-1")
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_invalid_status_raises(self):
        repo = make_mock_repo()
        uc = ListReportsUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="Invalid status"):
            await uc.execute(status="bogus")


# ────────────────────────── UpdateReportUseCase ───────────────────────
class TestUpdateReportUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        rpt = _make_report()
        repo = make_mock_repo(get_by_id=lambda eid: rpt, update=lambda r: r)
        uc = UpdateReportUseCase(report_repo=repo)
        result = await uc.execute("rpt-1", "user-1", name="New Name")
        assert result.name == "New Name"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = UpdateReportUseCase(report_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1", name="x")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        rpt = _make_report(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: rpt)
        uc = UpdateReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("rpt-1", "user-2", name="x")

    @pytest.mark.asyncio
    async def test_generating_status_raises(self):
        rpt = _make_report(status="generating")
        repo = make_mock_repo(get_by_id=lambda eid: rpt)
        uc = UpdateReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="Only pending or failed"):
            await uc.execute("rpt-1", "user-1", name="x")

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        rpt = _make_report()
        repo = make_mock_repo(get_by_id=lambda eid: rpt)
        uc = UpdateReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="cannot be empty"):
            await uc.execute("rpt-1", "user-1", name="  ")


# ────────────────────────── DeleteReportUseCase ───────────────────────
class TestDeleteReportUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        rpt = _make_report()
        repo = make_mock_repo(get_by_id=lambda eid: rpt, delete=lambda eid: True)
        uc = DeleteReportUseCase(report_repo=repo)
        result = await uc.execute("rpt-1", "user-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = DeleteReportUseCase(report_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        rpt = _make_report(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: rpt)
        uc = DeleteReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("rpt-1", "user-2")

    @pytest.mark.asyncio
    async def test_generating_status_raises(self):
        rpt = _make_report(status="generating")
        repo = make_mock_repo(get_by_id=lambda eid: rpt)
        uc = DeleteReportUseCase(report_repo=repo)
        with pytest.raises(ValidationException, match="Cannot delete"):
            await uc.execute("rpt-1", "user-1")


# ────────────────────────── CreateTemplateUseCase ─────────────────────
class TestCreateTemplateUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(create=lambda: tpl)
        uc = CreateTemplateUseCase(template_repo=repo)
        result = await uc.execute(name="My Tpl", report_type="phenotyping", user_id="user-1")
        assert result.name == "Default Report"

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        repo = make_mock_repo()
        uc = CreateTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="name is required"):
            await uc.execute(name="  ", report_type="phenotyping", user_id="u1")

    @pytest.mark.asyncio
    async def test_long_name_raises(self):
        repo = make_mock_repo()
        uc = CreateTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="less than 255"):
            await uc.execute(name="x" * 256, report_type="phenotyping", user_id="u1")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        repo = make_mock_repo()
        uc = CreateTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="Invalid report type"):
            await uc.execute(name="Tpl", report_type="invalid", user_id="u1")


# ────────────────────────── GetTemplateUseCase ────────────────────────
class TestGetTemplateUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(get_by_id=lambda eid: tpl)
        uc = GetTemplateUseCase(template_repo=repo)
        result = await uc.execute("tpl-1")
        assert result.id == "tpl-1"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = GetTemplateUseCase(template_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing")


# ────────────────────────── ListTemplatesUseCase ──────────────────────
class TestListTemplatesUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(list_templates=lambda: [tpl], count_templates=lambda: 1)
        uc = ListTemplatesUseCase(template_repo=repo)
        result = await uc.execute()
        assert result["total"] == 1


# ────────────────────────── UpdateTemplateUseCase ─────────────────────
class TestUpdateTemplateUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(get_by_id=lambda eid: tpl, update=lambda t: t)
        uc = UpdateTemplateUseCase(template_repo=repo)
        result = await uc.execute("tpl-1", "user-1", name="New Name")
        assert result.name == "New Name"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = UpdateTemplateUseCase(template_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1", name="x")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        tpl = _make_template(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: tpl)
        uc = UpdateTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("tpl-1", "user-2", name="x")

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        tpl = _make_template()
        repo = make_mock_repo(get_by_id=lambda eid: tpl)
        uc = UpdateTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="cannot be empty"):
            await uc.execute("tpl-1", "user-1", name="  ")


# ────────────────────────── DeleteTemplateUseCase ─────────────────────
class TestDeleteTemplateUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(get_by_id=lambda eid: tpl, delete=lambda eid: True)
        uc = DeleteTemplateUseCase(template_repo=repo)
        result = await uc.execute("tpl-1", "user-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = DeleteTemplateUseCase(template_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        tpl = _make_template(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: tpl)
        uc = DeleteTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("tpl-1", "user-2")


# ────────────────────────── Schema Validation ─────────────────────────
class TestSchemaValidation:
    def test_create_report_request(self):
        req = CreateReportRequest(name="Report", report_type="phenotyping")
        assert req.format == "pdf"

    def test_create_report_request_custom_format(self):
        req = CreateReportRequest(name="Report", report_type="genotyping", format="csv")
        assert req.format == "csv"

    def test_update_report_request(self):
        req = UpdateReportRequest(name="New")
        assert req.name == "New"

    def test_create_template_request(self):
        req = CreateTemplateRequest(name="Template", report_type="experiment")
        assert req.default_format == "pdf"

    def test_update_template_request(self):
        req = UpdateTemplateRequest(name="Updated")
        assert req.name == "Updated"

    def test_report_response(self):
        resp = ReportResponse(
            id="r1", name="Report", report_type="phenotyping", status="pending",
            format="pdf", created_by="u1",
            created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z",
        )
        assert resp.status == "pending"

    def test_template_response(self):
        resp = TemplateResponse(
            id="t1", name="Tpl", report_type="phenotyping", default_format="pdf",
            is_active=True, created_by="u1",
            created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z",
        )
        assert resp.is_active is True

    def test_paginated_reports_response(self):
        resp = PaginatedReportsResponse(items=[], total=0, skip=0, limit=20)
        assert resp.total == 0

    def test_paginated_templates_response(self):
        resp = PaginatedTemplatesResponse(items=[], total=0, skip=0, limit=20)
        assert resp.total == 0


# ────────────────────────── Integration Tests ─────────────────────────
class TestReportingModuleIntegration:
    def test_module_has_correct_structure(self):
        from app.modules.reporting.api import schemas
        from app.modules.reporting.api.router import router
        from app.modules.reporting.domain import interfaces, models

        assert hasattr(models, "ReportModel")
        assert hasattr(models, "ReportTemplateModel")
        assert hasattr(interfaces, "ReportRepositoryInterface")
        assert hasattr(interfaces, "ReportTemplateRepositoryInterface")
        assert hasattr(schemas, "CreateReportRequest")
        assert router is not None

    def test_router_has_all_endpoints(self):
        from app.modules.reporting.api.router import router
        routes = {r.path for r in router.routes}
        expected = [
            "/api/v1/reports/",
            "/api/v1/reports/{report_id}",
            "/api/v1/reports/{report_id}/download",
            "/api/v1/reports/templates",
            "/api/v1/reports/templates/{template_id}",
        ]
        for ep in expected:
            assert ep in routes, f"Missing endpoint: {ep}"

    def test_all_use_case_classes_exist(self):
        from app.modules.reporting.domain import use_cases
        expected = [
            "CreateReportUseCase", "GetReportUseCase", "ListReportsUseCase",
            "UpdateReportUseCase", "DeleteReportUseCase",
            "CreateTemplateUseCase", "GetTemplateUseCase", "ListTemplatesUseCase",
            "UpdateTemplateUseCase", "DeleteTemplateUseCase",
        ]
        for name in expected:
            assert hasattr(use_cases, name), f"Missing use case: {name}"

    def test_infrastructure_repos_exist(self):
        from app.modules.reporting.infrastructure import report_repository, template_repository
        assert hasattr(report_repository, "ReportRepository")
        assert hasattr(template_repository, "ReportTemplateRepository")
