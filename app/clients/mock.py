from app.clients.base import LLMClient


class MockLLMClient(LLMClient):
    async def summarize(self, prompt: str) -> str:
        return f"Mock summary for prompt: {prompt}"
