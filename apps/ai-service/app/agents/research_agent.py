import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from app.core.llm import get_llm, get_llm_mini
from app.tools.external_tools import (
    search_pubmed,
    get_pubmed_abstract,
    search_uniprot,
    get_gene_info,
)

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are PIP Assistant, an expert multidisciplinary plant science research AI.

You specialize in:
- Plant Biology, Genetics, Genomics, Molecular Biology
- Plant Breeding, Pathology, Biotechnology
- Bioinformatics, Computational Biology
- Crop Science, Precision Agriculture

Rules:
- Always be scientifically accurate and evidence-based
- Never fabricate references or data
- Clearly distinguish evidence from hypothesis
- Recommend validation experiments
- Use proper scientific terminology
- When uncertain, say so explicitly
- Cite sources when available

You have access to PubMed, UniProt, and NCBI Gene databases.
Always retrieve real data before making scientific claims."""


@tool
def search_scientific_literature(query: str) -> str:
    """Search PubMed for scientific papers on a given topic. Returns titles, authors, PMIDs."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    papers = loop.run_until_complete(search_pubmed(query, max_results=5))
    if not papers:
        return "No papers found for this query."
    lines = []
    for p in papers:
        lines.append(f"- PMID:{p['pmid']} | {p['title']} | {p['journal']} ({p['year']})")
    return "\n".join(lines)


@tool
def get_paper_abstract(pmid: str) -> str:
    """Fetch the abstract of a PubMed paper by PMID."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_pubmed_abstract(pmid))


@tool
def search_protein_info(query: str) -> str:
    """Search UniProt for protein information."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    results = loop.run_until_complete(search_uniprot(query, max_results=3))
    if not results:
        return "No protein results found."
    lines = []
    for r in results:
        lines.append(f"- {r['accession']} | {r['name']} | {r['organism']}")
        if r.get("function"):
            lines.append(f"  Function: {r['function'][:200]}")
    return "\n".join(lines)


@tool
def get_gene_details(gene_id: str) -> str:
    """Get detailed information about a gene from NCBI Gene database."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    info = loop.run_until_complete(get_gene_info(gene_id))
    if "error" in info:
        return f"Error: {info['error']}"
    return (
        f"Gene: {info['name']} (ID: {gene_id})\n"
        f"Organism: {info['organism']}\n"
        f"Description: {info['description']}\n"
        f"Chromosome: {info['chromosome']}\n"
        f"Map Location: {info['map_location']}"
    )


def get_research_tools():
    return [
        search_scientific_literature,
        get_paper_abstract,
        search_protein_info,
        get_gene_details,
    ]


async def chat_with_research_agent(
    message: str,
    conversation_history: list[dict] | None = None,
    context: dict | None = None,
) -> dict:
    """Process a chat message through the research agent."""
    llm = get_llm()
    tools = get_research_tools()
    llm_with_tools = llm.bind_tools(tools)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    if conversation_history:
        for msg in conversation_history[-10:]:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(SystemMessage(content=msg["content"]))

    context_str = ""
    if context:
        if context.get("species"):
            context_str += f"Species context: {context['species']}\n"
        if context.get("gene"):
            context_str += f"Gene context: {context['gene']}\n"
        if context.get("trait"):
            context_str += f"Trait context: {context['trait']}\n"

    full_message = f"{context_str}\n{message}" if context_str else message
    messages.append(HumanMessage(content=full_message))

    try:
        response = await llm_with_tools.ainvoke(messages)
        return {
            "response": response.content,
            "tools_used": [t.name for t in response.tool_calls] if response.tool_calls else [],
        }
    except Exception as e:
        logger.error("research_chat_failed", error=str(e))
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "tools_used": [],
        }


async def recommend_genes(
    trait: str,
    species: str = "wheat",
    context: dict | None = None,
) -> dict:
    """Recommend candidate genes for a given trait."""
    llm = get_llm()
    tools = get_research_tools()
    llm_with_tools = llm.bind_tools(tools)

    prompt = f"""Based on current scientific literature, recommend candidate genes for the trait "{trait}" in {species}.

For each gene, provide:
1. Gene name and symbol
2. Known function
3. Evidence from published studies (with PMIDs if available)
4. Related pathways
5. Confidence level (High/Medium/Low)
6. Recommended validation experiments

Search PubMed for recent papers on {trait} in {species} genetics.
Also search UniProt for protein information on candidate genes.

Be thorough but honest about uncertainty."""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm_with_tools.ainvoke(messages)
        return {
            "response": response.content,
            "trait": trait,
            "species": species,
            "tools_used": [t.name for t in response.tool_calls] if response.tool_calls else [],
        }
    except Exception as e:
        logger.error("gene_recommendation_failed", error=str(e))
        return {
            "response": "Unable to generate gene recommendations at this time.",
            "trait": trait,
            "species": species,
        }


async def design_experiment(
    objective: str,
    species: str = "wheat",
    constraints: dict | None = None,
) -> dict:
    """Design a scientific experiment based on the given objective."""
    llm = get_llm()

    constraint_str = ""
    if constraints:
        if constraints.get("budget"):
            constraint_str += f"Budget: {constraints['budget']}\n"
        if constraints.get("duration"):
            constraint_str += f"Duration: {constraints['duration']}\n"
        if constraints.get("equipment"):
            constraint_str += f"Available equipment: {constraints['equipment']}\n"

    prompt = f"""Design a rigorous scientific experiment for the following objective:

Objective: {objective}
Species: {species}
{constraint_str}
Include:
1. Hypothesis
2. Experimental design (RCBD, CRD, or appropriate)
3. Variables (independent, dependent, controlled)
4. Treatments and controls
5. Replication and randomization
6. Sample size considerations
7. Statistical analysis plan
8. Expected timeline
9. Materials and reagents needed
10. Potential challenges and mitigation strategies

Follow the AI_BEHAVIOUR.md guidelines for experimental design."""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "response": response.content,
            "objective": objective,
            "species": species,
        }
    except Exception as e:
        logger.error("experiment_design_failed", error=str(e))
        return {
            "response": "Unable to design experiment at this time.",
            "objective": objective,
        }
