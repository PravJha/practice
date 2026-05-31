import json
import re
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message


class PiiScrubberMiddleware(BaseHTTPMiddleware):
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.headers.get("content-type", "").startswith("application/json"):
            body_bytes = await request.body()
            if body_bytes:
                try:
                    payload = json.loads(body_bytes)
                except json.JSONDecodeError:
                    return await call_next(request)

                scrubbed_payload = self._scrub_payload(payload)
                scrubbed_body = json.dumps(scrubbed_payload).encode("utf-8")

                async def receive() -> Message:
                    return {"type": "http.request", "body": scrubbed_body, "more_body": False}

                request._receive = receive  # type: ignore[attr-defined]
                request._body = scrubbed_body

        return await call_next(request)

    def _scrub_payload(self, obj: Any) -> Any:
        if isinstance(obj, str):
            return self._scrub_text(obj)
        if isinstance(obj, dict):
            return {key: self._scrub_payload(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [self._scrub_payload(item) for item in obj]
        return obj

    def _scrub_text(self, text: str) -> str:
        text = self.SSN_PATTERN.sub("[REDACTED_SSN]", text)
        return self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
