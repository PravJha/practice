import logging

from openai import AsyncOpenAI

from app.clients.base import LLMClient
from app.core.exceptions import LLMUnavailableError

logger = logging.getLogger(__name__)


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)

    async def summarize(self, prompt: str) -> str:
        logger.info("Sending summarize request to OpenAI")
        try:
            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Summarize the following text concisely."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("OpenAI call failed: %s", exc)
            raise LLMUnavailableError("OpenAI request failed") from exc
