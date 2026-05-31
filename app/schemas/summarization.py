from pydantic import BaseModel


class SummarizationRequest(BaseModel):
    prompt: str


class SummarizationResponse(BaseModel):
    summary: str
