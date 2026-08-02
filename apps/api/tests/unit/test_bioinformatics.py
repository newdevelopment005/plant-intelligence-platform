from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.bioinformatics.api.schemas import (
    AnalysisJobDetailResponse,
    AnalysisJobResponse,
    CreateAnalysisJobRequest,
    CreatePipelineTemplateRequest,
    PaginatedAnalysisJobsResponse,
    PaginatedPipelineTemplatesResponse,
    PipelineTemplateResponse,
    UpdateAnalysisJobRequest,
    UpdatePipelineTemplateRequest,
)
from app.modules.bioinformatics.domain.interfaces import (
    AnalysisJobRepositoryInterface,
    PipelineTemplateRepositoryInterface,
)
from app.modules.bioinformatics.domain.use_cases import (
    CancelAnalysisJobUseCase,
    CreateAnalysisJobUseCase,
    CreatePipelineTemplateUseCase,
    DeleteAnalysisJobUseCase,
    DeletePipelineTemplateUseCase,
    GetAnalysisJobUseCase,
    GetPipelineTemplateUseCase,
    ListAnalysisJobsUseCase,
    ListPipelineTemplatesUseCase,
    UpdateAnalysisJobUseCase,
    UpdatePipelineTemplateUseCase,
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


def _make_job(**overrides):
    defaults = {
        "id": "job-1",
        "name": "Test Alignment",
        "description": "Align sequences",
        "analysis_type": "alignment",
        "status": "pending",
        "priority": "normal",
        "input_data": {"sequences": ["ATCG"]},
        "parameters": None,
        "result_data": None,
        "output_files": None,
        "error_message": None,
        "progress_percent": None,
        "started_at": None,
        "completed_at": None,
        "runtime_seconds": None,
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
        "name": "Default Alignment",
        "description": "Standard alignment pipeline",
        "analysis_type": "alignment",
        "steps": [{"step": 1, "tool": "bwa"}],
        "default_parameters": {"threads": 4},
        "required_inputs": ["sequences"],
        "version": "1.0",
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
    def test_job_interface_methods(self):
        methods = ["create", "get_by_id", "list_jobs", "count_jobs", "update", "delete"]
        for m in methods:
            assert hasattr(AnalysisJobRepositoryInterface, m)

    def test_template_interface_methods(self):
        methods = ["create", "get_by_id", "list_templates", "count_templates", "update", "delete"]
        for m in methods:
            assert hasattr(PipelineTemplateRepositoryInterface, m)


# ────────────────────────── CreateAnalysisJobUseCase ──────────────────
class TestCreateAnalysisJobUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        job = _make_job()
        repo = make_mock_repo(create=lambda: job)
        uc = CreateAnalysisJobUseCase(job_repo=repo)
        result = await uc.execute(
            name="My Job", analysis_type="alignment", user_id="user-1",
            input_data={"seq": "ATCG"}, priority="high",
        )
        assert result.name == "Test Alignment"
        repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        repo = make_mock_repo()
        uc = CreateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="name is required"):
            await uc.execute(name="  ", analysis_type="alignment", user_id="u1", input_data={"x": 1})

    @pytest.mark.asyncio
    async def test_long_name_raises(self):
        repo = make_mock_repo()
        uc = CreateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="less than 500"):
            await uc.execute(name="x" * 501, analysis_type="alignment", user_id="u1", input_data={"x": 1})

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        repo = make_mock_repo()
        uc = CreateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Invalid analysis type"):
            await uc.execute(name="Job", analysis_type="invalid", user_id="u1", input_data={"x": 1})

    @pytest.mark.asyncio
    async def test_invalid_priority_raises(self):
        repo = make_mock_repo()
        uc = CreateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Invalid priority"):
            await uc.execute(name="Job", analysis_type="alignment", user_id="u1", input_data={"x": 1}, priority="bogus")

    @pytest.mark.asyncio
    async def test_no_input_data_raises(self):
        repo = make_mock_repo()
        uc = CreateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Input data is required"):
            await uc.execute(name="Job", analysis_type="alignment", user_id="u1")


# ────────────────────────── GetAnalysisJobUseCase ─────────────────────
class TestGetAnalysisJobUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        job = _make_job()
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = GetAnalysisJobUseCase(job_repo=repo)
        result = await uc.execute("job-1")
        assert result.id == "job-1"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = GetAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing")


# ────────────────────────── ListAnalysisJobsUseCase ───────────────────
class TestListAnalysisJobsUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        job = _make_job()
        repo = make_mock_repo(list_jobs=lambda: [job], count_jobs=lambda: 1)
        uc = ListAnalysisJobsUseCase(job_repo=repo)
        result = await uc.execute(user_id="user-1")
        assert result["total"] == 1
        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_invalid_status_raises(self):
        repo = make_mock_repo()
        uc = ListAnalysisJobsUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Invalid status"):
            await uc.execute(status="bogus")


