
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
        "email": "researcher@test.edu",
        "password": "TestPass123!",
        "full_name": "Dr. Smith",
        "institution": "Plant Research Lab",
        "department": "Genomics",
    }


@pytest.fixture
def sample_project():
    return {
        "name": "Drought Resistance Study",
        "description": "Investigating wheat drought tolerance mechanisms",
        "tags": ["drought", "wheat", "genetics"],
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


class TestProjectEndpoints:
    @pytest.mark.asyncio
    async def test_create_project(self, client, auth_header, sample_project):
        response = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_project["name"]
        assert data["status"] == "active"
        assert data["tags"] == sample_project["tags"]

    @pytest.mark.asyncio
    async def test_create_project_no_auth(self, client, sample_project):
        response = await client.post("/api/v1/projects", json=sample_project)
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_create_project_empty_name(self, client, auth_header):
        response = await client.post(
            "/api/v1/projects",
            json={"name": ""},
            headers=auth_header,
        )
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_list_projects(self, client, auth_header, sample_project):
        await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        response = await client.get("/api/v1/projects", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_projects_with_search(self, client, auth_header, sample_project):
        await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        response = await client.get(
            "/api/v1/projects?search=Drought",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_projects_with_status_filter(
        self, client, auth_header, sample_project
    ):
        await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        response = await client.get(
            "/api/v1/projects?status=active",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_project(self, client, auth_header, sample_project):
        create_resp = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        project_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_project["name"]

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client, auth_header):
        response = await client.get(
            "/api/v1/projects/nonexistent-id",
            headers=auth_header,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project(self, client, auth_header, sample_project):
        create_resp = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        project_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/projects/{project_id}",
            json={"name": "Updated Project Name"},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project Name"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, client, auth_header):
        response = await client.put(
            "/api/v1/projects/nonexistent-id",
            json={"name": "X"},
            headers=auth_header,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project(self, client, auth_header, sample_project):
        create_resp = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        project_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=auth_header,
        )
        assert response.status_code == 200

        get_resp = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_header,
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, client, auth_header):
        response = await client.delete(
            "/api/v1/projects/nonexistent-id",
            headers=auth_header,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_member(self, client, auth_header, sample_project):
        create_resp = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        project_id = create_resp.json()["id"]

        response = await client.post(
            f"/api/v1/projects/{project_id}/members",
            json={"user_id": "user-other-123", "role": "researcher"},
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_members(self, client, auth_header, sample_project):
        create_resp = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        project_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/members",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_update_member_role(self, client, auth_header, sample_project):
        create_resp = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        project_id = create_resp.json()["id"]

        await client.post(
            f"/api/v1/projects/{project_id}/members",
            json={"user_id": "user-other-456", "role": "researcher"},
            headers=auth_header,
        )

        response = await client.put(
            f"/api/v1/projects/{project_id}/members/user-other-456",
            json={"role": "principal_investigator"},
            headers=auth_header,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_remove_member(self, client, auth_header, sample_project):
        create_resp = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_header,
        )
        project_id = create_resp.json()["id"]

        await client.post(
            f"/api/v1/projects/{project_id}/members",
            json={"user_id": "user-other-789", "role": "technician"},
            headers=auth_header,
        )

        response = await client.delete(
            f"/api/v1/projects/{project_id}/members/user-other-789",
            headers=auth_header,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_projects_pagination(self, client, auth_header):
        for i in range(5):
            await client.post(
                "/api/v1/projects",
                json={"name": f"Project {i}"},
                headers=auth_header,
            )

        response = await client.get(
            "/api/v1/projects?page=1&page_size=2",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5
