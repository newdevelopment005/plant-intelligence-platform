from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.research_agent import (
    chat_with_research_agent,
    recommend_genes,
    design_experiment,
)
from app.agents.literature_agent import (
    summarize_literature,
    search_literature_semantic,
    extract_findings,
)
from app.agents.image_agent import (
    analyze_plant_image,
    classify_plant_disease,
    measure_phenotype,
    compare_images,
)
from app.agents.knowledge_agent import (
    query_knowledge_graph,
    explore_entity,
    infer_relationships,
)
from app.workflows.research_workflow import run_research_workflow

router = APIRouter()


# =============================================
# Research Chat
# =============================================
class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    context: dict | None = None
    conversation_history: list[dict] | None = None


@router.post("/")
async def chat(request: ChatRequest):
    result = await chat_with_research_agent(
        message=request.message,
        conversation_history=request.conversation_history,
        context=request.context,
    )
    return {
        "response": result["response"],
        "conversation_id": request.conversation_id or "new",
        "tools_used": result.get("tools_used", []),
        "sources": [],
    }


class GeneRecommendRequest(BaseModel):
    trait: str
    species: str = "wheat"
    context: dict | None = None


@router.post("/recommend-genes")
async def recommend_genes_endpoint(request: GeneRecommendRequest):
    return await recommend_genes(
        trait=request.trait,
        species=request.species,
        context=request.context,
    )


class ExperimentDesignRequest(BaseModel):
    objective: str
    species: str = "wheat"
    constraints: dict | None = None


@router.post("/design-experiment")
async def design_experiment_endpoint(request: ExperimentDesignRequest):
    return await design_experiment(
        objective=request.objective,
        species=request.species,
        constraints=request.constraints,
    )


@router.post("/analyze-image")
async def analyze_image_endpoint(request: dict):
    from app.agents.image_agent import analyze_plant_image
    return await analyze_plant_image(
        image_url=request.get("image_url", ""),
        analysis_type=request.get("analysis_type", "comprehensive"),
        species=request.get("species"),
    )


# =============================================
# Research Workflow
# =============================================
class WorkflowRequest(BaseModel):
    query: str


@router.post("/workflow")
async def run_workflow(request: WorkflowRequest):
    return await run_research_workflow(request.query)


# =============================================
# Literature AI
# =============================================
class LiteratureSummarizeRequest(BaseModel):
    query: str
    max_papers: int = 5
    focus_areas: list[str] | None = None


@router.post("/literature/summarize")
async def summarize_literature_endpoint(request: LiteratureSummarizeRequest):
    return await summarize_literature(
        query=request.query,
        max_papers=request.max_papers,
        focus_areas=request.focus_areas,
    )


class LiteratureSearchRequest(BaseModel):
    query: str
    max_results: int = 10


@router.post("/literature/search")
async def search_literature_endpoint(request: LiteratureSearchRequest):
    return await search_literature_semantic(
        query=request.query,
        max_results=request.max_results,
    )


class ExtractFindingsRequest(BaseModel):
    text: str


@router.post("/literature/extract")
async def extract_findings_endpoint(request: ExtractFindingsRequest):
    return await extract_findings(request.text)


# =============================================
# Image Analysis AI
# =============================================
class ImageAnalyzeRequest(BaseModel):
    image_url: str
    analysis_type: str = "comprehensive"
    species: str | None = None


@router.post("/images/analyze")
async def analyze_image_ai(request: ImageAnalyzeRequest):
    return await analyze_plant_image(
        image_url=request.image_url,
        analysis_type=request.analysis_type,
        species=request.species,
    )


class DiseaseClassifyRequest(BaseModel):
    image_url: str
    species: str | None = None


@router.post("/images/classify-disease")
async def classify_disease(request: DiseaseClassifyRequest):
    return await classify_plant_disease(
        image_url=request.image_url,
        species=request.species,
    )


class PhenotypeMeasureRequest(BaseModel):
    image_url: str
    measurements: list[str] | None = None
    scale_reference: str | None = None


@router.post("/images/measure")
async def measure_phenotype_endpoint(request: PhenotypeMeasureRequest):
    return await measure_phenotype(
        image_url=request.image_url,
        measurements=request.measurements,
        scale_reference=request.scale_reference,
    )


class ImageCompareRequest(BaseModel):
    image_urls: list[str]
    comparison_focus: str = "morphological"


@router.post("/images/compare")
async def compare_images_endpoint(request: ImageCompareRequest):
    return await compare_images(
        image_urls=request.image_urls,
        comparison_focus=request.comparison_focus,
    )


# =============================================
# Knowledge Graph AI
# =============================================
class KGQueryRequest(BaseModel):
    query: str
    entity_type: str | None = None
    max_depth: int = 2


@router.post("/knowledge-graph/query")
async def query_kg(request: KGQueryRequest):
    return await query_knowledge_graph(
        query=request.query,
        entity_type=request.entity_type,
        max_depth=request.max_depth,
    )


class KGExploreRequest(BaseModel):
    entity_name: str
    entity_type: str = "gene"
    depth: int = 2


@router.post("/knowledge-graph/explore")
async def explore_kg_entity(request: KGExploreRequest):
    return await explore_entity(
        entity_name=request.entity_name,
        entity_type=request.entity_type,
        depth=request.depth,
    )


class KGInferRequest(BaseModel):
    entity_a: str
    entity_b: str
    context: str | None = None


@router.post("/knowledge-graph/infer")
async def infer_kg_relationships(request: KGInferRequest):
    return await infer_relationships(
        entity_a=request.entity_a,
        entity_b=request.entity_b,
        context=request.context,
    )