# ────────────────────────── UpdateAnalysisJobUseCase ──────────────────
class TestUpdateAnalysisJobUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        job = _make_job()
        repo = make_mock_repo(get_by_id=lambda eid: job, update=lambda j: j)
        uc = UpdateAnalysisJobUseCase(job_repo=repo)
        result = await uc.execute("job-1", "user-1", name="New Name")
        assert result.name == "New Name"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = UpdateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1", name="x")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        job = _make_job(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = UpdateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("job-1", "user-2", name="x")

    @pytest.mark.asyncio
    async def test_running_job_raises(self):
        job = _make_job(status="running")
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = UpdateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Only pending or failed"):
            await uc.execute("job-1", "user-1", name="x")

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        job = _make_job()
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = UpdateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="cannot be empty"):
            await uc.execute("job-1", "user-1", name="  ")

    @pytest.mark.asyncio
    async def test_invalid_priority_raises(self):
        job = _make_job()
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = UpdateAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Invalid priority"):
            await uc.execute("job-1", "user-1", priority="bogus")


# ────────────────────────── CancelAnalysisJobUseCase ──────────────────
class TestCancelAnalysisJobUseCase:
    @pytest.mark.asyncio
    async def test_success_pending(self):
        job = _make_job(status="pending")
        repo = make_mock_repo(get_by_id=lambda eid: job, update=lambda j: j)
        uc = CancelAnalysisJobUseCase(job_repo=repo)
        result = await uc.execute("job-1", "user-1")
        assert result.status == "cancelled"

    @pytest.mark.asyncio
    async def test_success_running(self):
        job = _make_job(status="running")
        repo = make_mock_repo(get_by_id=lambda eid: job, update=lambda j: j)
        uc = CancelAnalysisJobUseCase(job_repo=repo)
        result = await uc.execute("job-1", "user-1")
        assert result.status == "cancelled"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = CancelAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        job = _make_job(created_by="user-1", status="pending")
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = CancelAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("job-1", "user-2")

    @pytest.mark.asyncio
    async def test_completed_job_raises(self):
        job = _make_job(status="completed")
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = CancelAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Only pending or running"):
            await uc.execute("job-1", "user-1")


# ────────────────────────── DeleteAnalysisJobUseCase ──────────────────
class TestDeleteAnalysisJobUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        job = _make_job()
        repo = make_mock_repo(get_by_id=lambda eid: job, delete=lambda eid: True)
        uc = DeleteAnalysisJobUseCase(job_repo=repo)
        result = await uc.execute("job-1", "user-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = DeleteAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        job = _make_job(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = DeleteAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("job-1", "user-2")

    @pytest.mark.asyncio
    async def test_running_job_raises(self):
        job = _make_job(status="running")
        repo = make_mock_repo(get_by_id=lambda eid: job)
        uc = DeleteAnalysisJobUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Cannot delete a running"):
            await uc.execute("job-1", "user-1")


# ────────────────────────── CreatePipelineTemplateUseCase ─────────────
class TestCreatePipelineTemplateUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(create=lambda: tpl)
        uc = CreatePipelineTemplateUseCase(template_repo=repo)
        result = await uc.execute(
            name="My Pipeline", analysis_type="alignment", user_id="user-1",
        )
        assert result.name == "Default Alignment"

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        repo = make_mock_repo()
        uc = CreatePipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="name is required"):
            await uc.execute(name="  ", analysis_type="alignment", user_id="u1")

    @pytest.mark.asyncio
    async def test_long_name_raises(self):
        repo = make_mock_repo()
        uc = CreatePipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="less than 255"):
            await uc.execute(name="x" * 256, analysis_type="alignment", user_id="u1")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        repo = make_mock_repo()
        uc = CreatePipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="Invalid analysis type"):
            await uc.execute(name="Tpl", analysis_type="invalid", user_id="u1")


# ────────────────────────── GetPipelineTemplateUseCase ────────────────
class TestGetPipelineTemplateUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(get_by_id=lambda eid: tpl)
        uc = GetPipelineTemplateUseCase(template_repo=repo)
        result = await uc.execute("tpl-1")
        assert result.id == "tpl-1"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = GetPipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing")


# ────────────────────────── ListPipelineTemplatesUseCase ──────────────
class TestListPipelineTemplatesUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(list_templates=lambda: [tpl], count_templates=lambda: 1)
        uc = ListPipelineTemplatesUseCase(template_repo=repo)
        result = await uc.execute()
        assert result["total"] == 1


# ────────────────────────── UpdatePipelineTemplateUseCase ─────────────
class TestUpdatePipelineTemplateUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(get_by_id=lambda eid: tpl, update=lambda t: t)
        uc = UpdatePipelineTemplateUseCase(template_repo=repo)
        result = await uc.execute("tpl-1", "user-1", name="New Name")
        assert result.name == "New Name"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = UpdatePipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1", name="x")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        tpl = _make_template(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: tpl)
        uc = UpdatePipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("tpl-1", "user-2", name="x")

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        tpl = _make_template()
        repo = make_mock_repo(get_by_id=lambda eid: tpl)
        uc = UpdatePipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="cannot be empty"):
            await uc.execute("tpl-1", "user-1", name="  ")


