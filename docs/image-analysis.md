# Image Analysis Module

## Overview

The Image Analysis module provides image management and AI-powered analysis for plant science imagery. It handles upload, storage, metadata management, and submission of images to analysis pipelines for disease detection, phenotype measurement, growth stage classification, and more.

## Architecture

```
image_analysis/
├── domain/
│   ├── models.py          # PlantImageModel, ImageAnalysisJobModel, AnalysisResultModel
│   ├── interfaces.py      # 3 repository interfaces (18 methods)
│   └── use_cases.py       # 9 use cases
├── infrastructure/
│   ├── image_repository.py
│   ├── job_repository.py
│   ├── result_repository.py
│   └── __init__.py
├── api/
│   ├── router.py           # 9 REST endpoints
│   └── schemas.py          # 10 Pydantic schemas
└── tasks.py                # Celery tasks (placeholder)
```

## Domain Models

### PlantImageModel

Stores metadata about uploaded plant images.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `name` | str (required) | Image display name |
| `description` | str \| None | Description text |
| `file_url` | str (required) | Storage URL |
| `thumbnail_url` | str \| None | Thumbnail URL |
| `file_size_bytes` | int \| None | File size |
| `mime_type` | str \| None | MIME type |
| `width` / `height` | int \| None | Dimensions in pixels |
| `image_type` | str (required) | One of 11 types (see below) |
| `source_module` | str \| None | Originating PIP module |
| `source_id` | str \| None | ID in originating module |
| `species` | str \| None | Plant species |
| `tissue_type` | str \| None | Tissue (leaf, root, etc.) |
| `growth_stage` | str \| None | Growth stage |
| `magnification` | str \| None | Microscopy magnification |
| `gps_latitude` / `gps_longitude` | float \| None | GPS coordinates |
| `tags` | list[str] \| None | Categorization tags |
| `project_id` | UUID \| None | Owning project |
| `created_by` | UUID | Uploader user ID |

**Image types:** `general`, `leaf`, `root`, `seed`, `fruit`, `flower`, `microscopy`, `drone`, `phenotype`, `xray`, `thermal`

### ImageAnalysisJobModel

Tracks analysis submissions.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `image_id` | UUID | Source image |
| `analysis_type` | str (required) | One of 12 types (see below) |
| `status` | str | `pending`, `running`, `completed`, `failed` |
| `parameters` | dict \| None | Tool parameters |
| `error_message` | str \| None | Error if failed |
| `model_version` | str \| None | AI model version |
| `runtime_seconds` | float \| None | Total runtime |

**Analysis types:** `disease_detection`, `pest_detection`, `growth_stage`, `phenotype_measurement`, `leaf_area`, `root_analysis`, `seed_counting`, `fruit_quality`, `morphology`, `stress_detection`, `weed_detection`, `flowering_time`

### AnalysisResultModel

Individual analysis findings.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `job_id` | UUID | Parent analysis job |
| `result_type` | str | e.g., `classification`, `detection`, `measurement` |
| `label` | str \| None | Result label |
| `confidence` | float \| None | Confidence score |
| `bbox` | dict \| None | Bounding box (JSONB) |
| `measurements` | dict \| None | Measured values (JSONB) |
| `annotations` | dict \| None | Annotations (JSONB) |

## Use Cases

| Use Case | Input | Output | Validation |
|----------|-------|--------|------------|
| `UploadImageUseCase` | name, file_url, user_id, ... | `PlantImageModel` | Name + file_url required, valid image type |
| `GetImageUseCase` | image_id | `PlantImageModel` | Raises `NotFoundException` if missing |
| `ListImagesUseCase` | skip, limit, filters | `dict` | Paginated |
| `UpdateImageUseCase` | image_id, user_id, fields | `PlantImageModel` | Uploader-only |
| `DeleteImageUseCase` | image_id, user_id | `bool` | Uploader-only |
| `CreateAnalysisJobUseCase` | image_id, analysis_type, user_id | `ImageAnalysisJobModel` | Image must exist, valid analysis type |
| `GetAnalysisJobUseCase` | job_id | `ImageAnalysisJobModel` | Raises `NotFoundException` if missing |
| `ListAnalysisJobsUseCase` | skip, limit, filters | `dict` | Validates status enum |
| `GetAnalysisResultsUseCase` | job_id, skip, limit | `dict` | Job must exist |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/images/` | Upload image |
| GET | `/api/v1/images/` | List images (query: skip, limit, image_type, species, project_id, source_module, search) |
| GET | `/api/v1/images/{id}` | Get image |
| PUT | `/api/v1/images/{id}` | Update image (uploader only) |
| DELETE | `/api/v1/images/{id}` | Delete image (uploader only) |
| POST | `/api/v1/images/{id}/analyze` | Submit analysis job |
| GET | `/api/v1/images/{id}/analyze` | List analysis jobs for image |
| GET | `/api/v1/images/analyze/{job_id}` | Get analysis job |
| GET | `/api/v1/images/analyze/{job_id}/results` | Get analysis results |

## Validation Rules

- **Image name:** Required, non-empty, max 500 characters.
- **File URL:** Required, non-empty.
- **Image type:** Must be one of the 11 allowed values.
- **Analysis type:** Must be one of the 12 allowed values.
- **Authorization:** Only the uploader can update or delete images.

## Example: Upload Leaf Image

```http
POST /api/v1/images/
Authorization: Bearer <token>

{
  "name": "Wheat leaf - drought stress",
  "file_url": "https://storage.example.com/images/leaf-001.jpg",
  "image_type": "leaf",
  "species": "Triticum aestivum",
  "tissue_type": "leaf",
  "growth_stage": "tillering",
  "tags": ["drought", "stress"],
  "project_id": "uuid"
}
```

## Example: Submit Disease Detection

```http
POST /api/v1/images/{image_id}/analyze
Authorization: Bearer <token>

{
  "image_id": "img-uuid",
  "analysis_type": "disease_detection",
  "parameters": {"model": "resnet50", "threshold": 0.8}
}

# Response: { "id": "job-uuid", "status": "pending", ... }
```

## Example: Get Results

```http
GET /api/v1/images/analyze/{job_id}/results
Authorization: Bearer <token>

{
  "items": [
    {
      "result_type": "detection",
      "label": "leaf_rust",
      "confidence": 0.92,
      "bbox": {"x": 100, "y": 200, "w": 50, "h": 50},
      "measurements": {"affected_area_percent": 12.5}
    }
  ],
  "total": 1
}
```

## Celery Integration

The `tasks.py` file is a placeholder for Celery task definitions. In production, analysis jobs will be dispatched to Celery workers that run the actual CV/ML models (disease detection, leaf area measurement, etc.) and update job status/results via the repository.

## Testing

```bash
cd apps/api
python -m pytest tests/unit/test_image_analysis.py -v
```

41 unit tests covering:
- Interface contract validation
- All 9 use cases (success + error paths)
- 10 Pydantic schema validations
- 4 integration tests (module structure, router endpoints, class existence, repo exports)
