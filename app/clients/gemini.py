import logging

from google import genai

from app.clients.base import LLMClient
from app.core.exceptions import LLMUnavailableError

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"


class GeminiClient(LLMClient):
    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    async def summarize(self, prompt: str) -> str:
        logger.info("Sending summarize request to Gemini (model=%s)", GEMINI_MODEL)
        try:
            response = await self._client.aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            return response.text
        except Exception as exc:
            logger.error("Gemini call failed: %s", exc)
            raise LLMUnavailableError("Gemini request failed") from exc
