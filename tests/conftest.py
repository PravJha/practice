import pytest
from fastapi.testclient import TestClient

from app.clients.mock import MockLLMClient
from app.main import app
from app.services.summarization import SummarizationService, get_summarization_service


@pytest.fixture(scope="session")
def mock_llm_client() -> MockLLMClient:
    return MockLLMClient()


@pytest.fixture(scope="session")
def client(mock_llm_client: MockLLMClient) -> TestClient:
    def _override() -> SummarizationService:
        return SummarizationService(mock_llm_client)

    app.dependency_overrides[get_summarization_service] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
