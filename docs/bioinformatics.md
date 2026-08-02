# Bioinformatics Module

## Overview

The Bioinformatics module provides pipeline management for computational biology analyses in the Plant Intelligence Platform. It manages analysis job submission, tracking, and cancellation, plus reusable pipeline templates for common bioinformatics workflows.

## Architecture

```
bioinformatics/
├── domain/
│   ├── models.py          # AnalysisJobModel, PipelineTemplateModel
│   ├── interfaces.py      # AnalysisJobRepositoryInterface, PipelineTemplateRepositoryInterface
│   └── use_cases.py       # 11 use cases
├── infrastructure/
│   ├── job_repository.py
│   ├── template_repository.py
│   └── __init__.py
├── api/
│   ├── router.py           # 11 REST endpoints
│   └── schemas.py          # 10 Pydantic schemas
└── tasks.py                # Celery tasks (placeholder)
```

## Domain Models

### AnalysisJobModel

Represents a submitted bioinformatics analysis job.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `name` | str (required) | Job display name |
| `description` | str \| None | Description text |
| `analysis_type` | str (required) | One of 13 types (see below) |
| `status` | str | `pending`, `running`, `completed`, `failed`, or `cancelled` |
| `priority` | str | `low`, `normal`, `high`, or `urgent` |
| `input_data` | dict \| None | Input parameters for the analysis |
| `parameters` | dict \| None | Tool-specific parameters |
| `result_data` | dict \| None | Analysis results |
| `output_files` | list[str] \| None | Generated output file paths |
| `error_message` | str \| None | Error details if failed |
| `progress_percent` | int \| None | Completion percentage |
| `started_at` | datetime \| None | When processing started |
| `completed_at` | datetime \| None | When processing completed |
| `runtime_seconds` | float \| None | Total runtime |
| `tags` | list[str] \| None | Categorization tags |
| `project_id` | UUID \| None | Owning project |
| `created_by` | UUID | Creator user ID |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

**Supported analysis types:** `alignment`, `blast`, `variant_calling`, `rnaseq`, `phylogenetics`, `pathway_analysis`, `gene_prediction`, `primer_design`, `codon_usage`, `motif_search`, `population_genetics`, `gwas`, `qtl_mapping`

### PipelineTemplateModel

Reusable pipeline configuration templates.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `name` | str (required) | Template name |
| `description` | str \| None | Description text |
| `analysis_type` | str (required) | Analysis type |
| `steps` | list[dict] \| None | Pipeline steps (JSONB) |
| `default_parameters` | dict \| None | Default tool parameters |
| `required_inputs` | list[str] \| None | Required input names |
| `version` | str | Template version |
| `is_active` | bool | Whether template is active |
| `tags` | list[str] \| None | Categorization tags |
| `created_by` | UUID | Creator user ID |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

## Use Cases

