import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.clients.mock import MockLLMClient
from app.core.exceptions import LLMUnavailableError


@pytest.mark.asyncio
async def test_mock_client_returns_summary():
    client = MockLLMClient()
    result = await client.summarize("Hello world")
    assert result == "Mock summary for prompt: Hello world"


@pytest.mark.asyncio
async def test_gemini_client_raises_llm_unavailable_on_error():
    with patch("app.clients.gemini.genai.Client") as mock_client_cls:
        mock_aio = MagicMock()
        mock_aio.models.generate_content = AsyncMock(side_effect=RuntimeError("network error"))
        mock_client_cls.return_value.aio = mock_aio

        from app.clients.gemini import GeminiClient
        client = GeminiClient(api_key="fake-key")

        with pytest.raises(LLMUnavailableError):
            await client.summarize("test prompt")
