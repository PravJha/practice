# AI Prompt Scrubber Practice Repo

This repository is a scaffold for a FastAPI-based service that intercepts prompts, scrubs PII, and forwards sanitized text to a mockable LLM integration.

## What is included

- `app/main.py` — FastAPI application entry point
- `app/core/middleware.py` — `PII Scrubber` middleware for masking SSNs and emails
- `app/core/llm_client.py` — mockable LLM client abstraction
- `app/api/v1/router.py` — API router with a summarization endpoint
- `tests/` — test coverage for middleware and summarization flow
- `Dockerfile` and `docker-compose.yml` — containerization setup

## Quick start

1. Create a new repo from this scaffold:

   ```bash
   cd practice-ai-llm-scrubber
   git init
   git add .
   git commit -m "Initial scaffold for AI prompt scrubber"
   ```

2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run locally:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

4. Run tests:

   ```bash
   pytest
   ```

## Key tasks for the interview challenge

- Refactor this scaffold into production-ready architecture.
- Build a robust PII scrubber middleware for SSN and email masking.
- Keep the LLM integration mockable for safe testing.
- Containerize the final application with `Dockerfile` and `docker-compose.yml`.

## Notes

- The current scaffold uses a `MockLLMClient` by default so no external tokens are consumed during testing.
- The service is designed to easily swap in a real provider via dependency injection.
