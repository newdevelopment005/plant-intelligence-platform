import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm, get_llm_mini
from app.tools.external_tools import search_pubmed, search_uniprot, get_gene_info

logger = structlog.get_logger()

KNOWLEDGE_SYSTEM_PROMPT = """You are PIP Knowledge Graph Assistant, an expert in plant science knowledge representation.

You help researchers:
- Explore relationships between genes, proteins, traits, and pathways
- Identify connections across biological databases
- Generate hypotheses from knowledge graph patterns
- Discover potential gene-trait associations
- Map metabolic and signaling pathways

Rules:
- Base recommendations on published evidence
- Clearly state confidence levels
- Direct verified relationships from predicted ones
- Recommend validation for novel predictions
- Use standard biological nomenclature"""


async def query_knowledge_graph(
    query: str,
    entity_type: str | None = None,
    max_depth: int = 2,
) -> dict:
    """Query the knowledge graph with natural language."""
    llm = get_llm()

    entity_str = f"Entity type filter: {entity_type}" if entity_type else "All entity types"

    prompt = f"""Answer this knowledge graph query: {query}

{entity_str}
Search depth: {max_depth} hops

1. Identify relevant entities and relationships
2. Search PubMed for supporting evidence
3. Search UniProt for protein relationships
4. Map the connections found
5. Provide a structured answer

Include:
- Direct relationships found
- Indirect connections (if depth > 1)
- Confidence level for each relationship
- Supporting evidence (PMIDs where available)
- Suggested follow-up queries"""

    messages = [
        SystemMessage(content=KNOWLEDGE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "response": response.content,
            "query": query,
            "entity_type": entity_type,
        }
    except Exception as e:
        logger.error("kg_query_failed", error=str(e))
        return {
            "response": "Unable to query knowledge graph at this time.",
            "query": query,
        }


async def explore_entity(
    entity_name: str,
    entity_type: str = "gene",
    depth: int = 2,
) -> dict:
    """Explore connections for a specific entity."""
    llm = get_llm()

    # Gather real data about the entity
    entity_info = {}

    if entity_type == "gene":
        gene_data = await get_gene_info(entity_name)
        entity_info["gene_data"] = gene_data

    pubmed_results = await search_pubmed(f"{entity_name} {entity_type} plant", max_results=3)
    entity_info["related_papers"] = pubmed_results

    prompt = f"""Explore the knowledge graph for: {entity_name} (type: {entity_type})

Available data:
{entity_info}

Provide:
1. Entity description and function
2. Direct relationships (1-hop)
3. Indirect relationships (2-hop)
4. Related pathways
5. Associated publications
6. Potential novel connections
7. Confidence levels for each connection
8. Suggested experiments to validate novel connections

Use the retrieved data to provide evidence-based answers."""

    messages = [
        SystemMessage(content=KNOWLEDGE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "response": response.content,
            "entity": entity_name,
            "entity_type": entity_type,
            "data_sources": list(entity_info.keys()),
        }
    except Exception as e:
        logger.error("entity_exploration_failed", error=str(e))
        return {
            "response": f"Unable to explore entity {entity_name}.",
            "entity": entity_name,
        }


async def infer_relationships(
    entity_a: str,
    entity_b: str,
    context: str | None = None,
) -> dict:
    """Infer potential relationships between two entities."""
    llm = get_llm()

    context_str = f"Additional context: {context}" if context else ""

    prompt = f"""Infer potential relationships between: {entity_a} and {entity_b}

{context_str}

1. Search for direct evidence connecting these entities
2. Search for indirect connections through intermediaries
3. Evaluate the biological plausibility
4. Assess evidence strength
5. Identify potential mechanisms

For each inferred relationship:
- Describe the relationship type
- Provide supporting evidence
- Assign confidence level (High/Medium/Low)
- Suggest validation experiments
- Note any contradictions found

Be cautious and evidence-based. Clearly distinguish verified from predicted relationships."""

    messages = [
        SystemMessage(content=KNOWLEDGE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "response": response.content,
            "entity_a": entity_a,
            "entity_b": entity_b,
        }
    except Exception as e:
        logger.error("relationship_inference_failed", error=str(e))
        return {
            "response": "Unable to infer relationships at this time.",
            "entity_a": entity_a,
            "entity_b": entity_b,
        }
