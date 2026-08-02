import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm, get_llm_mini
from app.tools.external_tools import search_pubmed, get_pubmed_abstract

logger = structlog.get_logger()

LITERATURE_SYSTEM_PROMPT = """You are PIP Literature Assistant, an expert in plant science literature analysis.

Rules:
- Summarize papers accurately without adding information not present in the text
- Always distinguish between the authors' conclusions and your interpretation
- Identify key findings, methodologies, and limitations
- Note sample sizes and statistical methods used
- Highlight contradictions between studies
- Never fabricate citations or references
- When summarizing, provide a balanced view of the evidence"""


async def summarize_literature(
    query: str,
    max_papers: int = 5,
    focus_areas: list[str] | None = None,
) -> dict:
    """Search and summarize literature on a given topic."""
    llm = get_llm()

    papers = await search_pubmed(query, max_results=max_papers)
    if not papers:
        return {
            "summary": "No papers found for this query. Try different keywords or check spelling.",
            "papers": [],
            "query": query,
        }

    abstracts = []
    for paper in papers[:max_papers]:
        abstract = await get_pubmed_abstract(particle["pmid"])
        if abstract:
            abstracts.append(f"PMID {paper['pmid']}: {abstract[:1500]}")

    focus_str = ""
    if focus_areas:
        focus_str = f"\nFocus areas: {', '.join(focus_areas)}"

    prompt = f"""Summarize the following scientific papers on: {query}{focus_str}

Papers:
{chr(10).join(abstracts)}

Provide:
1. Executive summary (2-3 sentences)
2. Key findings across studies
3. Methodologies used
4. Areas of agreement
5. Areas of disagreement/uncertainty
6. Knowledge gaps identified
7. Recommended next steps for research

Be concise but thorough. Cite papers by PMID."""

    messages = [
        SystemMessage(content=LITERATURE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "summary": response.content,
            "papers": papers,
            "query": query,
            "paper_count": len(papers),
        }
    except Exception as e:
        logger.error("literature_summary_failed", error=str(e))
        return {
            "summary": "Unable to generate summary at this time.",
            "papers": papers,
            "query": query,
        }


async def search_literature_semantic(
    query: str,
    max_results: int = 10,
) -> dict:
    """Search literature with semantic understanding."""
    papers = await search_pubmed(query, max_results=max_results)

    if not papers:
        return {
            "results": [],
            "query": query,
            "message": "No results found.",
        }

    llm = get_llm_mini()

    paper_summaries = []
    for p in papers[:5]:
        abstract = await get_pubmed_abstract(p["pmid"])
        paper_summaries.append({
            "pmid": p["pmid"],
            "title": p["title"],
            "journal": p["journal"],
            "year": p["year"],
            "relevance": "high" if any(
                kw.lower() in p["title"].lower()
                for kw in query.split()
            ) else "medium",
        })

    return {
        "results": paper_summaries,
        "query": query,
        "total_found": len(papers),
    }


async def extract_findings(paper_text: str) -> dict:
    """Extract key findings from a paper's text."""
    llm = get_llm()

    prompt = f"""Extract key findings from the following scientific text:

{paper_text[:3000]}

Provide:
1. Main hypothesis
2. Key experimental results
3. Statistical significance (if reported)
4. Species studied
5. Genes/proteins mentioned
6. Conclusions
7. Limitations acknowledged by authors
8. Suggested future work

Format as structured JSON."""

    messages = [
        SystemMessage(content=LITERATURE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "extracted_findings": response.content,
            "text_length": len(paper_text),
        }
    except Exception as e:
        logger.error("finding_extraction_failed", error=str(e))
        return {"error": "Unable to extract findings."}
