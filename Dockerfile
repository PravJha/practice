# ── base: shared dependency layer ─────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ── test: full source + dev deps, used by docker compose run test ─────────────
FROM base AS test

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy everything so pytest can discover all test files
COPY . .

# Tests always run with the mock provider — no real API key needed
ENV LLM_PROVIDER=mock

CMD ["pytest", "tests/", "-v", "--tb=short"]

# ── prod: minimal runtime image ────────────────────────────────────────────────
FROM base AS prod

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser

COPY app/ ./app/

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
