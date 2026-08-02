# API Documentation

## Overview

The Plant Intelligence Platform API is a RESTful service built with FastAPI. All endpoints are versioned under `/api/v1/`.

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <token>
```

### Getting a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.pip-platform.org`

## API Modules

### Authentication (`/api/v1/auth`)

#### Public Endpoints

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/register` | Register new user | `{email, password, full_name, institution?, department?}` |
| POST | `/login` | Login | `{email, password}` |
| POST | `/forgot-password` | Request password reset | `{email}` |
| POST | `/reset-password` | Reset password | `{token, new_password}` |

#### Protected Endpoints (requires Bearer token)

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/refresh` | Refresh access token | `{refresh_token}` |
| POST | `/logout` | Logout (revoke token) | `{refresh_token}` |
| GET | `/me` | Get current user profile | - |
| PUT | `/me` | Update profile | `{full_name?, institution?, department?, bio?, orcid_id?}` |
| POST | `/change-password` | Change password | `{current_password, new_password}` |

#### Password Requirements
- Minimum 8 characters
- At least one uppercase, one lowercase, one digit, one special character

#### Roles
`admin`, `principal_investigator`, `researcher`, `technician`, `readonly`

#### Example: Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "researcher@university.edu",
  "password": "SecurePass123!",
  "full_name": "Dr. Jane Smith",
  "institution": "Plant Science University",
  "department": "Crop Genetics"
}
```

#### Example: Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "researcher@university.edu",
    "full_name": "Dr. Jane Smith",
    "role": "researcher"
  }
}
```

