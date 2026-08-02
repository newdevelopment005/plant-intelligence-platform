# Project Management Module

## Overview

The Project Management module enables researchers to create, organize, and collaborate on plant science research projects. It provides role-based access control, team management, and serves as the central hub connecting all platform modules.

## Features

- **Project CRUD**: Create, read, update, and delete research projects
- **Team Management**: Add/remove collaborators with role-based permissions
- **Status Tracking**: Active, archived, and deleted project states
- **Tagging System**: Organize projects with searchable tags
- **Search & Filter**: Find projects by name, description, or status
- **Pagination**: Efficient pagination for large project lists

## Architecture

```
project/
├── domain/
│   ├── models.py          # ProjectModel, ProjectMemberModel
│   ├── interfaces.py      # Repository interfaces
│   └── use_cases.py       # Business logic (CRUD + member management)
├── infrastructure/
│   ├── repositories.py    # ProjectRepository (PostgreSQL)
│   └── member_repository.py  # ProjectMemberRepository
└── api/
    ├── router.py          # FastAPI router with 8 endpoints
    └── schemas.py         # Pydantic request/response models
```

## Database Schema

### Projects Table (`project.projects`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Project name (unique) |
| description | TEXT | Optional description |
| status | ENUM | active, archived, deleted |
| owner_id | UUID | FK to auth.users |
| start_date | DATE | Optional start date |
| end_date | DATE | Optional end date |
| tags | TEXT[] | Array of tags |
| metadata | JSONB | Flexible metadata storage |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update timestamp |

### Project Members Table (`project.project_members`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| project_id | UUID | FK to project.projects |
| user_id | UUID | FK to auth.users |
| role | VARCHAR(50) | Member role |
| joined_at | TIMESTAMPTZ | When member was added |

## API Endpoints

### List Projects
```
GET /api/v1/projects?search=drought&status=active&page=1&page_size=20
```

### Create Project
```
POST /api/v1/projects
{
  "name": "Drought Resistance Study",
  "description": "Investigating wheat drought tolerance mechanisms",
  "tags": ["drought", "wheat", "genetics"]
}
```

### Get Project
```
GET /api/v1/projects/{id}
```

### Update Project
```
PUT /api/v1/projects/{id}
{
  "name": "Updated Project Name",
  "status": "archived"
}
```

### Delete Project
```
DELETE /api/v1/projects/{id}
```

### Member Management
```
POST   /api/v1/projects/{id}/members          # Add member
GET    /api/v1/projects/{id}/members           # List members
PUT    /api/v1/projects/{id}/members/{member_id}  # Update role
DELETE /api/v1/projects/{id}/members/{member_id}  # Remove member
```

## Permissions

| Action | Owner | PI | Researcher | Technician | Readonly |
|--------|-------|-----|------------|------------|----------|
| View project | ✓ | ✓ | ✓ | ✓ | ✓ |
| Update project | ✓ | ✗ | ✗ | ✗ | ✗ |
| Delete project | ✓ | ✗ | ✗ | ✗ | ✗ |
| Add member | ✓ | ✓ | ✗ | ✗ | ✗ |
| Remove member | ✓ | ✓ | ✗ | ✗ | ✗ |
| Update member role | ✓ | ✓ | ✗ | ✗ | ✗ |

## Frontend Pages

| Route | Description |
|-------|-------------|
| `/projects` | Project list with search and create modal |
| `/projects/{id}` | Project detail with tabs (Overview, Members, Settings) |
| `/projects/{id}/germplasm` | Germplasm data for project (Phase 5) |
| `/projects/{id}/phenotyping` | Phenotyping data (Phase 6) |
| `/projects/{id}/genomics` | Genomics data (Phase 7) |
| `/projects/{id}/literature` | Literature (Phase 10) |
| `/projects/{id}/notebook` | Lab notebook (Phase 12) |

## Tests

- **Unit tests**: `apps/api/tests/unit/test_project.py` — 12 test cases covering use cases
- **Integration tests**: `apps/api/tests/integration/test_project.py` — 18 test cases covering API endpoints

## Usage Example

```python
# Create a project
from app.modules.project.domain.use_cases import CreateProjectUseCase

use_case = CreateProjectUseCase(project_repo)
project = await use_case.execute(
    owner_id="user-123",
    name="Drought Resistance Study",
    description="Investigating wheat drought tolerance",
    tags=["drought", "wheat"]
)

# Add a team member
from app.modules.project.domain.use_cases import AddMemberUseCase

use_case = AddMemberUseCase(member_repo, project_repo)
member = await use_case.execute(
    project_id=project.id,
    owner_id="user-123",
    user_id="user-456",
    role="researcher"
)
```