# ────────────────────────── DeletePipelineTemplateUseCase ─────────────
class TestDeletePipelineTemplateUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        tpl = _make_template()
        repo = make_mock_repo(get_by_id=lambda eid: tpl, delete=lambda eid: True)
        uc = DeletePipelineTemplateUseCase(template_repo=repo)
        result = await uc.execute("tpl-1", "user-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = DeletePipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        tpl = _make_template(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: tpl)
        uc = DeletePipelineTemplateUseCase(template_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("tpl-1", "user-2")


# ────────────────────────── Schema Validation ─────────────────────────
class TestSchemaValidation:
    def test_create_job_request(self):
        req = CreateAnalysisJobRequest(
            name="Align", analysis_type="alignment", input_data={"seq": "ATCG"},
        )
        assert req.priority == "normal"

    def test_create_job_request_custom_priority(self):
        req = CreateAnalysisJobRequest(
            name="Align", analysis_type="blast", input_data={"q": "x"}, priority="urgent",
        )
        assert req.priority == "urgent"

    def test_update_job_request(self):
        req = UpdateAnalysisJobRequest(name="New")
        assert req.name == "New"

    def test_create_template_request(self):
        req = CreatePipelineTemplateRequest(
            name="Pipeline", analysis_type="phylogenetics",
        )
        assert req.analysis_type == "phylogenetics"

    def test_update_template_request(self):
        req = UpdatePipelineTemplateRequest(name="Updated")
        assert req.name == "Updated"

    def test_job_response(self):
        resp = AnalysisJobResponse(
            id="j1", name="Test", analysis_type="alignment", status="pending",
            priority="normal", created_by="u1",
            created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z",
        )
        assert resp.id == "j1"

    def test_job_detail_response(self):
        resp = AnalysisJobDetailResponse(
            id="j1", name="Test", analysis_type="alignment", status="pending",
            priority="normal", created_by="u1", input_data={"seq": "ATCG"},
            created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z",
        )
        assert resp.input_data == {"seq": "ATCG"}

    def test_template_response(self):
        resp = PipelineTemplateResponse(
            id="t1", name="Pipe", analysis_type="blast", version="1.0",
            is_active=True, created_by="u1",
            created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z",
        )
        assert resp.version == "1.0"

    def test_paginated_jobs_response(self):
        resp = PaginatedAnalysisJobsResponse(items=[], total=0, skip=0, limit=20)
        assert resp.total == 0

    def test_paginated_templates_response(self):
        resp = PaginatedPipelineTemplatesResponse(items=[], total=0, skip=0, limit=20)
        assert resp.total == 0


# ────────────────────────── Integration Tests ─────────────────────────
class TestBioinformaticsModuleIntegration:
    def test_module_has_correct_structure(self):
        from app.modules.bioinformatics.api import schemas
        from app.modules.bioinformatics.api.router import router
        from app.modules.bioinformatics.domain import interfaces, models

        assert hasattr(models, "AnalysisJobModel")
        assert hasattr(models, "PipelineTemplateModel")
        assert hasattr(interfaces, "AnalysisJobRepositoryInterface")
        assert hasattr(interfaces, "PipelineTemplateRepositoryInterface")
        assert hasattr(schemas, "CreateAnalysisJobRequest")
        assert router is not None

    def test_router_has_all_endpoints(self):
        from app.modules.bioinformatics.api.router import router
        routes = {r.path for r in router.routes}
        expected = [
            "/api/v1/bioinformatics/jobs",
            "/api/v1/bioinformatics/jobs/{job_id}",
            "/api/v1/bioinformatics/jobs/{job_id}/cancel",
            "/api/v1/bioinformatics/templates",
            "/api/v1/bioinformatics/templates/{template_id}",
        ]
        for ep in expected:
            assert ep in routes, f"Missing endpoint: {ep}"

    def test_all_use_case_classes_exist(self):
        from app.modules.bioinformatics.domain import use_cases
        expected = [
            "CreateAnalysisJobUseCase", "GetAnalysisJobUseCase",
            "ListAnalysisJobsUseCase", "UpdateAnalysisJobUseCase",
            "CancelAnalysisJobUseCase", "DeleteAnalysisJobUseCase",
            "CreatePipelineTemplateUseCase", "GetPipelineTemplateUseCase",
            "ListPipelineTemplatesUseCase", "UpdatePipelineTemplateUseCase",
            "DeletePipelineTemplateUseCase",
        ]
        for name in expected:
            assert hasattr(use_cases, name), f"Missing use case: {name}"

    def test_infrastructure_repos_exist(self):
        from app.modules.bioinformatics.infrastructure import job_repository, template_repository
        assert hasattr(job_repository, "AnalysisJobRepository")
        assert hasattr(template_repository, "PipelineTemplateRepository")
