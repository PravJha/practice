from abc import ABC, abstractmethod

from app.core.config import settings


class LLMClient(ABC):
    @abstractmethod
    def summarize(self, prompt: str) -> str:
        raise NotImplementedError


class MockLLMClient(LLMClient):
    def summarize(self, prompt: str) -> str:
        return f"Mock summary for prompt: {prompt}"


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def summarize(self, prompt: str) -> str:
        raise NotImplementedError("OpenAIClient is a stub. Replace with a real implementation.")


def get_llm_client() -> LLMClient:
    if settings.llm_provider == "openai":
        raise RuntimeError("OpenAI provider is not configured in this scaffold.")
    return MockLLMClient()
