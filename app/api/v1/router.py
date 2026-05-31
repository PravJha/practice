from fastapi import APIRouter, Depends

from app.core.llm_client import LLMClient, get_llm_client
from app.schemas.summarization import SummarizationRequest, SummarizationResponse

router = APIRouter(tags=["summarization"])


@router.post("/v1/summarize", response_model=SummarizationResponse)
async def summarize(
    request: SummarizationRequest,
    llm_client: LLMClient = Depends(get_llm_client),
):
    summary = llm_client.summarize(request.prompt)
    return SummarizationResponse(summary=summary)
