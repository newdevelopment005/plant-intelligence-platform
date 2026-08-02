from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class GraphQueryRequest(BaseModel):
    query: str
    entity_type: str | None = None
    max_depth: int = 2


@router.post("/query")
async def query_knowledge_graph(request: GraphQueryRequest):
    return {"message": "Knowledge agent - query graph", "query": request.query}


@router.post("/explore")
async def explore_entity():
    return {"message": "Knowledge agent - explore entity"}


@router.post("/infer")
async def infer_relationships():
    return {"message": "Knowledge agent - infer relationships"}
