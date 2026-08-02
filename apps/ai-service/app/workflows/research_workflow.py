from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict

from app.core.llm import get_llm
from app.tools.external_tools import search_pubmed, search_uniprot, get_gene_info

import structlog

logger = structlog.get_logger()


class AgentState(TypedDict):
    user_query: str
    query_type: str
    context: list[str]
    plan: list[str]
    gathered_evidence: list[dict]
    current_step: str
    response: str
    confidence: str
    sources: list[dict]


QUERY_TYPES = {
    "gene": ["gene", "gen", "allele", "locus", "marker"],
    "trait": ["trait", "phenotype", "character", "morpholog"],
    "disease": ["disease", "pathogen", "resistance", "susceptib", "infection"],
    "pathway": ["pathway", "metabol", "biosyn", "enzyme", "catalyz"],
    "breeding": ["breed", "cross", "hybrid", "selection", "parent"],
    "experiment": ["experiment", "design", "protocol", "method", "assay"],
    "literature": ["paper", "study", "research", "publication", "review"],
}


def classify_query(state: AgentState) -> dict:
    """Classify the user query into a category."""
    query_lower = state["user_query"].lower()
    detected_types = []

    for qtype, keywords in QUERY_TYPES.items():
        if any(kw in query_lower for kw in keywords):
            detected_types.append(qtype)

    query_type = detected_types[0] if detected_types else "general"

    return {"query_type": query_type, "current_step": "classified"}


def create_plan(state: AgentState) -> dict:
    """Create an execution plan based on query type."""
    query_type = state["query_type"]
    plans = {
        "gene": [
            "search_literature_for_gene",
            "search_protein_database",
            "gather_gene_function_info",
            "identify_related_pathways",
            "synthesize_response",
        ],
        "trait": [
            "search_trait_literature",
            "find_genetic_associations",
            "identify_candidate_genes",
            "evaluate_evidence",
            "synthesize_response",
        ],
        "disease": [
            "search_disease_literature",
            "find_resistance_genes",
            "identify_mechanisms",
            "gather_management_info",
            "synthesize_response",
        ],
        "pathway": [
            "search_pathway_literature",
            "map_pathway_components",
            "identify_regulators",
            "gather_expression_data",
            "synthesize_response",
        ],
        "breeding": [
            "search_breeding_literature",
            "identify_selection_methods",
            "gather_population_info",
            "evaluate_strategies",
            "synthesize_response",
        ],
        "experiment": [
            "search_methodology_literature",
            "identify_appropriate_designs",
            "gather_statistical_requirements",
            "outline_protocols",
            "synthesize_response",
        ],
        "literature": [
            "search_relevant_papers",
            "retrieve_abstracts",
            "analyze_findings",
            "identify_gaps",
            "synthesize_response",
        ],
        "general": [
            "search_broad_literature",
            "gather_key_information",
            "evaluate_evidence",
            "synthesize_response",
        ],
    }

    plan = plans.get(query_type, plans["general"])
    return {"plan": plan, "current_step": "planned"}


async def execute_plan(state: AgentState) -> dict:
    """Execute the research plan by gathering evidence."""
    evidence = []
    query = state["user_query"]

    try:
        # Search PubMed
        papers = await search_pubmed(query, max_results=5)
        if papers:
            evidence.append({
                "source": "pubmed",
                "type": "literature",
                "data": papers[:3],
                "count": len(papers),
            })

        # If gene-related, also search UniProt and NCBI Gene
        if state["query_type"] == "gene":
            proteins = await search_uniprot(query, max_results=3)
            if proteins:
                evidence.append({
                    "source": "uniprot",
                    "type": "protein",
                    "data": proteins,
                })

    except Exception as e:
        logger.error("evidence_gathering_failed", error=str(e))
        evidence.append({"source": "error", "type": "error", "data": str(e)})

    return {"gathered_evidence": evidence, "current_step": "executed"}


async def synthesize_results(state: AgentState) -> dict:
    """Synthesize gathered evidence into a comprehensive response."""
    llm = get_llm()

    evidence_str = ""
    for ev in state.get("gathered_evidence", []):
        if ev["type"] == "literature":
            evidence_str += "\nRelevant papers:\n"
            for p in ev.get("data", []):
                evidence_str += f"- PMID:{p.get('pmid', 'N/A')} | {p.get('title', '')} | {p.get('journal', '')} ({p.get('year', '')})\n"
        elif ev["type"] == "protein":
            evidence_str += "\nProtein information:\n"
            for pr in ev.get("data", []):
                evidence_str += f"- {pr.get('accession', '')} | {pr.get('name', '')} | {pr.get('organism', '')}\n"

    prompt = f"""Based on the following evidence, provide a comprehensive response to: {state['user_query']}

Query type: {state['query_type']}
Evidence gathered: {evidence_str}

Provide:
1. Direct answer to the question
2. Supporting evidence from literature
3. Confidence assessment
4. Limitations and uncertainties
5. Recommended follow-up actions
6. Key references (PMIDs)

Be scientifically rigorous. Clearly distinguish established facts from hypotheses.
Follow the AI_BEHAVIOUR.md guidelines."""

    messages = [
        SystemMessage(content="You are PIP Research Assistant. Provide evidence-based scientific responses."),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)

        sources = []
        for ev in state.get("gathered_evidence", []):
            if ev["type"] == "literature":
                for p in ev.get("data", []):
                    sources.append({
                        "pmid": p.get("pmid"),
                        "title": p.get("title"),
                        "url": p.get("url"),
                    })

        return {
            "response": response.content,
            "sources": sources,
            "confidence": "medium" if sources else "low",
            "current_step": "synthesized",
        }
    except Exception as e:
        logger.error("synthesis_failed", error=str(e))
        return {
            "response": "Unable to synthesize results at this time.",
            "sources": [],
            "confidence": "unknown",
            "current_step": "synthesis_failed",
        }


def build_research_workflow():
    """Build and compile the research workflow graph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("classify", classify_query)
    workflow.add_node("plan", create_plan)
    workflow.add_node("execute", execute_plan)
    workflow.add_node("synthesize", synthesize_results)

    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "plan")
    workflow.add_edge("plan", "execute")
    workflow.add_edge("execute", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()


# Compiled workflow instance
research_workflow = build_research_workflow()


async def run_research_workflow(query: str) -> dict:
    """Run the research workflow on a user query."""
    initial_state = {
        "user_query": query,
        "query_type": "",
        "context": [],
        "plan": [],
        "gathered_evidence": [],
        "current_step": "start",
        "response": "",
        "confidence": "",
        "sources": [],
    }

    try:
        result = await research_workflow.ainvoke(initial_state)
        return {
            "response": result.get("response", ""),
            "query_type": result.get("query_type", ""),
            "confidence": result.get("confidence", ""),
            "sources": result.get("sources", []),
        }
    except Exception as e:
        logger.error("workflow_failed", error=str(e))
        return {
            "response": "Research workflow encountered an error. Please try again.",
            "query_type": "error",
            "confidence": "unknown",
            "sources": [],
        }
