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
        "email": "germplasm@test.edu",
        "password": "TestPass123!",
        "full_name": "Germplasm Curator",
        "institution": "Seed Bank Institute",
        "department": "Germplasm Conservation",
    }


@pytest.fixture
def sample_species():
    return {
        "common_name": "Common wheat",
        "scientific_name": "Triticum aestivum",
        "family": "Poaceae",
        "genus": "Triticum",
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


class TestSpeciesEndpoints:
    @pytest.mark.asyncio
    async def test_create_species(self, client, auth_header, sample_species):
        response = await client.post(
            "/api/v1/germplasm/species",
            json=sample_species,
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["common_name"] == sample_species["common_name"]
        assert data["scientific_name"] == sample_species["scientific_name"]

    @pytest.mark.asyncio
    async def test_create_species_no_auth(self, client, sample_species):
        response = await client.post("/api/v1/germplasm/species", json=sample_species)
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_create_species_duplicate(self, client, auth_header, sample_species):
        await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        response = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_list_species(self, client, auth_header, sample_species):
        await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        response = await client.get("/api/v1/germplasm/species", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_species(self, client, auth_header, sample_species):
        create_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        species_id = create_resp.json()["id"]
        response = await client.get(f"/api/v1/germplasm/species/{species_id}", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["common_name"] == sample_species["common_name"]

    @pytest.mark.asyncio
    async def test_update_species(self, client, auth_header, sample_species):
        create_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        species_id = create_resp.json()["id"]
        response = await client.put(
            f"/api/v1/germplasm/species/{species_id}",
            json={"common_name": "Bread wheat"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["common_name"] == "Bread wheat"

    @pytest.mark.asyncio
    async def test_delete_species(self, client, auth_header, sample_species):
        create_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        species_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/germplasm/species/{species_id}", headers=auth_header)
        assert response.status_code == 200


class TestAccessionEndpoints:
    @pytest.fixture
    def sample_accession(self, sample_species):
        return {
            "accession_number": "PI 123456",
            "species_id": None,
            "name": "Wheat landrace from Nepal",
            "description": "Drought tolerant variety",
            "latitude": 27.7172,
            "longitude": 85.3240,
            "tags": ["drought", "nepal"],
        }

    @pytest.mark.asyncio
    async def test_create_accession(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        response = await client.post(
            "/api/v1/germplasm/accessions",
            json=sample_accession,
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["accession_number"] == "PI 123456"
        assert data["availability_status"] == "available"

    @pytest.mark.asyncio
    async def test_list_accessions(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        await client.post("/api/v1/germplasm/accessions", json=sample_accession, headers=auth_header)
        response = await client.get("/api/v1/germplasm/accessions", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    @pytest.mark.asyncio
    async def test_search_accessions(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        await client.post("/api/v1/germplasm/accessions", json=sample_accession, headers=auth_header)
        response = await client.get(
            "/api/v1/germplasm/accessions/search?q=wheat",
            headers=auth_header,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_accession(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        create_resp = await client.post(
            "/api/v1/germplasm/accessions",
            json=sample_accession,
            headers=auth_header,
        )
        accession_id = create_resp.json()["id"]
        response = await client.get(f"/api/v1/germplasm/accessions/{accession_id}", headers=auth_header)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_passport_data(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        acc_resp = await client.post("/api/v1/germplasm/accessions", json=sample_accession, headers=auth_header)
        accession_id = acc_resp.json()["id"]
        response = await client.post(
            f"/api/v1/germplasm/accessions/{accession_id}/passport",
            json={"institute_code": "IRRI", "country_code": "PH"},
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_pedigree(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        acc_resp = await client.post("/api/v1/germplasm/accessions", json=sample_accession, headers=auth_header)
        accession_id = acc_resp.json()["id"]
        response = await client.post(
            f"/api/v1/germplasm/accessions/{accession_id}/pedigree",
            json={"parent1_name": "Parent A", "cross_type": "single_cross"},
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_seed_storage(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        acc_resp = await client.post("/api/v1/germplasm/accessions", json=sample_accession, headers=auth_header)
        accession_id = acc_resp.json()["id"]
        response = await client.post(
            f"/api/v1/germplasm/accessions/{accession_id}/storage",
            json={"location": "Genebank Vault A", "quantity_grams": 100.5},
            headers=auth_header,
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_seed_storages(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        acc_resp = await client.post("/api/v1/germplasm/accessions", json=sample_accession, headers=auth_header)
        accession_id = acc_resp.json()["id"]
        await client.post(
            f"/api/v1/germplasm/accessions/{accession_id}/storage",
            json={"location": "Vault A"},
            headers=auth_header,
        )
        response = await client.get(f"/api/v1/germplasm/accessions/{accession_id}/storage", headers=auth_header)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    @pytest.mark.asyncio
    async def test_delete_accession(self, client, auth_header, sample_species, sample_accession):
        species_resp = await client.post("/api/v1/germplasm/species", json=sample_species, headers=auth_header)
        sample_accession["species_id"] = species_resp.json()["id"]
        create_resp = await client.post("/api/v1/germplasm/accessions", json=sample_accession, headers=auth_header)
        accession_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/germplasm/accessions/{accession_id}", headers=auth_header)
        assert response.status_code == 200
