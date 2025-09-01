from fastapi import APIRouter
from .health import router as health_router
from .ingest import router as ingest_router
from .search import router as search_router
from .chat import router as chat_router

router = APIRouter()
router.include_router(health_router)
router.include_router(ingest_router)
router.include_router(search_router)
router.include_router(chat_router)
