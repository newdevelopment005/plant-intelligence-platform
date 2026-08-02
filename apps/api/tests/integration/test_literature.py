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
        "email": "literature@test.edu",
        "password": "TestPass123!",
        "full_name": "Literature Researcher",
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


class TestLiteraturePapers:
    @pytest.mark.asyncio
    async def test_create_paper(self, client, auth_header):
        response = await client.post(
            "/api/v1/literature/papers",
            json={
                "title": "Drought Tolerance in Wheat",
                "authors": ["Smith J."],
                "abstract": "A study on drought tolerance mechanisms...",
                "doi": "10.1000/test.2024.001",
                "year": 2024,
                "source": "pubmed",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Drought Tolerance in Wheat"

    @pytest.mark.asyncio
    async def test_list_papers(self, client, auth_header):
        await client.post(
            "/api/v1/literature/papers",
            json={"title": "Paper1", "authors": ["A"], "year": 2024},
            headers=auth_header,
        )
        response = await client.get("/api/v1/literature/papers", headers=auth_header)
        assert response.status_code == 200
        assert "items" in response.json()

    @pytest.mark.asyncio
    async def test_create_collection(self, client, auth_header):
        response = await client.post(
            "/api/v1/literature/collections",
            json={
                "name": "Drought Papers",
                "description": "Collection of drought-related papers",
            },
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_add_paper_to_collection(self, client, auth_header):
        paper = await client.post(
            "/api/v1/literature/papers",
            json={"title": "ToCollection", "authors": ["A"], "year": 2024},
            headers=auth_header,
        )
        paper_id = paper.json()["id"]

        coll = await client.post(
            "/api/v1/literature/collections",
            json={"name": "My Collection"},
            headers=auth_header,
        )
        coll_id = coll.json()["id"]

        response = await client.post(
            f"/api/v1/literature/collections/{coll_id}/papers",
            json={"paper_id": paper_id},
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_note(self, client, auth_header):
        paper = await client.post(
            "/api/v1/literature/papers",
            json={"title": "Noted Paper", "authors": ["A"], "year": 2024},
            headers=auth_header,
        )
        paper_id = paper.json()["id"]

        response = await client.post(
            f"/api/v1/literature/papers/{paper_id}/notes",
            json={"content": "Important findings on page 5"},
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_no_auth(self, client):
        response = await client.get("/api/v1/literature/papers")
        assert response.status_code in (401, 403)
