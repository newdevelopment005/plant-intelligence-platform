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
        "email": "ai@test.edu",
        "password": "TestPass123!",
        "full_name": "AI Researcher",
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


class TestAIAssistantConversations:
    @pytest.mark.asyncio
    async def test_create_conversation(self, client, auth_header):
        response = await client.post(
            "/api/v1/ai/conversations",
            json={
                "title": "Drought Gene Analysis",
                "description": "Analyzing drought tolerance genes",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Drought Gene Analysis"

    @pytest.mark.asyncio
    async def test_list_conversations(self, client, auth_header):
        await client.post(
            "/api/v1/ai/conversations",
            json={"title": "Conv1"},
            headers=auth_header,
        )
        response = await client.get("/api/v1/ai/conversations", headers=auth_header)
        assert response.status_code == 200
        assert "items" in response.json()

    @pytest.mark.asyncio
    async def test_send_message(self, client, auth_header):
        conv = await client.post(
            "/api/v1/ai/conversations",
            json={"title": "MsgConv"},
            headers=auth_header,
        )
        conv_id = conv.json()["id"]
        response = await client.post(
            f"/api/v1/ai/conversations/{conv_id}/messages",
            json={"content": "What genes are involved in drought response?"},
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_messages(self, client, auth_header):
        conv = await client.post(
            "/api/v1/ai/conversations",
            json={"title": "ListMsg"},
            headers=auth_header,
        )
        conv_id = conv.json()["id"]
        await client.post(
            f"/api/v1/ai/conversations/{conv_id}/messages",
            json={"content": "Hello"},
            headers=auth_header,
        )
        response = await client.get(
            f"/api/v1/ai/conversations/{conv_id}/messages", headers=auth_header
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_auth(self, client):
        response = await client.get("/api/v1/ai/conversations")
        assert response.status_code in (401, 403)
