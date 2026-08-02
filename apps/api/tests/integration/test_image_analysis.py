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
        "email": "images@test.edu",
        "password": "TestPass123!",
        "full_name": "Image Analyst",
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


class TestImageAnalysis:
    @pytest.mark.asyncio
    async def test_list_images(self, client, auth_header):
        response = await client.get("/api/v1/images/", headers=auth_header)
        assert response.status_code == 200
        assert "items" in response.json()

    @pytest.mark.asyncio
    async def test_no_auth(self, client):
        response = await client.get("/api/v1/images/")
        assert response.status_code in (401, 403)
