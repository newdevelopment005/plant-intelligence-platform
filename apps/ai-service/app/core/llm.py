import structlog
from langchain_openai import ChatOpenAI

from app.config import settings

logger = structlog.get_logger()


def get_llm(model: str | None = None) -> ChatOpenAI:
    if settings.USE_LOCAL_LLM:
        return ChatOpenAI(
            model=model or settings.OLLAMA_MODEL,
            api_key="ollama",
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.1,
        )
    return ChatOpenAI(
        model=model or settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0.1,
    )


def get_llm_mini() -> ChatOpenAI:
    if settings.USE_LOCAL_LLM:
        return get_llm(settings.OLLAMA_MINI_MODEL)
    return get_llm(settings.OPENAI_MINI_MODEL)