### Projects (`/api/v1/projects`)

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/` | List user's projects (with search, status filter, pagination) | - |
| POST | `/` | Create new project | `{name, description?, tags?}` |
| GET | `/{id}` | Get project details with members | - |
| PUT | `/{id}` | Update project (owner only) | `{name?, description?, status?, tags?}` |
| DELETE | `/{id}` | Delete project (owner only) | - |
| GET | `/{id}/members` | List project members | - |
| POST | `/{id}/members` | Add member to project | `{user_id, role}` |
| PUT | `/{id}/members/{member_id}` | Update member role | `{role}` |
| DELETE | `/{id}/members/{member_id}` | Remove member | - |

#### Query Parameters (List)

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search project names and descriptions |
| `status` | string | Filter by status: `active`, `archived`, `deleted` |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20, max: 100) |

#### Example: Create Project

```http
POST /api/v1/projects
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Drought Resistance Study",
  "description": "Investigating wheat drought tolerance mechanisms",
  "tags": ["drought", "wheat", "genetics"]
}
```

Response (201):
```json
{
  "id": "uuid",
  "name": "Drought Resistance Study",
  "description": "Investigating wheat drought tolerance mechanisms",
  "status": "active",
  "owner_id": "uuid",
  "tags": ["drought", "wheat", "genetics"],
  "metadata": null,
  "member_count": 1,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### Example: Add Member

```http
POST /api/v1/projects/{project_id}/members
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_id": "uuid",
  "role": "researcher"
}
```

#### Roles

| Role | Permissions |
|------|-------------|
| `principal_investigator` | Full project access |
| `researcher` | Can view and edit project data |
| `technician` | Can view and edit limited data |
| `readonly` | View-only access |

### Germplasm (`/api/v1/germplasm`)

#### Species

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/species` | List species (with search, pagination) | - |
| POST | `/species` | Create species | `{common_name, scientific_name, family?, genus?}` |
| GET | `/{species_id}` | Get species details | - |
| PUT | `/{species_id}` | Update species | `{common_name?, scientific_name?, ...}` |
| DELETE | `/{species_id}` | Delete species | - |

#### Accessions

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/accessions` | List accessions (with filters, pagination) | - |
| POST | `/accessions` | Create accession | `{accession_number, species_id, name, ...}` |
| GET | `/accessions/search` | Search accessions | `?q=query` |
| GET | `/{accession_id}` | Get accession details | - |
| PUT | `/{accession_id}` | Update accession (creator only) | `{name?, description?, ...}` |
| DELETE | `/{accession_id}` | Delete accession (creator only) | - |

#### Passport Data

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/accessions/{id}/passport` | Get passport data | - |
| POST | `/accessions/{id}/passport` | Create passport data | `{institute_code, country_code, ...}` |
| PUT | `/accessions/{id}/passport` | Update passport data | `{institute_code?, ...}` |

#### Pedigree

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/accessions/{id}/pedigree` | Get pedigree | - |
| GET | `/accessions/{id}/pedigree/tree` | Get pedigree tree (ancestors/descendants) | `?depth=3` |
| POST | `/accessions/{id}/pedigree` | Create pedigree | `{parent1_name, cross_type, ...}` |

#### Seed Storage

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/accessions/{id}/storage` | List seed storages | - |
| POST | `/accessions/{id}/storage` | Add seed storage | `{location, quantity_grams?, ...}` |
| PUT | `/storage/{storage_id}` | Update seed storage | `{location?, viability?, ...}` |
| DELETE | `/storage/{storage_id}` | Delete seed storage | - |

#### Images & Files

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/accessions/{id}/images` | List images | - |
| POST | `/accessions/{id}/images` | Upload image | `multipart/form-data` |
| DELETE | `/images/{image_id}` | Delete image | - |
| GET | `/accessions/{id}/files` | List files | - |
| POST | `/accessions/{id}/files` | Upload file | `multipart/form-data` |
| DELETE | `/files/{file_id}` | Delete file | - |

#### Query Parameters (Accessions List)

| Parameter | Type | Description |
|-----------|------|-------------|
| `species_id` | uuid | Filter by species |
| `project_id` | uuid | Filter by project |
| `status` | string | Filter: `available`, `limited`, `unavailable`, `reserved` |
| `search` | string | Search name, accession number, description |
| `skip` | int | Offset (default: 0) |
| `limit` | int | Limit (default: 20, max: 100) |

#### Example: Create Accession

```http
POST /api/v1/germplasm/accessions
Content-Type: application/json
Authorization: Bearer <token>

{
  "accession_number": "PI 123456",
  "species_id": "uuid",
  "name": "Wheat landrace from Nepal",
  "description": "Drought tolerant variety",
  "latitude": 27.7172,
  "longitude": 85.3240,
  "tags": ["drought", "nepal"]
}
```

#### Example: Create Seed Storage

```http
POST /api/v1/germplasm/accessions/{id}/storage
Content-Type: application/json
Authorization: Bearer <token>

{
  "location": "Genebank Vault A",
  "container_type": "Paper envelope",
  "quantity_grams": 100.5,
  "storage_conditions": "-18°C, 20% RH"
}
```

### Phenotyping (`/api/v1/phenotyping`)

#### Experiments

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/experiments` | List experiments | Query: skip, limit, project_id, status, search |
| POST | `/experiments` | Create experiment | `{name, description?, experiment_type?, project_id?, location?, latitude?, longitude?, altitude?, start_date?, end_date?, tags?}` |
| GET | `/experiments/{id}` | Get experiment | - |
| PUT | `/experiments/{id}` | Update experiment | `{name?, description?, experiment_type?, status?, ...}` |
| DELETE | `/experiments/{id}` | Delete experiment | - |
| GET | `/experiments/{id}/summary` | Experiment statistics | - |

#### Traits

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/experiments/{id}/traits` | List traits | Query: skip, limit |
| POST | `/experiments/{id}/traits` | Create trait | `{name, description?, trait_category?, unit?, data_type?, min_value?, max_value?, allowed_values?, is_required?}` |
| GET | `/traits/{id}` | Get trait | - |
| PUT | `/traits/{id}` | Update trait | `{name?, data_type?, unit?, ...}` |
| DELETE | `/traits/{id}` | Delete trait | - |

#### Measurements

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/experiments/{id}/measurements` | List measurements | Query: skip, limit, trait_id, accession_id |
| POST | `/experiments/{id}/measurements` | Add measurement | `{trait_id, value_numeric?, value_text?, accession_id?, rep?, block?, plot?, ...}` |
| POST | `/experiments/{id}/measurements/bulk` | Bulk import | `{measurements: [{trait_id, value_numeric?, ...}, ...]}` |
| GET | `/measurements/{id}` | Get measurement | - |
| PUT | `/measurements/{id}` | Update measurement | `{value_numeric?, value_text?, ...}` |
| DELETE | `/measurements/{id}` | Delete measurement | - |

### Genomics (`/api/v1/genomics`)

#### Sequences

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/sequences` | List sequences | Query: skip, limit, sequence_type, species_id, project_id, search |
| POST | `/sequences` | Register sequence | `{name, description?, sequence_type?, species_id?, organism?, chromosome?, length?, gc_content?, ...}` |
| GET | `/sequences/{id}` | Get sequence | - |
| PUT | `/sequences/{id}` | Update sequence | `{name?, sequence_type?, organism?, ...}` |
| DELETE | `/sequences/{id}` | Delete sequence | - |

#### Variants

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/sequences/{id}/variants` | List variants | Query: skip, limit, chromosome, variant_type, gene_name |
| POST | `/sequences/{id}/variants` | Add variant | `{chromosome, position, reference_allele, alternate_allele, variant_type, quality?, ...}` |
| POST | `/sequences/{id}/variants/bulk` | Bulk import | `{variants: [{chromosome, position, ref, alt, type, ...}, ...]}` |
| GET | `/variants/search` | Search variants | Query: sequence_id, chromosome, start, end, variant_type, gene_name, min_quality |
| GET | `/variants/{id}` | Get variant | - |
| DELETE | `/variants/{id}` | Delete variant | - |

#### Annotations

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/sequences/{id}/annotations` | List annotations | Query: skip, limit, search |
| POST | `/sequences/{id}/annotations` | Add annotation | `{gene_symbol, gene_name?, description?, chromosome?, go_terms?, pfam_domains?, kegg_pathways?}` |
| GET | `/annotations/{id}` | Get annotation | - |
| PUT | `/annotations/{id}` | Update annotation | `{gene_name?, description?, go_terms?, ...}` |
| DELETE | `/annotations/{id}` | Delete annotation | - |

### Molecular Biology (`/api/v1/molecular`)

#### Experiments

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/experiments` | Create experiment | `{name, description?, experiment_type?, project_id?, species_id?, protocol?, ...}` |
| GET | `/experiments` | List experiments | Query: skip, limit, experiment_type, project_id, status, search |
| GET | `/experiments/{id}` | Get experiment | - |
| PUT | `/experiments/{id}` | Update experiment | `{name?, experiment_type?, status?, protocol?, ...}` |
| DELETE | `/experiments/{id}` | Delete experiment | - |

#### Primers

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/experiments/{exp_id}/primers` | Create primer | `{name, sequence, primer_type?, target_gene?, tm?, ...}` |
| GET | `/experiments/{exp_id}/primers` | List primers | Query: skip, limit, primer_type, search |
| GET | `/experiments/{exp_id}/primers/{id}` | Get primer | - |
| PUT | `/experiments/{exp_id}/primers/{id}` | Update primer | `{name?, sequence?, primer_type?, ...}` |
| DELETE | `/experiments/{exp_id}/primers/{id}` | Delete primer | - |

#### Constructs

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/experiments/{exp_id}/constructs` | Create construct | `{name, construct_type?, vector_backbone?, insert_sequence?, ...}` |
| GET | `/experiments/{exp_id}/constructs` | List constructs | Query: skip, limit, construct_type, search |
| GET | `/experiments/{exp_id}/constructs/{id}` | Get construct | - |
| PUT | `/experiments/{exp_id}/constructs/{id}` | Update construct | `{name?, construct_type?, vector_backbone?, ...}` |
| DELETE | `/experiments/{exp_id}/constructs/{id}` | Delete construct | - |

### Literature (`/api/v1/literature`)

#### Papers

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/papers` | Create paper | `{title, abstract?, authors?, doi?, pmid?, journal?, source?, paper_type?, ...}` |
| GET | `/papers` | List papers | Query: skip, limit, project_id, source, paper_type, year, search |
| GET | `/papers/{id}` | Get paper | - |
| PUT | `/papers/{id}` | Update paper | `{title?, abstract?, authors?, doi?, summary?, ...}` |
| DELETE | `/papers/{id}` | Delete paper | - |

#### Semantic Search

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/search` | Semantic search | `{query, limit?, project_id?}` |

#### Collections

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/collections` | Create collection | `{name, description?, color?, project_id?, tags?}` |
| GET | `/collections` | List collections | Query: skip, limit, project_id, search |
| GET | `/collections/{id}` | Get collection | - |
| PUT | `/collections/{id}` | Update collection | `{name?, description?, color?, tags?}` |
| DELETE | `/collections/{id}` | Delete collection | - |
| POST | `/collections/{id}/papers` | Add paper to collection | `{paper_id}` |
| DELETE | `/collections/{id}/papers/{pid}` | Remove paper | - |
| GET | `/collections/{id}/papers` | List papers in collection | Query: skip, limit |

#### Notes

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/papers/{id}/notes` | Create note | `{content, page_number?, highlight_text?, tags?}` |
| GET | `/papers/{id}/notes` | List notes | Query: skip, limit |
| GET | `/papers/{id}/notes/{nid}` | Get note | - |
| PUT | `/papers/{id}/notes/{nid}` | Update note | `{content?, page_number?, tags?}` |
| DELETE | `/papers/{id}/notes/{nid}` | Delete note | - |

### Bioinformatics (`/api/v1/bioinformatics`)

#### Analysis Jobs

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/jobs` | Create analysis job | `{name, analysis_type, input_data, priority?, parameters?, description?, tags?, project_id?}` |
| GET | `/jobs` | List jobs | Query: skip, limit, analysis_type, status_filter, project_id, search |
| GET | `/jobs/{id}` | Get job details | - |
| PUT | `/jobs/{id}` | Update job (creator only, pending/failed) | `{name?, description?, priority?, tags?}` |
| POST | `/jobs/{id}/cancel` | Cancel job (creator only, pending/running) | - |
| DELETE | `/jobs/{id}` | Delete job (creator only, not running) | - |

#### Pipeline Templates

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/templates` | Create template | `{name, analysis_type, description?, steps?, default_parameters?, required_inputs?, tags?}` |
| GET | `/templates` | List templates | Query: skip, limit, analysis_type, search |
| GET | `/templates/{id}` | Get template | - |
| PUT | `/templates/{id}` | Update template (creator only) | `{name?, description?, steps?, ...}` |
| DELETE | `/templates/{id}` | Delete template (creator only) | - |

**Analysis types:** `alignment`, `blast`, `variant_calling`, `rnaseq`, `phylogenetics`, `pathway_analysis`, `gene_prediction`, `primer_design`, `codon_usage`, `motif_search`, `population_genetics`, `gwas`, `qtl_mapping`

**Status values:** `pending`, `running`, `completed`, `failed`, `cancelled`

**Priority values:** `low`, `normal`, `high`, `urgent`

### Knowledge Graph (`/api/v1/knowledge-graph`)

#### Entities

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/entities` | Create entity | `{name, entity_type, description?, source_module?, source_id?, properties?, tags?, project_id?}` |
| GET | `/entities` | List entities | Query: skip, limit, entity_type, project_id, source_module, search |
| GET | `/entities/{id}` | Get entity | - |
| PUT | `/entities/{id}` | Update entity (creator only) | `{name?, description?, properties?, tags?}` |
| DELETE | `/entities/{id}` | Delete entity + cascade edges (creator only) | - |
| GET | `/entities/{id}/explore` | Explore neighbors | Query: relation_type, depth |

**Supported entity types:** `gene`, `protein`, `trait`, `phenotype`, `pathway`, `species`, `researcher`, `institution`, `experiment`, `publication`, `environment`, `treatment`, `disease`, `pest`, `chemical`, `marker`, `qtl`, `go_term`, `kegg_pathway`, `other`

#### Edges

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/edges` | Create edge | `{source_entity_id, target_entity_id, relation_type, description?, properties?, weight?, source?, project_id?}` |
| GET | `/edges` | List edges | Query: skip, limit, source_entity_id, target_entity_id, relation_type, project_id |
| DELETE | `/edges/{id}` | Delete edge | - |

#### Relations & Search

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/relations` | Get distinct relation types | Query: project_id |
| POST | `/search` | Semantic search | `{query, limit?, project_id?}` |

**Validation rules:**
- Entity name: required, max 500 characters.
- Entity type: must be one of the 20 allowed values.
- Edge relation type: required, non-empty.
- Self-referencing edges are not allowed.
- Only the creator can update/delete an entity.

### Image Analysis (`/api/v1/images`)

#### Plant Images

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/` | Upload image | `{name, file_url, image_type?, species?, tissue_type?, ...}` |
| GET | `/` | List images | Query: skip, limit, image_type, species, project_id, source_module, search |
| GET | `/{id}` | Get image | - |
| PUT | `/{id}` | Update image (uploader only) | `{name?, description?, species?, tissue_type?, growth_stage?, tags?}` |
| DELETE | `/{id}` | Delete image (uploader only) | - |

#### Analysis

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/{image_id}/analyze` | Submit analysis job | `{analysis_type, parameters?, project_id?}` |
| GET | `/{image_id}/analyze` | List analysis jobs | Query: skip, limit, status_filter |
| GET | `/analyze/{job_id}` | Get analysis job | - |
| GET | `/analyze/{job_id}/results` | Get analysis results | Query: skip, limit |

**Image types:** `general`, `leaf`, `root`, `seed`, `fruit`, `flower`, `microscopy`, `drone`, `phenotype`, `xray`, `thermal`

**Analysis types:** `disease_detection`, `pest_detection`, `growth_stage`, `phenotype_measurement`, `leaf_area`, `root_analysis`, `seed_counting`, `fruit_quality`, `morphology`, `stress_detection`, `weed_detection`, `flowering_time`

**Status values:** `pending`, `running`, `completed`, `failed`

### AI Research Assistant (`/api/v1/ai`)

#### Conversations

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/conversations` | Create conversation | `{title, description?, model_used?, tags?, project_id?}` |
| GET | `/conversations` | List conversations | Query: skip, limit, project_id, status_filter, search |
| GET | `/conversations/{id}` | Get conversation | - |
| PUT | `/conversations/{id}` | Update conversation (creator only) | `{title?, description?, status?, tags?}` |
| DELETE | `/conversations/{id}` | Delete conversation + cascade messages (creator only) | - |

#### Messages

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/conversations/{id}/messages` | Send message | `{content}` |
| GET | `/conversations/{id}/messages` | List messages | Query: skip, limit |

#### AI Tools

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/summarize-literature` | Summarize papers | `{paper_ids, focus_areas?}` |
| POST | `/recommend-genes` | Gene recommendations | `{trait_description, species?}` |
| POST | `/design-experiment` | Experiment design | `{research_question, species?, variables?, constraints?}` |
| POST | `/analyze-image` | Image analysis | `{image_url?, image_base64?, analysis_type?}` |

**Status values:** `active`, `archived`, `deleted`

**Analysis types:** `general`, `phenotype`, `disease`, `growth_stage`, `morphism`

**Validation rules:**
- Conversation title: required, max 500 characters.
- Message content: required, max 50,000 characters.
- Only the conversation creator can send messages, update, or delete.
- Archived conversations cannot receive new messages.

### Notebook (`/api/v1/notebook`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entries` | List entries |
| POST | `/entries` | Create entry |
| GET | `/entries/{id}` | Get entry |
| PUT | `/entries/{id}` | Update entry |
| POST | `/entries/{id}/lock` | Lock entry |
| POST | `/entries/{id}/unlock` | Unlock entry |

### LIMS (`/api/v1/lims`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/samples` | List samples |
| POST | `/samples` | Register sample |
| POST | `/samples/transfer` | Transfer sample |
| GET | `/equipment` | List equipment |
| GET | `/reagents` | List reagents |

### Reports (`/api/v1/reports`)

#### Reports

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/` | Create report | `{name, report_type, format?, data_source?, parameters?, description?, tags?, project_id?}` |
| GET | `/` | List reports | Query: skip, limit, report_type, status_filter, project_id, search |
| GET | `/{id}` | Get report | - |
| PUT | `/{id}` | Update report (creator only, pending/failed) | `{name?, description?, tags?}` |
| DELETE | `/{id}` | Delete report (creator only, not generating) | - |
| GET | `/{id}/download` | Download report | - |

#### Report Templates

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/templates` | Create template | `{name, report_type, default_format?, data_source?, layout?, default_parameters?, tags?}` |
| GET | `/templates` | List templates | Query: skip, limit, report_type, search |
| GET | `/templates/{id}` | Get template | - |
| PUT | `/templates/{id}` | Update template (creator only) | `{name?, description?, layout?, default_parameters?, tags?}` |
| DELETE | `/templates/{id}` | Delete template (creator only) | - |

**Report types:** `phenotyping`, `genotyping`, `germplasm`, `experiment`, `project_summary`, `custom`, `statistical`, `comparative`, `temporal`, `geospatial`

**Export formats:** `pdf`, `csv`, `json`, `xlsx`, `html`, `docx`

**Status values:** `pending`, `generating`, `completed`, `failed`

### Admin (`/api/v1/admin`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List users |
| PUT | `/users/{id}/role` | Update role |
| GET | `/audit-log` | View audit log |
| GET | `/system-health` | System health |

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

### Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Rate Limiting

- API endpoints: 100 requests per minute per user
- AI endpoints: 30 requests per minute per user

## Pagination

List endpoints support cursor-based pagination:

```http
GET /api/v1/germplasm?cursor=abc123&limit=20
```

Response:
```json
{
  "items": [...],
  "next_cursor": "def456",
  "has_more": true,
  "total": 1234
}
```
