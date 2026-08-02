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
        "email": "genomics@test.edu",
        "password": "TestPass123!",
        "full_name": "Genomics Researcher",
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


class TestGenomicsSequences:
    @pytest.mark.asyncio
    async def test_create_sequence(self, client, auth_header):
        response = await client.post(
            "/api/v1/genomics/sequences",
            json={
                "name": "TaDREB2A",
                "sequence": "ATGCGATCGATCG" * 10,
                "sequence_type": "gene",
                "species_name": "Triticum aestivum",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "TaDREB2A"
        assert data["sequence_type"] == "gene"

    @pytest.mark.asyncio
    async def test_list_sequences(self, client, auth_header):
        await client.post(
            "/api/v1/genomics/sequences",
            json={
                "name": "Seq1",
                "sequence": "ATCGATCG",
                "sequence_type": "gene",
                "species_name": "Triticum aestivum",
            },
            headers=auth_header,
        )
        response = await client.get("/api/v1/genomics/sequences", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_sequence(self, client, auth_header):
        create = await client.post(
            "/api/v1/genomics/sequences",
            json={
                "name": "GetMe",
                "sequence": "ATCG",
                "sequence_type": "gene",
                "species_name": "Triticum aestivum",
            },
            headers=auth_header,
        )
        seq_id = create.json()["id"]
        response = await client.get(
            f"/api/v1/genomics/sequences/{seq_id}", headers=auth_header
        )
        assert response.status_code == 200
        assert response.json()["name"] == "GetMe"

    @pytest.mark.asyncio
    async def test_update_sequence(self, client, auth_header):
        create = await client.post(
            "/api/v1/genomics/sequences",
            json={
                "name": "UpdateMe",
                "sequence": "ATCG",
                "sequence_type": "gene",
                "species_name": "Triticum aestivum",
            },
            headers=auth_header,
        )
        seq_id = create.json()["id"]
        response = await client.put(
            f"/api/v1/genomics/sequences/{seq_id}",
            json={"name": "Updated"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    @pytest.mark.asyncio
    async def test_delete_sequence(self, client, auth_header):
        create = await client.post(
            "/api/v1/genomics/sequences",
            json={
                "name": "DeleteMe",
                "sequence": "ATCG",
                "sequence_type": "gene",
                "species_name": "Triticum aestivum",
            },
            headers=auth_header,
        )
        seq_id = create.json()["id"]
        response = await client.delete(
            f"/api/v1/genomics/sequences/{seq_id}", headers=auth_header
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_sequence_not_found(self, client, auth_header):
        response = await client.get(
            "/api/v1/genomics/sequences/nonexistent", headers=auth_header
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_variant(self, client, auth_header):
        create = await client.post(
            "/api/v1/genomics/sequences",
            json={
                "name": "VarSeq",
                "sequence": "ATCG",
                "sequence_type": "gene",
                "species_name": "Triticum aestivum",
            },
            headers=auth_header,
        )
        seq_id = create.json()["id"]
        response = await client.post(
            f"/api/v1/genomics/sequences/{seq_id}/variants",
            json={
                "name": "SNP1",
                "chromosome": "1A",
                "position": 100,
                "reference_allele": "A",
                "alternative_allele": "T",
                "variant_type": "SNP",
            },
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_annotation(self, client, auth_header):
        create = await client.post(
            "/api/v1/genomics/sequences",
            json={
                "name": "AnnoSeq",
                "sequence": "ATCG",
                "sequence_type": "gene",
                "species_name": "Triticum aestivum",
            },
            headers=auth_header,
        )
        seq_id = create.json()["id"]
        response = await client.post(
            f"/api/v1/genomics/sequences/{seq_id}/annotations",
            json={
                "name": "Promoter",
                "annotation_type": "regulatory",
                "start_position": 1,
                "end_position": 500,
            },
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_no_auth(self, client):
        response = await client.get("/api/v1/genomics/sequences")
        assert response.status_code in (401, 403)