| Use Case | Input | Output | Validation |
|----------|-------|--------|------------|
| `CreateAnalysisJobUseCase` | name, analysis_type, user_id, input_data, ... | `AnalysisJobModel` | Name required, valid type/priority, input_data required |
| `GetAnalysisJobUseCase` | job_id | `AnalysisJobModel` | Raises `NotFoundException` if missing |
| `ListAnalysisJobsUseCase` | skip, limit, filters | `dict` | Validates status enum |
| `UpdateAnalysisJobUseCase` | job_id, user_id, fields | `AnalysisJobModel` | Creator-only, only pending/failed jobs |
| `CancelAnalysisJobUseCase` | job_id, user_id | `AnalysisJobModel` | Creator-only, only pending/running jobs |
| `DeleteAnalysisJobUseCase` | job_id, user_id | `bool` | Creator-only, cannot delete running jobs |
| `CreatePipelineTemplateUseCase` | name, analysis_type, user_id, ... | `PipelineTemplateModel` | Name required, valid type |
| `GetPipelineTemplateUseCase` | template_id | `PipelineTemplateModel` | Raises `NotFoundException` if missing |
| `ListPipelineTemplatesUseCase` | skip, limit, filters | `dict` | Paginated |
| `UpdatePipelineTemplateUseCase` | template_id, user_id, fields | `PipelineTemplateModel` | Creator-only |
| `DeletePipelineTemplateUseCase` | template_id, user_id | `bool` | Creator-only |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/bioinformatics/jobs` | Create analysis job |
| GET | `/api/v1/bioinformatics/jobs` | List jobs (query: skip, limit, analysis_type, status_filter, project_id, search) |
| GET | `/api/v1/bioinformatics/jobs/{id}` | Get job details |
| PUT | `/api/v1/bioinformatics/jobs/{id}` | Update job (creator only, pending/failed only) |
| POST | `/api/v1/bioinformatics/jobs/{id}/cancel` | Cancel job (creator only, pending/running only) |
| DELETE | `/api/v1/bioinformatics/jobs/{id}` | Delete job (creator only, not running) |
| POST | `/api/v1/bioinformatics/templates` | Create pipeline template |
| GET | `/api/v1/bioinformatics/templates` | List templates (query: skip, limit, analysis_type, search) |
| GET | `/api/v1/bioinformatics/templates/{id}` | Get template |
| PUT | `/api/v1/bioinformatics/templates/{id}` | Update template (creator only) |
| DELETE | `/api/v1/bioinformatics/templates/{id}` | Delete template (creator only) |

## Validation Rules

- **Job name:** Required, non-empty, max 500 characters.
- **Analysis type:** Must be one of the 13 allowed values.
- **Priority:** Must be `low`, `normal`, `high`, or `urgent`.
- **Input data:** Required for job creation.
- **Status transitions:** Jobs can only be edited in `pending` or `failed` state. Cancellation only for `pending` or `running`. Deletion blocked for `running` jobs.
- **Authorization:** Only the creator can update, cancel, or delete jobs/templates.

## Example: Submit Alignment Job

```http
POST /api/v1/bioinformatics/jobs
Authorization: Bearer <token>

{
  "name": "Wheat genome alignment",
  "analysis_type": "alignment",
  "priority": "high",
  "input_data": {
    "sequences": ["fasta_file_1.fa", "fasta_file_2.fa"],
    "reference": "IWGSC_ref_v1.0.fa"
  },
  "parameters": {
    "tool": "bwa-mem2",
    "threads": 16,
    "preset": "map-ont"
  },
  "project_id": "uuid"
}

# Response: { "id": "job-uuid", "status": "pending", ... }
```

## Example: Create Pipeline Template

```http
POST /api/v1/bioinformatics/templates
Authorization: Bearer <token>

{
  "name": "Standard RNA-Seq Pipeline",
  "analysis_type": "rnaseq",
  "description": "STAR alignment + DESeq2 differential expression",
  "steps": [
    {"step": 1, "tool": "fastp", "action": "quality_filter"},
    {"step": 2, "tool": "star", "action": "align"},
    {"step": 3, "tool": "featurecounts", "action": "quantify"},
    {"step": 4, "tool": "deseq2", "action": "differential_expression"}
  ],
  "default_parameters": {"threads": 8, "pvalue_cutoff": 0.05},
  "required_inputs": ["fastq_r1", "fastq_r2", "reference_genome", "gtf_annotation"]
}

# Response: { "id": "tpl-uuid", "version": "1.0", ... }
```

## Job Lifecycle

```
pending → running → completed
pending → running → failed
pending → cancelled
running → cancelled
```

## Celery Integration

The `tasks.py` file is a placeholder for Celery task definitions. In production, analysis jobs will be dispatched to Celery workers that execute the actual bioinformatics tools (BWA, STAR, GATK, etc.) and update job status/progress via the repository.

## Testing

```bash
cd apps/api
python -m pytest tests/unit/test_bioinformatics.py -v
```

55 unit tests covering:
- Interface contract validation
- All 11 use cases (success + error paths)
- 10 Pydantic schema validations
- 4 integration tests (module structure, router endpoints, class existence, repo exports)
