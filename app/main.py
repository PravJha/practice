from fastapi import FastAPI

from app.api.v1.router import router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import PiiScrubberMiddleware


def create_app() -> FastAPI:
    configure_logging(settings.log_level)

    app = FastAPI(title="AI Prompt Scrubber", version="0.1.0")
    app.add_middleware(PiiScrubberMiddleware)
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
