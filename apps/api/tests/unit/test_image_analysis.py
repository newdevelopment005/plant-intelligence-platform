from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.image_analysis.api.schemas import (
    AnalysisJobResponse,
    AnalysisResultResponse,
    CreateAnalysisJobRequest,
    ImageResponse,
    PaginatedAnalysisJobsResponse,
    PaginatedAnalysisResultsResponse,
    PaginatedImagesResponse,
    UpdateImageRequest,
    UploadImageRequest,
)
from app.modules.image_analysis.domain.interfaces import (
    AnalysisResultRepositoryInterface,
    ImageAnalysisJobRepositoryInterface,
    PlantImageRepositoryInterface,
)
from app.modules.image_analysis.domain.use_cases import (
    CreateAnalysisJobUseCase,
    DeleteImageUseCase,
    GetAnalysisJobUseCase,
    GetAnalysisResultsUseCase,
    GetImageUseCase,
    ListAnalysisJobsUseCase,
    ListImagesUseCase,
    UpdateImageUseCase,
    UploadImageUseCase,
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


def _make_image(**overrides):
    defaults = {
        "id": "img-1",
        "name": "Leaf Image 1",
        "description": "A leaf",
        "file_url": "http://example.com/img.jpg",
        "thumbnail_url": None,
        "file_size_bytes": 1024,
        "mime_type": "image/jpeg",
        "width": 800,
        "height": 600,
        "image_type": "leaf",
        "source_module": "germplasm",
        "source_id": "acc-1",
        "species": "Triticum aestivum",
        "tissue_type": "leaf",
        "growth_stage": "tillering",
        "magnification": None,
        "capture_date": None,
        "gps_latitude": None,
        "gps_longitude": None,
        "tags": ["drought"],
        "metadata_json": None,
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


def _make_job(**overrides):
    defaults = {
        "id": "job-1",
        "image_id": "img-1",
        "analysis_type": "disease_detection",
        "status": "pending",
        "parameters": None,
        "error_message": None,
        "started_at": None,
        "completed_at": None,
        "runtime_seconds": None,
        "model_version": None,
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


def _make_result(**overrides):
    defaults = {
        "id": "res-1",
        "job_id": "job-1",
        "result_type": "classification",
        "label": "healthy",
        "confidence": 0.95,
        "bbox": None,
        "measurements": None,
        "annotations": None,
        "raw_output": None,
        "created_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


# ────────────────────────── Interfaces ────────────────────────────────
class TestInterfaces:
    def test_image_interface_methods(self):
        methods = ["create", "get_by_id", "list_images", "count_images", "update", "delete"]
        for m in methods:
            assert hasattr(PlantImageRepositoryInterface, m)

    def test_job_interface_methods(self):
        methods = ["create", "get_by_id", "list_jobs", "count_jobs", "update", "delete"]
        for m in methods:
            assert hasattr(ImageAnalysisJobRepositoryInterface, m)

    def test_result_interface_methods(self):
        methods = ["create", "get_by_id", "list_by_job", "count_by_job", "delete"]
        for m in methods:
            assert hasattr(AnalysisResultRepositoryInterface, m)


# ────────────────────────── UploadImageUseCase ────────────────────────
class TestUploadImageUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        img = _make_image()
        repo = make_mock_repo(create=lambda: img)
        uc = UploadImageUseCase(image_repo=repo)
        result = await uc.execute(
            name="My Image", file_url="http://example.com/img.jpg",
            user_id="user-1", image_type="leaf", species="wheat",
        )
        assert result.name == "Leaf Image 1"
        repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        repo = make_mock_repo()
        uc = UploadImageUseCase(image_repo=repo)
        with pytest.raises(ValidationException, match="name is required"):
            await uc.execute(name="  ", file_url="http://x.com/img.jpg", user_id="u1")

    @pytest.mark.asyncio
    async def test_long_name_raises(self):
        repo = make_mock_repo()
        uc = UploadImageUseCase(image_repo=repo)
        with pytest.raises(ValidationException, match="less than 500"):
            await uc.execute(name="x" * 501, file_url="http://x.com/img.jpg", user_id="u1")

    @pytest.mark.asyncio
    async def test_no_file_url_raises(self):
        repo = make_mock_repo()
        uc = UploadImageUseCase(image_repo=repo)
        with pytest.raises(ValidationException, match="File URL is required"):
            await uc.execute(name="Image", file_url="  ", user_id="u1")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        repo = make_mock_repo()
        uc = UploadImageUseCase(image_repo=repo)
        with pytest.raises(ValidationException, match="Invalid image type"):
            await uc.execute(name="Image", file_url="http://x.com/img.jpg", user_id="u1", image_type="invalid")


# ────────────────────────── GetImageUseCase ───────────────────────────
class TestGetImageUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        img = _make_image()
        repo = make_mock_repo(get_by_id=lambda eid: img)
        uc = GetImageUseCase(image_repo=repo)
        result = await uc.execute("img-1")
        assert result.id == "img-1"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = GetImageUseCase(image_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing")


# ────────────────────────── ListImagesUseCase ─────────────────────────
class TestListImagesUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        img = _make_image()
        repo = make_mock_repo(list_images=lambda: [img], count_images=lambda: 1)
        uc = ListImagesUseCase(image_repo=repo)
        result = await uc.execute(user_id="user-1")
        assert result["total"] == 1
        assert len(result["items"]) == 1


# ────────────────────────── UpdateImageUseCase ────────────────────────
class TestUpdateImageUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        img = _make_image()
        repo = make_mock_repo(get_by_id=lambda eid: img, update=lambda i: i)
        uc = UpdateImageUseCase(image_repo=repo)
        result = await uc.execute("img-1", "user-1", species="rice")
        assert result.species == "rice"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = UpdateImageUseCase(image_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1", species="x")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        img = _make_image(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: img)
        uc = UpdateImageUseCase(image_repo=repo)
        with pytest.raises(ValidationException, match="Only the uploader"):
            await uc.execute("img-1", "user-2", species="x")

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        img = _make_image()
        repo = make_mock_repo(get_by_id=lambda eid: img)
        uc = UpdateImageUseCase(image_repo=repo)
        with pytest.raises(ValidationException, match="cannot be empty"):
            await uc.execute("img-1", "user-1", name="  ")


# ────────────────────────── DeleteImageUseCase ────────────────────────
class TestDeleteImageUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        img = _make_image()
        repo = make_mock_repo(get_by_id=lambda eid: img, delete=lambda eid: True)
        uc = DeleteImageUseCase(image_repo=repo)
        result = await uc.execute("img-1", "user-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = DeleteImageUseCase(image_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        img = _make_image(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: img)
        uc = DeleteImageUseCase(image_repo=repo)
        with pytest.raises(ValidationException, match="Only the uploader"):
            await uc.execute("img-1", "user-2")


# ────────────────────────── CreateAnalysisJobUseCase ──────────────────
class TestCreateAnalysisJobUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        img = _make_image()
        job = _make_job()
        image_repo = make_mock_repo(get_by_id=lambda eid: img)
        job_repo = make_mock_repo(create=lambda: job)
        uc = CreateAnalysisJobUseCase(job_repo=job_repo, image_repo=image_repo)
        result = await uc.execute(
            image_id="img-1", analysis_type="disease_detection", user_id="user-1",
        )
        assert result.analysis_type == "disease_detection"

    @pytest.mark.asyncio
    async def test_image_not_found(self):
        image_repo = make_mock_repo(get_by_id=lambda eid: None)
        job_repo = make_mock_repo()
        uc = CreateAnalysisJobUseCase(job_repo=job_repo, image_repo=image_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(image_id="missing", analysis_type="disease_detection", user_id="u1")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        img = _make_image()
        image_repo = make_mock_repo(get_by_id=lambda eid: img)
        job_repo = make_mock_repo()
        uc = CreateAnalysisJobUseCase(job_repo=job_repo, image_repo=image_repo)
        with pytest.raises(ValidationException, match="Invalid analysis type"):
            await uc.execute(image_id="img-1", analysis_type="invalid", user_id="u1")


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
        result = await uc.execute(image_id="img-1")
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_invalid_status_raises(self):
        repo = make_mock_repo()
        uc = ListAnalysisJobsUseCase(job_repo=repo)
        with pytest.raises(ValidationException, match="Invalid status"):
            await uc.execute(status="bogus")


# ────────────────────────── GetAnalysisResultsUseCase ─────────────────
class TestGetAnalysisResultsUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        job = _make_job()
        res = _make_result()
        job_repo = make_mock_repo(get_by_id=lambda eid: job)
        result_repo = make_mock_repo(list_by_job=lambda: [res], count_by_job=lambda: 1)
        uc = GetAnalysisResultsUseCase(job_repo=job_repo, result_repo=result_repo)
        result = await uc.execute(job_id="job-1")
        assert result["total"] == 1
        assert result["items"][0]["label"] == "healthy"

    @pytest.mark.asyncio
    async def test_job_not_found(self):
        job_repo = make_mock_repo(get_by_id=lambda eid: None)
        result_repo = make_mock_repo()
        uc = GetAnalysisResultsUseCase(job_repo=job_repo, result_repo=result_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(job_id="missing")


# ────────────────────────── Schema Validation ─────────────────────────
class TestSchemaValidation:
    def test_upload_image_request(self):
        req = UploadImageRequest(name="Leaf", file_url="http://x.com/img.jpg")
        assert req.image_type == "general"

    def test_upload_image_request_custom_type(self):
        req = UploadImageRequest(name="Micro", file_url="http://x.com/img.jpg", image_type="microscopy")
        assert req.image_type == "microscopy"

    def test_update_image_request(self):
        req = UpdateImageRequest(species="rice")
        assert req.species == "rice"

    def test_create_analysis_job_request(self):
        req = CreateAnalysisJobRequest(image_id="i1", analysis_type="disease_detection")
        assert req.analysis_type == "disease_detection"

    def test_image_response(self):
        resp = ImageResponse(
            id="i1", name="Leaf", file_url="http://x.com/img.jpg", image_type="leaf",
            created_by="u1", created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z",
        )
        assert resp.id == "i1"

    def test_analysis_job_response(self):
        resp = AnalysisJobResponse(
            id="j1", image_id="i1", analysis_type="disease_detection", status="pending",
            created_by="u1", created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z",
        )
        assert resp.status == "pending"

    def test_analysis_result_response(self):
        resp = AnalysisResultResponse(
            id="r1", job_id="j1", result_type="classification", label="healthy",
            confidence=0.95, created_at="2025-01-01T00:00:00Z",
        )
        assert resp.confidence == 0.95

    def test_paginated_images_response(self):
        resp = PaginatedImagesResponse(items=[], total=0, skip=0, limit=20)
        assert resp.total == 0

    def test_paginated_jobs_response(self):
        resp = PaginatedAnalysisJobsResponse(items=[], total=0, skip=0, limit=20)
        assert resp.total == 0

    def test_paginated_results_response(self):
        resp = PaginatedAnalysisResultsResponse(items=[], total=0, skip=0, limit=100)
        assert resp.total == 0


# ────────────────────────── Integration Tests ─────────────────────────
class TestImageAnalysisModuleIntegration:
    def test_module_has_correct_structure(self):
        from app.modules.image_analysis.api import schemas
        from app.modules.image_analysis.api.router import router
        from app.modules.image_analysis.domain import interfaces, models

        assert hasattr(models, "PlantImageModel")
        assert hasattr(models, "ImageAnalysisJobModel")
        assert hasattr(models, "AnalysisResultModel")
        assert hasattr(interfaces, "PlantImageRepositoryInterface")
        assert hasattr(interfaces, "ImageAnalysisJobRepositoryInterface")
        assert hasattr(interfaces, "AnalysisResultRepositoryInterface")
        assert hasattr(schemas, "UploadImageRequest")
        assert router is not None

    def test_router_has_all_endpoints(self):
        from app.modules.image_analysis.api.router import router
        routes = {r.path for r in router.routes}
        expected = [
            "/api/v1/images/",
            "/api/v1/images/{image_id}",
            "/api/v1/images/{image_id}/analyze",
            "/api/v1/images/analyze/{job_id}",
            "/api/v1/images/analyze/{job_id}/results",
        ]
        for ep in expected:
            assert ep in routes, f"Missing endpoint: {ep}"

    def test_all_use_case_classes_exist(self):
        from app.modules.image_analysis.domain import use_cases
        expected = [
            "UploadImageUseCase", "GetImageUseCase", "ListImagesUseCase",
            "UpdateImageUseCase", "DeleteImageUseCase",
            "CreateAnalysisJobUseCase", "GetAnalysisJobUseCase",
            "ListAnalysisJobsUseCase", "GetAnalysisResultsUseCase",
        ]
        for name in expected:
            assert hasattr(use_cases, name), f"Missing use case: {name}"

    def test_infrastructure_repos_exist(self):
        from app.modules.image_analysis.infrastructure import (
            image_repository,
            job_repository,
            result_repository,
        )
        assert hasattr(image_repository, "PlantImageRepository")
        assert hasattr(job_repository, "ImageAnalysisJobRepository")
        assert hasattr(result_repository, "AnalysisResultRepository")
