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
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "institution": "Test University",
        "department": "Plant Science",
    }


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client, sample_user):
    response = await client.post("/api/v1/auth/register", json=sample_user)
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "user" in data
    assert data["user"]["email"] == sample_user["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    response = await client.post("/api/v1/auth/register", json=sample_user)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "invalid", "password": "TestPass123!", "full_name": "Test"},
    )
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_login_success(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == sample_user["email"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": "WrongPassword123!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "TestPass123!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user["email"]
    assert data["full_name"] == sample_user["full_name"]


@pytest.mark.asyncio
async def test_get_profile_no_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_update_profile(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    token = login_response.json()["access_token"]

    response = await client.put(
        "/api/v1/auth/me",
        json={"bio": "Plant researcher", "orcid_id": "0000-0001-2345-6789"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == "Plant researcher"
    assert data["orcid_id"] == "0000-0001-2345-6789"


@pytest.mark.asyncio
async def test_forgot_password(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": sample_user["email"]},
    )
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_forgot_password_nonexistent_email(client):
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": sample_user["password"],
            "new_password": "NewPassword456!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": "NewPassword456!"},
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword456!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_logout(client, sample_user):
    await client.post("/api/v1/auth/register", json=sample_user)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    data = login_response.json()
    token = data["access_token"]
    refresh = data["refresh_token"]

    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "message" in response.json()
