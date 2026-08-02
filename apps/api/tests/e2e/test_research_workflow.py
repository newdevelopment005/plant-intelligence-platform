"""End-to-end tests covering cross-module workflows.

These tests verify that multiple modules work together correctly
in realistic research scenarios.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def researcher():
    return {
        "email": "e2e_researcher@test.edu",
        "password": "TestPass123!",
        "full_name": "Dr. E2E Researcher",
        "institution": "Plant Intelligence Lab",
        "department": "Genomics",
    }


@pytest.fixture
async def auth(client, researcher):
    await client.post("/api/v1/auth/register", json=researcher)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": researcher["email"], "password": researcher["password"]},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


class TestResearchWorkflow:
    """Full workflow: user registers -> creates project -> adds germplasm -> runs analysis -> generates report."""

    @pytest.mark.asyncio
    async def test_complete_research_pipeline(self, client, auth):
        # Step 1: Create a project
        project = await client.post(
            "/api/v1/projects",
            json={
                "name": "Wheat Drought Genomics",
                "description": "Multi-omics study of drought tolerance",
                "tags": ["drought", "wheat", "genomics"],
            },
            headers=auth,
        )
        assert project.status_code == 201
        project_id = project.json()["id"]

        # Step 2: Create germplasm species
        species = await client.post(
            "/api/v1/germplasm/species",
            json={
                "scientific_name": "Triticum aestivum",
                "common_name": "Bread Wheat",
                "family": "Poaceae",
            },
            headers=auth,
        )
        assert species.status_code == 201

        # Step 3: Create an accession
        accession = await client.post(
            "/api/v1/germplasm/accessions",
            json={
                "accession_number": "WHEAT-001",
                "name": "Drought Line 1",
                "species_name": "Triticum aestivum",
                "origin_country": "USA",
            },
            headers=auth,
        )
        assert accession.status_code == 201

        # Step 4: Create a genomic sequence
        sequence = await client.post(
            "/api/v1/genomics/sequences",
            json={
                "name": "TaDREB2A",
                "sequence": "ATGCGATCGATCG" * 20,
                "sequence_type": "gene",
                "species_name": "Triticum aestivum",
            },
            headers=auth,
        )
        assert sequence.status_code == 201
        sequence_id = sequence.json()["id"]

        # Step 5: Add a variant to the sequence
        variant = await client.post(
            f"/api/v1/genomics/sequences/{sequence_id}/variants",
            json={
                "name": "DREB2A_SNP1",
                "chromosome": "3A",
                "position": 12345,
                "reference_allele": "A",
                "alternative_allele": "G",
                "variant_type": "SNP",
            },
            headers=auth,
        )
        assert variant.status_code == 201

        # Step 6: Create a phenotyping experiment
        phenotype_exp = await client.post(
            "/api/v1/phenotyping/experiments",
            json={
                "name": "Drought Phenotyping",
                "description": "Measuring growth under water deficit",
                "experiment_type": "greenhouse",
            },
            headers=auth,
        )
        assert phenotype_exp.status_code == 201

        # Step 7: Create a literature collection
        collection = await client.post(
            "/api/v1/literature/collections",
            json={
                "name": "Drought References",
                "description": "Key papers on drought tolerance",
            },
            headers=auth,
        )
        assert collection.status_code == 201

        # Step 8: Add a paper
        paper = await client.post(
            "/api/v1/literature/papers",
            json={
                "title": "DREB2A regulates drought response in wheat",
                "authors": ["Zhang et al."],
                "doi": "10.1000/drought.2024.001",
                "year": 2024,
            },
            headers=auth,
        )
        assert paper.status_code == 201

        # Step 9: Create a knowledge graph entity
        entity = await client.post(
            "/api/v1/knowledge-graph/entities",
            json={
                "name": "TaDREB2A",
                "entity_type": "gene",
                "description": "Key drought tolerance gene",
                "properties": {"chromosome": "3A", "function": "stress response"},
            },
            headers=auth,
        )
        assert entity.status_code == 201

        # Step 10: Create a report
        report = await client.post(
            "/api/v1/reports/",
            json={
                "title": "Drought Genomics Report",
                "report_type": "summary",
                "content": "Summary of drought genomics findings",
            },
            headers=auth,
        )
        assert report.status_code == 201

        # Verify all resources exist
        assert project.json()["name"] == "Wheat Drought Genomics"
        assert sequence.json()["name"] == "TaDREB2A"
        assert entity.json()["entity_type"] == "gene"


class TestAuthCrossModule:
    """Verify auth state persists across module calls."""

    @pytest.mark.asyncio
    async def test_single_login_multiple_modules(self, client, auth):
        # Use same auth token across different modules
        projects = await client.get("/api/v1/projects", headers=auth)
        assert projects.status_code == 200

        species = await client.get("/api/v1/germplasm/species", headers=auth)
        assert species.status_code == 200

        sequences = await client.get("/api/v1/genomics/sequences", headers=auth)
        assert sequences.status_code == 200

        papers = await client.get("/api/v1/literature/papers", headers=auth)
        assert papers.status_code == 200

        entities = await client.get("/api/v1/knowledge-graph/entities", headers=auth)
        assert entities.status_code == 200

        reports = await client.get("/api/v1/reports/", headers=auth)
        assert reports.status_code == 200

    @pytest.mark.asyncio
    async def test_unauthenticated_access_denied(self, client):
        endpoints = [
            "/api/v1/projects",
            "/api/v1/germplasm/species",
            "/api/v1/genomics/sequences",
            "/api/v1/phenotyping/experiments",
            "/api/v1/molecular/experiments",
            "/api/v1/literature/papers",
            "/api/v1/knowledge-graph/entities",
            "/api/v1/ai/conversations",
            "/api/v1/bioinformatics/jobs",
            "/api/v1/reports/",
        ]
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code in (401, 403), f"{endpoint} should require auth"


class TestPagination:
    """Verify pagination works consistently across modules."""

    @pytest.mark.asyncio
    async def test_project_pagination(self, client, auth):
        for i in range(5):
            await client.post(
                "/api/v1/projects",
                json={"name": f"Project {i}"},
                headers=auth,
            )

        page1 = await client.get("/api/v1/projects?page=1&page_size=2", headers=auth)
        assert page1.status_code == 200
        data = page1.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5

    @pytest.mark.asyncio
    async def test_sequences_pagination(self, client, auth):
        for i in range(3):
            await client.post(
                "/api/v1/genomics/sequences",
                json={
                    "name": f"Seq{i}",
                    "sequence": "ATCG",
                    "sequence_type": "gene",
                    "species_name": "Triticum aestivum",
                },
                headers=auth,
            )

        response = await client.get(
            "/api/v1/genomics/sequences?page=1&page_size=2", headers=auth
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) == 2
