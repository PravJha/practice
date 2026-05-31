from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_pii_scrubber_replaces_ssn_and_email():
    response = client.post(
        "/api/v1/summarize",
        json={"prompt": "Contact jane.doe@example.com and SSN 123-45-6789 for details."},
    )

    assert response.status_code == 200
    body = response.json()
    assert "[REDACTED_EMAIL]" in body["summary"]
    assert "[REDACTED_SSN]" in body["summary"]
    assert "jane.doe@example.com" not in body["summary"]
    assert "123-45-6789" not in body["summary"]
