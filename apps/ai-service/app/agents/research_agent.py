from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    context: dict | None = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: list[dict] = []


@router.post("/")
async def chat(request: ChatRequest):
    return {
        "response": "Research assistant - chat",
        "conversation_id": request.conversation_id or "new",
        "sources": [],
    }


@router.post("/analyze-image")
async def analyze_image():
    return {"message": "Research assistant - analyze image"}


@router.post("/recommend-genes")
async def recommend_genes():
    return {"message": "Research assistant - recommend genes"}


@router.post("/design-experiment")
async def design_experiment():
    return {"message": "Research assistant - design experiment"}
