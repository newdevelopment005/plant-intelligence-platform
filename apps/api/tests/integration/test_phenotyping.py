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
        "email": "phenotyping@test.edu",
        "password": "TestPass123!",
        "full_name": "Phenomics Researcher",
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


class TestPhenotypingExperiments:
    @pytest.mark.asyncio
    async def test_create_experiment(self, client, auth_header):
        response = await client.post(
            "/api/v1/phenotyping/experiments",
            json={
                "name": "Height Trial",
                "description": "Measuring plant height",
                "experiment_type": "greenhouse",
                "status": "planning",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Height Trial"

    @pytest.mark.asyncio
    async def test_list_experiments(self, client, auth_header):
        await client.post(
            "/api/v1/phenotyping/experiments",
            json={"name": "Exp1", "experiment_type": "field"},
            headers=auth_header,
        )
        response = await client.get(
            "/api/v1/phenotyping/experiments", headers=auth_header
        )
        assert response.status_code == 200
        assert "items" in response.json()

    @pytest.mark.asyncio
    async def test_get_experiment(self, client, auth_header):
        create = await client.post(
            "/api/v1/phenotyping/experiments",
            json={"name": "GetMe", "experiment_type": "greenhouse"},
            headers=auth_header,
        )
        exp_id = create.json()["id"]
        response = await client.get(
            f"/api/v1/phenotyping/experiments/{exp_id}", headers=auth_header
        )
        assert response.status_code == 200
        assert response.json()["name"] == "GetMe"

    @pytest.mark.asyncio
    async def test_create_trait(self, client, auth_header):
        create = await client.post(
            "/api/v1/phenotyping/experiments",
            json={"name": "TraitExp", "experiment_type": "greenhouse"},
            headers=auth_header,
        )
        exp_id = create.json()["id"]
        response = await client.post(
            f"/api/v1/phenotyping/experiments/{exp_id}/traits",
            json={
                "name": "Plant Height",
                "description": "Height in cm",
                "trait_type": "quantitative",
                "unit": "cm",
            },
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_measurement(self, client, auth_header):
        create = await client.post(
            "/api/v1/phenotyping/experiments",
            json={"name": "MeasExp", "experiment_type": "greenhouse"},
            headers=auth_header,
        )
        exp_id = create.json()["id"]
        response = await client.post(
            f"/api/v1/phenotyping/experiments/{exp_id}/measurements",
            json={
                "trait_name": "Plant Height",
                "accession_number": "ACC-001",
                "value": 45.2,
                "replicate": 1,
            },
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_get_experiment_summary(self, client, auth_header):
        create = await client.post(
            "/api/v1/phenotyping/experiments",
            json={"name": "SummaryExp", "experiment_type": "greenhouse"},
            headers=auth_header,
        )
        exp_id = create.json()["id"]
        response = await client.get(
            f"/api/v1/phenotyping/experiments/{exp_id}/summary", headers=auth_header
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_auth(self, client):
        response = await client.get("/api/v1/phenotyping/experiments")
        assert response.status_code in (401, 403)
