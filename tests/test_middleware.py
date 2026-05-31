import logging

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _summarize(client: TestClient, prompt: str) -> dict:
    return client.post("/api/v1/summarize", json={"prompt": prompt}).json()


# ---------------------------------------------------------------------------
# Core PII types
# ---------------------------------------------------------------------------

def test_ssn_is_redacted(client: TestClient):
    body = _summarize(client, "SSN is 123-45-6789")
    assert "[REDACTED_SSN]" in body["summary"]
    assert "123-45-6789" not in body["summary"]


def test_email_is_redacted(client: TestClient):
    body = _summarize(client, "Contact jane.doe@example.com for info.")
    assert "[REDACTED_EMAIL]" in body["summary"]
    assert "jane.doe@example.com" not in body["summary"]


def test_phone_is_redacted(client: TestClient):
    for phone in ["555-867-5309", "(555) 867-5309", "+1 555-867-5309"]:
        body = _summarize(client, f"Call me at {phone}.")
        assert "[REDACTED_PHONE]" in body["summary"], f"Phone not redacted: {phone}"
        assert phone not in body["summary"]


def test_credit_card_is_redacted(client: TestClient):
    for cc in ["4111 1111 1111 1111", "4111-1111-1111-1111", "4111111111111111"]:
        body = _summarize(client, f"Card: {cc}")
        assert "[REDACTED_CREDIT_CARD]" in body["summary"], f"CC not redacted: {cc}"
        assert cc not in body["summary"]


def test_ip_address_is_redacted(client: TestClient):
    body = _summarize(client, "Server is at 192.168.1.100")
    assert "[REDACTED_IP_ADDRESS]" in body["summary"]
    assert "192.168.1.100" not in body["summary"]


def test_date_of_birth_is_redacted(client: TestClient):
    for dob in ["01/15/1990", "1-5-2001"]:
        body = _summarize(client, f"Born on {dob}")
        assert "[REDACTED_DATE_OF_BIRTH]" in body["summary"], f"DOB not redacted: {dob}"
        assert dob not in body["summary"]


# ---------------------------------------------------------------------------
# Multiple PII types in one request
# ---------------------------------------------------------------------------

def test_multiple_pii_types_in_one_request(client: TestClient):
    prompt = (
        "Contact jane.doe@example.com, SSN 123-45-6789, "
        "card 4111 1111 1111 1111, phone 555-867-5309."
    )
    body = _summarize(client, prompt)
    summary = body["summary"]
    assert "[REDACTED_EMAIL]" in summary
    assert "[REDACTED_SSN]" in summary
    assert "[REDACTED_CREDIT_CARD]" in summary
    assert "[REDACTED_PHONE]" in summary
    assert "jane.doe@example.com" not in summary
    assert "123-45-6789" not in summary
    assert "4111 1111 1111 1111" not in summary
    assert "555-867-5309" not in summary


# ---------------------------------------------------------------------------
# Nested JSON scrubbing
# ---------------------------------------------------------------------------

def test_nested_json_is_fully_scrubbed(client: TestClient):
    """Middleware must walk the whole payload tree, not just top-level strings."""
    from app.core.middleware import _scrub_value

    payload = {
        "level1": {
            "email": "user@corp.com",
            "level2": {
                "items": ["call 555-123-4567", "ssn: 111-22-3333"],
                "cc": "4111 1111 1111 1111",
            },
        }
    }
    scrubbed, counts = _scrub_value(payload)
    assert counts["EMAIL"] == 1
    assert counts["PHONE"] == 1
    assert counts["SSN"] == 1
    assert counts["CREDIT_CARD"] == 1
    assert "user@corp.com" not in str(scrubbed)
    assert "555-123-4567" not in str(scrubbed)
    assert "111-22-3333" not in str(scrubbed)
    assert "4111 1111 1111 1111" not in str(scrubbed)


def test_list_of_prompts_scrubbed(client: TestClient):
    from app.core.middleware import _scrub_value

    payload = ["email me at a@b.com", "my ssn is 999-88-7777", "no pii here"]
    scrubbed, counts = _scrub_value(payload)
    assert counts["EMAIL"] == 1
    assert counts["SSN"] == 1
    assert "a@b.com" not in str(scrubbed)
    assert "999-88-7777" not in str(scrubbed)
    assert "no pii here" in str(scrubbed)


# ---------------------------------------------------------------------------
# Clean request passes through unchanged
# ---------------------------------------------------------------------------

def test_no_pii_passes_through_unchanged(client: TestClient):
    response = client.post("/api/v1/summarize", json={"prompt": "No PII here."})
    assert response.status_code == 200
    assert "No PII here." in response.json()["summary"]


# ---------------------------------------------------------------------------
# GET request (no body) passes through — middleware must not crash
# ---------------------------------------------------------------------------

def test_get_request_is_not_blocked(client: TestClient):
    response = client.get("/api/v1/summarize")
    assert response.status_code == 405  # route not defined for GET, not a 500


# ---------------------------------------------------------------------------
# Log safety — raw PII must never appear in log output
# ---------------------------------------------------------------------------

def test_logs_contain_no_raw_pii(client: TestClient, caplog):
    pii_prompt = "SSN 123-45-6789, email spy@evil.com, card 4111 1111 1111 1111"
    with caplog.at_level(logging.DEBUG):
        client.post("/api/v1/summarize", json={"prompt": pii_prompt})

    full_log = caplog.text
    assert "123-45-6789" not in full_log, "SSN leaked into logs"
    assert "spy@evil.com" not in full_log, "Email leaked into logs"
    assert "4111 1111 1111 1111" not in full_log, "Credit card leaked into logs"


# ---------------------------------------------------------------------------
# Response scrubbing (defence-in-depth)
# ---------------------------------------------------------------------------

def test_response_body_is_scrubbed(client: TestClient):
    """Even if PII somehow appears in the LLM response it must be redacted."""
    from unittest.mock import AsyncMock, patch
    from app.clients.mock import MockLLMClient

    async def leaky_summarize(self, prompt: str) -> str:
        return "Here is PII: ssn=123-45-6789 email=leak@corp.com"

    with patch.object(MockLLMClient, "summarize", new=leaky_summarize):
        response = client.post("/api/v1/summarize", json={"prompt": "anything"})

    assert response.status_code == 200
    body = response.json()["summary"]
    assert "123-45-6789" not in body
    assert "leak@corp.com" not in body
    assert "[REDACTED_SSN]" in body
    assert "[REDACTED_EMAIL]" in body
