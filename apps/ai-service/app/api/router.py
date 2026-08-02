from fastapi import APIRouter

from app.agents.literature_agent import router as literature_agent_router
from app.agents.research_agent import router as research_agent_router
from app.agents.image_agent import router as image_agent_router
from app.agents.knowledge_agent import router as knowledge_agent_router

router = APIRouter()

router.include_router(literature_agent_router, prefix="/literature", tags=["Literature AI"])
router.include_router(research_agent_router, prefix="/chat", tags=["Research Assistant"])
router.include_router(image_agent_router, prefix="/images", tags=["Image Analysis"])
router.include_router(knowledge_agent_router, prefix="/knowledge-graph", tags=["Knowledge Graph AI"])
