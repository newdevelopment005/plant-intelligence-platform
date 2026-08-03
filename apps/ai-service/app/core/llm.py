import structlog
from langchain_openai import ChatOpenAI

from app.config import settings

logger = structlog.get_logger()


def get_llm(model: str | None = None) -> ChatOpenAI:
    return ChatOpenAI(
        model=model or settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0.1,
    )


def get_llm_mini() -> ChatOpenAI:
    return get_llm(settings.OPENAI_MINI_MODEL)
