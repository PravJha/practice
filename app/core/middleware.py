import json
import logging
import re
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PII pattern registry — order matters: more-specific patterns first so a
# credit-card number is not partially matched by the phone pattern, etc.
# ---------------------------------------------------------------------------
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # SSN  123-45-6789
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    # Credit card  4111 1111 1111 1111 / 4111-1111-1111-1111 / 4111111111111111
    ("CREDIT_CARD", re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")),
    # Email
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    # US phone  (555) 867-5309 / 555-867-5309 / +1 555 867 5309
    ("PHONE", re.compile(
        r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"
    )),
    # IPv4 address  192.168.1.1
    ("IP_ADDRESS", re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    )),
    # Date of birth  MM/DD/YYYY or MM-DD-YYYY
    ("DATE_OF_BIRTH", re.compile(
        r"\b(?:0?[1-9]|1[0-2])[/\-](?:0?[1-9]|[12]\d|3[01])[/\-](?:19|20)\d{2}\b"
    )),
    # US passport  letter + 8 digits  e.g. A12345678
    ("PASSPORT", re.compile(r"\b[A-Z]\d{8}\b")),
    # IBAN  up to 34 alphanumeric chars starting with two letters + two digits
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b")),
]


class PiiScrubberMiddleware(BaseHTTPMiddleware):
    """Scrubs PII from every inbound JSON request body and every outbound JSON
    response body.  Logs only redaction *counts* — raw PII values are never
    written to any log entry."""

    async def dispatch(self, request: Request, call_next):
        request = await self._scrub_request(request)
        response = await call_next(request)
        response = await self._scrub_response(response, request.url.path)
        return response

    # ------------------------------------------------------------------
    # Request scrubbing
    # ------------------------------------------------------------------

    async def _scrub_request(self, request: Request) -> Request:
        if request.method not in ("POST", "PUT", "PATCH"):
            return request
        if not request.headers.get("content-type", "").startswith("application/json"):
            return request

        body_bytes = await request.body()
        if not body_bytes:
            return request

        try:
            payload = json.loads(body_bytes)
        except json.JSONDecodeError:
            logger.warning(
                "Non-JSON body on %s %s — PII scrub skipped",
                request.method,
                request.url.path,
            )
            return request

        scrubbed_payload, counts = _scrub_value(payload)

        if any(counts.values()):
            # SAFE: only counts and path are logged, never raw PII
            logger.info(
                "PII redacted from request [%s %s]: %s",
                request.method,
                request.url.path,
                {k: v for k, v in counts.items() if v},
            )

        scrubbed_body = json.dumps(scrubbed_payload).encode("utf-8")

        async def receive() -> Message:
            return {"type": "http.request", "body": scrubbed_body, "more_body": False}

        request._receive = receive  # type: ignore[attr-defined]
        request._body = scrubbed_body  # type: ignore[attr-defined]
        return request

    # ------------------------------------------------------------------
    # Response scrubbing  (defence-in-depth: catches any PII the LLM
    # may have reconstructed or hallucinated in its reply)
    # ------------------------------------------------------------------

    async def _scrub_response(self, response: Response, path: str) -> Response:
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")

        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type,
            )

        scrubbed_payload, counts = _scrub_value(payload)

        if any(counts.values()):
            # Warn — PII in the LLM response is unexpected since the request
            # was already scrubbed; log counts only, never the raw values.
            logger.warning(
                "PII found in LLM response [%s] and redacted: %s",
                path,
                {k: v for k, v in counts.items() if v},
            )

        scrubbed_body = json.dumps(scrubbed_payload).encode("utf-8")
        headers = dict(response.headers)
        headers["content-length"] = str(len(scrubbed_body))
        return Response(
            content=scrubbed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=content_type,
        )


# ---------------------------------------------------------------------------
# Pure-function helpers (no class state — easy to unit-test independently)
# ---------------------------------------------------------------------------

def _scrub_value(obj: Any) -> tuple[Any, dict[str, int]]:
    counts: dict[str, int] = {label: 0 for label, _ in _PATTERNS}
    result = _scrub_recursive(obj, counts)
    return result, counts


def _scrub_recursive(obj: Any, counts: dict[str, int]) -> Any:
    if isinstance(obj, str):
        return _scrub_text(obj, counts)
    if isinstance(obj, dict):
        return {k: _scrub_recursive(v, counts) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_scrub_recursive(item, counts) for item in obj]
    return obj


def _scrub_text(text: str, counts: dict[str, int]) -> str:
    for label, pattern in _PATTERNS:
        text, n = pattern.subn(f"[REDACTED_{label}]", text)
        counts[label] += n
    return text
