from fastapi import APIRouter

from app.api.v1.endpoints.summarization import router as summarization_router

router = APIRouter()
router.include_router(summarization_router)
