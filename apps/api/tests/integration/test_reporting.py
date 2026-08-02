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
        "email": "reporting@test.edu",
        "password": "TestPass123!",
        "full_name": "Report Writer",
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


class TestReporting:
    @pytest.mark.asyncio
    async def test_create_report(self, client, auth_header):
        response = await client.post(
            "/api/v1/reports/",
            json={
                "title": "Q4 Summary",
                "report_type": "summary",
                "content": "Quarterly progress report",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Q4 Summary"

    @pytest.mark.asyncio
    async def test_list_reports(self, client, auth_header):
        await client.post(
            "/api/v1/reports/",
            json={"title": "R1", "report_type": "summary"},
            headers=auth_header,
        )
        response = await client.get("/api/v1/reports/", headers=auth_header)
        assert response.status_code == 200
        assert "items" in response.json()

    @pytest.mark.asyncio
    async def test_create_template(self, client, auth_header):
        response = await client.post(
            "/api/v1/reports/templates",
            json={
                "name": "Experiment Template",
                "report_type": "experiment",
                "description": "Standard experiment report",
                "sections": ["Intro", "Methods", "Results"],
            },
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_templates(self, client, auth_header):
        response = await client.get("/api/v1/reports/templates", headers=auth_header)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_auth(self, client):
        response = await client.get("/api/v1/reports/")
        assert response.status_code in (401, 403)
