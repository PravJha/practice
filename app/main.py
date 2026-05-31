from fastapi import FastAPI

from app.api.v1.router import router
from app.core.middleware import PiiScrubberMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="AI Prompt Scrubber", version="0.1.0")
    app.add_middleware(PiiScrubberMiddleware)
    app.include_router(router, prefix="/api")
    return app


app = create_app()
