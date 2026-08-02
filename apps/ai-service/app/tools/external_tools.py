import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UNIPROT_BASE = "https://rest.uniprot.org"
NCBI_GENE_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


async def search_pubmed(query: str, max_results: int = 10) -> list[dict]:
    """Search PubMed for scientific papers."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            search_resp = await client.get(
                f"{PUBMED_BASE}/esearch.fcgi",
                params={
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "json",
                    "sort": "relevance",
                },
            )
            search_resp.raise_for_status()
            ids = search_resp.json().get("esearchresult", {}).get("idlist", [])

            if not ids:
                return []

            detail_resp = await client.get(
                f"{PUBMED_BASE}/esummary.fcgi",
                params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
            )
            detail_resp.raise_for_status()
            results = detail_resp.json().get("result", {})

            papers = []
            for uid in ids:
                doc = results.get(uid, {})
                if not doc or isinstance(doc, str):
                    continue
                papers.append({
                    "pmid": uid,
                    "title": doc.get("title", ""),
                    "authors": [a.get("name", "") for a in doc.get("authors", [])],
                    "journal": doc.get("fulljournalname", ""),
                    "year": doc.get("pubdate", "")[:4] if doc.get("pubdate") else None,
                    "doi": next(
                        (eid.get("value") for eid in doc.get("articleids", []) if eid.get("idtype") == "doi"),
                        None,
                    ),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                })
            return papers
        except Exception as e:
            logger.error("pubmed_search_failed", error=str(e))
            return []


async def get_pubmed_abstract(pmid: str) -> str:
    """Fetch full abstract from PubMed."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                f"{PUBMED_BASE}/efetch.fcgi",
                params={"db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "text"},
            )
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.error("pubmed_abstract_failed", pmid=pmid, error=str(e))
            return ""


async def search_uniprot(query: str, max_results: int = 5) -> list[dict]:
    """Search UniProt for protein information."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                f"{UNIPROT_BASE}/uniprotkb/search",
                params={
                    "query": query,
                    "format": "json",
                    "size": max_results,
                },
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            return [
                {
                    "accession": r.get("primaryAccession", ""),
                    "name": r.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", ""),
                    "organism": r.get("organism", {}).get("scientificName", ""),
                    "function": next(
                        (c.get("commentText", "") for c in r.get("comments", []) if c.get("commentType") == "FUNCTION"),
                        "",
                    ),
                    "url": f"https://www.uniprot.org/uniprotkb/{r.get('primaryAccession', '')}",
                }
                for r in results
            ]
        except Exception as e:
            logger.error("uniprot_search_failed", error=str(e))
            return []


async def get_gene_info(gene_id: str) -> dict:
    """Get gene information from NCBI Gene."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                f"{NCBI_GENE_BASE}/esummary.fcgi",
                params={"db": "gene", "id": gene_id, "retmode": "json"},
            )
            resp.raise_for_status()
            result = resp.json().get("result", {})
            doc = result.get(gene_id, {})
            if not doc or isinstance(doc, str):
                return {"error": "Gene not found"}
            return {
                "gene_id": gene_id,
                "name": doc.get("name", ""),
                "description": doc.get("description", ""),
                "organism": doc.get("organism", {}).get("scientificname", ""),
                "chromosome": doc.get("chromosome", ""),
                "map_location": doc.get("maplocation", ""),
                "aliases": doc.get("aliases", []),
                "type_of_gene": doc.get("typegenefromsource", ""),
            }
        except Exception as e:
            logger.error("gene_info_failed", gene_id=gene_id, error=str(e))
            return {"error": str(e)}
