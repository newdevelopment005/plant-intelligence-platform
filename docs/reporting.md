# Reporting Module

## Overview

The Reporting module provides report generation, storage, and management for the Plant Intelligence Platform. It supports creating reports from various data sources (phenotyping, genomics, germplasm, experiments), managing reusable report templates, and exporting in multiple formats.

## Architecture

```
reporting/
├── domain/
│   ├── models.py          # ReportModel, ReportTemplateModel
│   ├── interfaces.py      # ReportRepositoryInterface, ReportTemplateRepositoryInterface
│   └── use_cases.py       # 10 use cases
├── infrastructure/
│   ├── report_repository.py
│   ├── template_repository.py
│   └── __init__.py
├── api/
│   ├── router.py           # 10 REST endpoints
│   └── schemas.py          # 8 Pydantic schemas
└── tasks.py                # Celery tasks (placeholder)
```

## Domain Models

### ReportModel

Stores report metadata and generation status.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `name` | str (required) | Report display name |
| `description` | str \| None | Description text |
| `report_type` | str (required) | One of 10 types (see below) |
| `status` | str | `pending`, `generating`, `completed`, `failed` |
| `format` | str | Export format |
| `data_source` | str \| None | Origin data module |
| `parameters` | dict \| None | Generation parameters (JSONB) |
| `file_url` | str \| None | Generated file URL |
| `file_size_bytes` | int \| None | File size |
| `error_message` | str \| None | Error if failed |
| `tags` | list[str] \| None | Categorization tags |
| `project_id` | UUID \| None | Owning project |
| `created_by` | UUID | Creator user ID |

**Report types:** `phenotyping`, `genotyping`, `germplasm`, `experiment`, `project_summary`, `custom`, `statistical`, `comparative`, `temporal`, `geospatial`

**Export formats:** `pdf`, `csv`, `json`, `xlsx`, `html`, `docx`

### ReportTemplateModel

Reusable report configuration templates.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `name` | str (required) | Template name |
| `report_type` | str (required) | Report type |
| `default_format` | str | Default export format |
| `data_source` | str \| None | Data source module |
| `layout` | dict \| None | Layout configuration (JSONB) |
| `default_parameters` | dict \| None | Default parameters |
| `is_active` | bool | Whether template is active |
| `tags` | list[str] \| None | Categorization tags |
| `created_by` | UUID | Creator user ID |

## Use Cases

| Use Case | Input | Output | Validation |
|----------|-------|--------|------------|
| `CreateReportUseCase` | name, report_type, user_id, ... | `ReportModel` | Name required, valid type + format |
| `GetReportUseCase` | report_id | `ReportModel` | Raises `NotFoundException` if missing |
| `ListReportsUseCase` | skip, limit, filters | `dict` | Validates status enum |
| `UpdateReportUseCase` | report_id, user_id, fields | `ReportModel` | Creator-only, pending/failed only |
| `DeleteReportUseCase` | report_id, user_id | `bool` | Creator-only, not generating |
| `CreateTemplateUseCase` | name, report_type, user_id, ... | `ReportTemplateModel` | Name required, valid type |
| `GetTemplateUseCase` | template_id | `ReportTemplateModel` | Raises `NotFoundException` if missing |
| `ListTemplatesUseCase` | skip, limit, filters | `dict` | Paginated |
| `UpdateTemplateUseCase` | template_id, user_id, fields | `ReportTemplateModel` | Creator-only |
| `DeleteTemplateUseCase` | template_id, user_id | `bool` | Creator-only |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reports/` | Create report |
| GET | `/api/v1/reports/` | List reports (query: skip, limit, report_type, status_filter, project_id, search) |
| GET | `/api/v1/reports/{id}` | Get report |
| PUT | `/api/v1/reports/{id}` | Update report (creator only, pending/failed) |
| DELETE | `/api/v1/reports/{id}` | Delete report (creator only, not generating) |
| GET | `/api/v1/reports/{id}/download` | Download report |
| POST | `/api/v1/reports/templates` | Create template |
| GET | `/api/v1/reports/templates` | List templates (query: skip, limit, report_type, search) |
| GET | `/api/v1/reports/templates/{id}` | Get template |
| PUT | `/api/v1/reports/templates/{id}` | Update template (creator only) |
| DELETE | `/api/v1/reports/templates/{id}` | Delete template (creator only) |

## Validation Rules

- **Report name:** Required, non-empty, max 500 characters.
- **Report type:** Must be one of the 10 allowed values.
- **Format:** Must be `pdf`, `csv`, `json`, `xlsx`, `html`, or `docx`.
- **Status transitions:** Reports can only be edited in `pending` or `failed` state.
- **Deletion:** Cannot delete a report being generated.
- **Authorization:** Only the creator can update/delete reports/templates.

## Report Lifecycle

```
pending → generating → completed
pending → generating → failed
```

## Example: Create Report

```http
POST /api/v1/reports/
Authorization: Bearer <token>

{
  "name": "Drought Trial - Phenotyping Summary",
  "report_type": "phenotyping",
  "format": "pdf",
  "data_source": "phenotyping",
  "parameters": {
    "experiment_id": "exp-uuid",
    "traits": ["plant_height", "leaf_area", "yield"],
    "date_range": {"start": "2025-01-01", "end": "2025-06-30"}
  },
  "project_id": "uuid"
}

# Response: { "id": "rpt-uuid", "status": "pending", ... }
```

## Example: Create Template

```http
POST /api/v1/reports/templates
Authorization: Bearer <token>

{
  "name": "Standard Phenotyping Report",
  "report_type": "phenotyping",
  "default_format": "pdf",
  "layout": {
    "sections": ["summary", "traits", "statistics", "charts"],
    "charts": ["bar", "boxplot", "heatmap"]
  },
  "default_parameters": {"include_statistics": true, "confidence_level": 0.95}
}

# Response: { "id": "tpl-uuid", "is_active": true, ... }
```

## Celery Integration

The `tasks.py` file is a placeholder for Celery task definitions. In production, report generation will be dispatched to Celery workers that collect data from the relevant modules, generate the report in the requested format, and update the report status/file_url via the repository.

## Testing

```bash
cd apps/api
python -m pytest tests/unit/test_reporting.py -v
```

47 unit tests covering:
- Interface contract validation
- All 10 use cases (success + error paths)
- 8 Pydantic schema validations
- 4 integration tests (module structure, router endpoints, class existence, repo exports)
