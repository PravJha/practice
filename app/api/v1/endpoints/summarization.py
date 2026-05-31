import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions import LLMError
from app.schemas.summarization import SummarizationRequest, SummarizationResponse
from app.services.summarization import SummarizationService, get_summarization_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["summarization"])


@router.post("/summarize", response_model=SummarizationResponse)
async def summarize(
    request: SummarizationRequest,
    service: SummarizationService = Depends(get_summarization_service),
) -> SummarizationResponse:
    try:
        summary = await service.summarize(request.prompt)
        return SummarizationResponse(summary=summary)
    except LLMError as exc:
        logger.error("LLM service error: %s", exc)
        raise HTTPException(status_code=503, detail="LLM service unavailable") from exc
