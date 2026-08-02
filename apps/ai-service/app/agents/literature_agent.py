from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LiteratureRequest(BaseModel):
    query: str
    max_results: int = 10


class LiteratureResponse(BaseModel):
    summary: str
    papers: list[dict]


@router.post("/summarize")
async def summarize_literature(request: LiteratureRequest):
    return {"message": "Literature agent - summarize", "query": request.query}


@router.post("/search")
async def search_literature(request: LiteratureRequest):
    return {"message": "Literature agent - search", "query": request.query}


@router.post("/extract")
async def extract_findings():
    return {"message": "Literature agent - extract findings"}
