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
        "email": "kg@test.edu",
        "password": "TestPass123!",
        "full_name": "KG Researcher",
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


class TestKnowledgeGraphEntities:
    @pytest.mark.asyncio
    async def test_create_entity(self, client, auth_header):
        response = await client.post(
            "/api/v1/knowledge-graph/entities",
            json={
                "name": "TaDREB2A",
                "entity_type": "gene",
                "description": "DREB2A transcription factor",
                "properties": {"chromosome": "3A"},
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["name"] == "TaDREB2A"

    @pytest.mark.asyncio
    async def test_list_entities(self, client, auth_header):
        await client.post(
            "/api/v1/knowledge-graph/entities",
            json={"name": "Gene1", "entity_type": "gene"},
            headers=auth_header,
        )
        response = await client.get(
            "/api/v1/knowledge-graph/entities", headers=auth_header
        )
        assert response.status_code == 200
        assert "items" in response.json()

    @pytest.mark.asyncio
    async def test_create_edge(self, client, auth_header):
        e1 = await client.post(
            "/api/v1/knowledge-graph/entities",
            json={"name": "Source", "entity_type": "gene"},
            headers=auth_header,
        )
        e2 = await client.post(
            "/api/v1/knowledge-graph/entities",
            json={"name": "Target", "entity_type": "protein"},
            headers=auth_header,
        )
        response = await client.post(
            "/api/v1/knowledge-graph/edges",
            json={
                "source_entity_id": e1.json()["id"],
                "target_entity_id": e2.json()["id"],
                "relation_type": "ENCODES",
            },
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_explore_entity(self, client, auth_header):
        e1 = await client.post(
            "/api/v1/knowledge-graph/entities",
            json={"name": "Explore", "entity_type": "gene"},
            headers=auth_header,
        )
        entity_id = e1.json()["id"]
        response = await client.get(
            f"/api/v1/knowledge-graph/entities/{entity_id}/explore",
            headers=auth_header,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_relation_types(self, client, auth_header):
        response = await client.get(
            "/api/v1/knowledge-graph/relations", headers=auth_header
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_auth(self, client):
        response = await client.get("/api/v1/knowledge-graph/entities")
        assert response.status_code in (401, 403)
