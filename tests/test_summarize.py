import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.core.exceptions import LLMUnavailableError
from app.main import app
from app.services.summarization import SummarizationService, get_summarization_service


def test_summarize_endpoint_returns_mock_summary(client: TestClient):
    response = client.post("/api/v1/summarize", json={"prompt": "Hello world"})

    assert response.status_code == 200
    assert response.json() == {"summary": "Mock summary for prompt: Hello world"}


def test_summarize_endpoint_returns_503_on_llm_error():
    failing_mock = AsyncMock(spec=SummarizationService)
    failing_mock.summarize.side_effect = LLMUnavailableError("down")

    def _override() -> SummarizationService:
        return failing_mock

    app.dependency_overrides[get_summarization_service] = _override
    try:
        with TestClient(app) as c:
            response = c.post("/api/v1/summarize", json={"prompt": "test"})
        assert response.status_code == 503
        assert response.json()["detail"] == "LLM service unavailable"
    finally:
        app.dependency_overrides.clear()
