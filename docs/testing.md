# Testing Guide

Comprehensive guide to the Plant Intelligence Platform test suite.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures (client, auth, sample data)
├── factories.py             # Test data factory classes
├── unit/                    # Unit tests (mocked dependencies)
│   ├── test_auth.py
│   ├── test_project.py
│   ├── test_germplasm.py
│   ├── test_genomics.py
│   ├── test_phenotyping.py
│   ├── test_molecular.py
│   ├── test_literature.py
│   ├── test_knowledge_graph.py
│   ├── test_ai_assistant.py
│   ├── test_bioinformatics.py
│   ├── test_image_analysis.py
│   ├── test_reporting.py
│   └── ...
├── integration/             # Integration tests (HTTP endpoint tests)
│   ├── test_auth.py
│   ├── test_project.py
│   ├── test_germplasm.py
│   ├── test_genomics.py
│   ├── test_phenotyping.py
│   ├── test_molecular.py
│   ├── test_literature.py
│   ├── test_knowledge_graph.py
│   ├── test_ai_assistant.py
│   ├── test_bioinformatics.py
│   ├── test_image_analysis.py
│   └── test_reporting.py
└── e2e/                     # End-to-end tests (cross-module workflows)
    └── test_research_workflow.py
```

## Running Tests

```bash
# Run all tests
make test-api

# Run by category
cd apps/api
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
pytest tests/e2e/ -v                     # E2E tests only
pytest -m slow -v                        # Slow tests only

# Run with coverage
make test-cov
# Or manually:
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run specific module
pytest tests/unit/test_auth.py -v
pytest tests/integration/test_project.py -v

# Run specific test class or method
pytest tests/unit/test_auth.py::TestRegisterUserUseCase -v
pytest tests/integration/test_auth.py::test_register_user -v
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Test domain use cases in isolation
- All repository dependencies are mocked with `AsyncMock`/`MagicMock`
- Fast execution, no I/O
- ~550 tests across all modules

### Integration Tests (`tests/integration/`)
- Test HTTP endpoints via `httpx.AsyncClient` with `ASGITransport`
- No real server needed (in-process testing)
- Each test registers a user, logs in, and gets an auth token
- Tests CRUD operations, validation, and error handling

### End-to-End Tests (`tests/e2e/`)
- Test cross-module workflows
- Verify modules work together in realistic scenarios
- Example: register -> create project -> add germplasm -> run analysis -> generate report

## Fixtures

Shared fixtures in `tests/conftest.py`:

| Fixture | Description |
|---------|-------------|
| `client` | `httpx.AsyncClient` wired to FastAPI app |
| `auth_client` | Returns `(client, auth_header)` tuple |
| `sample_user` | Default user registration data |
| `sample_project` | Default project data |
| `sample_species` | Default species data |
| `sample_accession` | Default accession data |
| `sample_sequence` | Default genomic sequence data |

## Factories

Test data factories in `tests/factories.py`:

```python
from tests.factories import UserFactory, ProjectFactory, SequenceFactory

# Generate unique test data
user = UserFactory.build()           # auto-generates unique email
project = ProjectFactory.build(name="Custom Name")
sequence = SequenceFactory.build(species_name="Oryza sativa")
```

Available factories:
- `UserFactory`, `ProjectFactory`, `SpeciesFactory`, `AccessionFactory`
- `SequenceFactory`, `VariantFactory`, `AnnotationFactory`
- `ExperimentFactory`, `TraitFactory`, `MeasurementFactory`
- `MolecularExperimentFactory`, `PrimerFactory`, `ConstructFactory`
- `PaperFactory`, `CollectionFactory`, `NoteFactory`
- `EntityFactory`, `EdgeFactory`
- `ConversationFactory`, `MessageFactory`
- `AnalysisJobFactory`, `PipelineTemplateFactory`
- `ReportFactory`, `ReportTemplateFactory`

## Coverage

Coverage configuration in `pyproject.toml`:
- Minimum threshold: **70%**
- Source: `app/`
- Excludes: tests, migrations, `__pycache__`

```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Writing New Tests

### Unit Test Pattern
```python
class TestMyUseCase:
    def setup_method(self):
        self.repo = AsyncMock(spec=MyRepositoryInterface)
        self.use_case = CreateMyThingUseCase(self.repo)

    async def test_success(self):
        self.repo.create.return_value = MyModel(id="1", name="test")
        result = await self.use_case.execute(name="test")
        assert result.name == "test"
        self.repo.create.assert_called_once()

    async def test_not_found(self):
        self.repo.get.return_value = None
        with pytest.raises(NotFoundError):
            await self.use_case.execute(id="nonexistent")
```

### Integration Test Pattern
```python
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_header(client, sample_user):
    client.post("/api/v1/auth/register", json=sample_user)
    login = client.post("/api/v1/auth/login", json={...})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestMyEndpoint:
    @pytest.mark.asyncio
    async def test_create(self, client, auth_header):
        response = await client.post("/api/v1/my/", json={...}, headers=auth_header)
        assert response.status_code == 201
```

## CI Integration

Tests run automatically in CI (`.github/workflows/ci.yml`):
1. Lint (Ruff, MyPy, ESLint)
2. Unit tests with coverage upload to Codecov
3. Integration tests with PostgreSQL service
4. Docker build verification
