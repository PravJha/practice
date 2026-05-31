import pytest
from unittest.mock import AsyncMock, patch

from app.clients.base import LLMClient
from app.core.exceptions import LLMUnavailableError
from app.services.summarization import SummarizationService


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=LLMClient)


@pytest.fixture
def service(mock_client: AsyncMock) -> SummarizationService:
    return SummarizationService(llm_client=mock_client)


@pytest.mark.asyncio
async def test_summarize_happy_path(service: SummarizationService, mock_client: AsyncMock):
    mock_client.summarize.return_value = "A great summary."
    result = await service.summarize("Some text")
    assert result == "A great summary."
    mock_client.summarize.assert_awaited_once_with("Some text")


@pytest.mark.asyncio
async def test_summarize_retries_on_unavailable(service: SummarizationService, mock_client: AsyncMock):
    # Fails twice, succeeds on third attempt
    mock_client.summarize.side_effect = [
        LLMUnavailableError("down"),
        LLMUnavailableError("down"),
        "Recovered summary",
    ]

    with patch("app.services.summarization.settings") as mock_settings:
        mock_settings.retry_max_attempts = 3
        mock_settings.retry_min_wait_seconds = 0
        mock_settings.retry_max_wait_seconds = 0
        mock_settings.llm_provider = "mock"
        result = await service.summarize("Some text")

    assert result == "Recovered summary"
    assert mock_client.summarize.await_count == 3


@pytest.mark.asyncio
async def test_summarize_raises_after_exhausted_retries(service: SummarizationService, mock_client: AsyncMock):
    mock_client.summarize.side_effect = LLMUnavailableError("permanently down")

    with patch("app.services.summarization.settings") as mock_settings:
        mock_settings.retry_max_attempts = 2
        mock_settings.retry_min_wait_seconds = 0
        mock_settings.retry_max_wait_seconds = 0
        mock_settings.llm_provider = "mock"

        with pytest.raises(LLMUnavailableError):
            await service.summarize("Some text")

    assert mock_client.summarize.await_count == 2
