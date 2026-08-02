import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

# =============================================
# HTTP Client Fixtures
# =============================================

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_client(client, sample_user):
    """Returns (client, auth_header) tuple with a logged-in user."""
    await client.post("/api/v1/auth/register", json=sample_user)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    token = login.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


# =============================================
# Sample Data Fixtures
# =============================================

@pytest.fixture
def sample_user():
    return {
        "email": "researcher@test.edu",
        "password": "TestPass123!",
        "full_name": "Dr. Smith",
        "institution": "Plant Research Lab",
        "department": "Genomics",
    }


@pytest.fixture
def sample_user_2():
    return {
        "email": "tech@test.edu",
        "password": "TestPass456!",
        "full_name": "Lab Tech",
        "institution": "Plant Research Lab",
        "department": "Molecular Biology",
    }


@pytest.fixture
def sample_project():
    return {
        "name": "Drought Resistance Study",
        "description": "Investigating wheat drought tolerance mechanisms",
        "tags": ["drought", "wheat", "genetics"],
    }


@pytest.fixture
def sample_species():
    return {
        "scientific_name": "Triticum aestivum",
        "common_name": "Bread Wheat",
        "family": "Poaceae",
        "genus": "Triticum",
    }


@pytest.fixture
def sample_accession():
    return {
        "accession_number": "ACC-001",
        "name": "Wheat Drought Line 1",
        "species_name": "Triticum aestivum",
        "origin_country": "USA",
        "collection_year": 2024,
        "status": "active",
    }


@pytest.fixture
def sample_sequence():
    return {
        "name": "TaDREB2A",
        "sequence": "ATGGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCG",
        "sequence_type": "gene",
        "species_name": "Triticum aestivum",
        "description": "DREB2A transcription factor",
    }


@pytest.fixture
def sample_experiment():
    return {
        "name": "Drought Stress Phenotyping",
        "description": "Measuring growth under water deficit",
        "experiment_type": "field",
        "status": "planning",
    }


@pytest.fixture
def sample_molecular_experiment():
    return {
        "name": "CRISPR Knockout Screen",
        "description": "Targeting drought tolerance genes",
        "experiment_type": "crispr",
        "status": "planning",
    }


@pytest.fixture
def sample_paper():
    return {
        "title": "Drought tolerance mechanisms in wheat",
        "authors": ["Smith J.", "Jones A."],
        "abstract": "We investigate the genetic basis of drought tolerance...",
        "doi": "10.1000/example.2024.001",
        "year": 2024,
        "source": "pubmed",
    }


@pytest.fixture
def sample_entity():
    return {
        "name": "TaDREB2A",
        "entity_type": "gene",
        "description": "DREB2A transcription factor in wheat",
        "properties": {"chromosome": "3A", "function": "stress response"},
    }


@pytest.fixture
def sample_report():
    return {
        "title": "Q4 Research Summary",
        "report_type": "summary",
        "content": "Quarterly research progress report",
    }


@pytest.fixture
def sample_template():
    return {
        "name": "Standard Experiment Report",
        "report_type": "experiment",
        "description": "Template for experiment reports",
        "sections": ["Introduction", "Methods", "Results", "Discussion"],
    }
