import logging

from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.clients.base import LLMClient, get_llm_client
from app.core.config import settings
from app.core.exceptions import LLMUnavailableError

logger = logging.getLogger(__name__)


class SummarizationService:
    def __init__(self, llm_client: LLMClient) -> None:
        self._client = llm_client

    async def summarize(self, prompt: str) -> str:
        _call = retry(
            stop=stop_after_attempt(settings.retry_max_attempts),
            wait=wait_exponential(
                min=settings.retry_min_wait_seconds,
                max=settings.retry_max_wait_seconds,
            ),
            retry=retry_if_exception_type(LLMUnavailableError),
            reraise=True,
        )(self._call_llm)
        try:
            return await _call(prompt)
        except RetryError as exc:
            raise LLMUnavailableError("LLM unavailable after retries") from exc

    async def _call_llm(self, prompt: str) -> str:
        logger.info("Calling LLM client (provider=%s)", settings.llm_provider)
        try:
            return await self._client.summarize(prompt)
        except LLMUnavailableError:
            logger.warning("LLM unavailable, retrying...")
            raise


def get_summarization_service() -> SummarizationService:
    return SummarizationService(get_llm_client())
