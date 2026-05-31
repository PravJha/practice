from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_summarize_endpoint_returns_mock_summary():
    response = client.post("/api/v1/summarize", json={"prompt": "Hello world"})

    assert response.status_code == 200
    assert response.json() == {"summary": "Mock summary for prompt: Hello world"}
