from langchain_core.tools import tool


@tool
def search_pubmed(query: str, max_results: int = 10) -> str:
    """Search PubMed for scientific papers matching the query."""
    return f"PubMed search results for: {query}"


@tool
def search_uniprot(query: str) -> str:
    """Search UniProt for protein information."""
    return f"UniProt search results for: {query}"


@tool
def get_gene_info(gene_id: str) -> str:
    """Get detailed information about a specific gene."""
    return f"Gene information for: {gene_id}"


@tool
def query_neo4j(query: str) -> str:
    """Execute a Cypher query against the knowledge graph."""
    return f"Neo4j query results for: {query}"


@tool
def search_vectors(query: str, collection: str, limit: int = 10) -> str:
    """Search the vector store for semantically similar content."""
    return f"Vector search results for: {query} in {collection}"


@tool
def analyze_image_features(image_url: str) -> str:
    """Extract and analyze features from a plant image."""
    return f"Image analysis results for: {image_url}"


ALL_TOOLS = [
    search_pubmed,
    search_uniprot,
    get_gene_info,
    query_neo4j,
    search_vectors,
    analyze_image_features,
]
