import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_user():
    return {
        "email": "bioinfo@test.edu",
        "password": "TestPass123!",
        "full_name": "Bioinformatician",
        "institution": "Plant Research Lab",
    }


@pytest.fixture
def auth_header(client, sample_user):
    client.post("/api/v1/auth/register", json=sample_user)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestBioinformaticsJobs:
    @pytest.mark.asyncio
    async def test_create_job(self, client, auth_header):
        response = await client.post(
            "/api/v1/bioinformatics/jobs",
            json={
                "name": "Alignment Job",
                "analysis_type": "alignment",
                "description": "Aligning wheat reads",
                "input_data": {"file": "sample.fasta"},
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Alignment Job"

    @pytest.mark.asyncio
    async def test_list_jobs(self, client, auth_header):
        await client.post(
            "/api/v1/bioinformatics/jobs",
            json={
                "name": "Job1",
                "analysis_type": "alignment",
                "input_data": {},
            },
            headers=auth_header,
        )
        response = await client.get("/api/v1/bioinformatics/jobs", headers=auth_header)
        assert response.status_code == 200
        assert "items" in response.json()

    @pytest.mark.asyncio
    async def test_create_template(self, client, auth_header):
        response = await client.post(
            "/api/v1/bioinformatics/templates",
            json={
                "name": "RNA-seq Pipeline",
                "analysis_type": "rnaseq",
                "description": "Standard RNA-seq pipeline",
                "steps": ["fastqc", "trim", "align", "quantify"],
            },
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_templates(self, client, auth_header):
        response = await client.get(
            "/api/v1/bioinformatics/templates", headers=auth_header
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_auth(self, client):
        response = await client.get("/api/v1/bioinformatics/jobs")
        assert response.status_code in (401, 403)
