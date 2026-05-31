from abc import ABC, abstractmethod

from app.core.config import settings


class LLMClient(ABC):
    @abstractmethod
    async def summarize(self, prompt: str) -> str:
        raise NotImplementedError


def get_llm_client() -> LLMClient:
    if settings.llm_provider == "openai":
        from app.clients.openai import OpenAIClient
        return OpenAIClient(api_key=settings.openai_api_key)
    if settings.llm_provider == "gemini":
        from app.clients.gemini import GeminiClient
        return GeminiClient(api_key=settings.gemini_api_key)
    from app.clients.mock import MockLLMClient
    return MockLLMClient()
