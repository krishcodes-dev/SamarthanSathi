"""API v1 router."""
from fastapi import APIRouter
from app.api.routes.requests import router as requests_router
from app.api.routes.health import router as health_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.preview import router as preview_router

api_router = APIRouter()
api_router.include_router(preview_router)
api_router.include_router(requests_router)
api_router.include_router(feedback_router)
api_router.include_router(health_router)

@api_router.post("/requests/direct-check")
def direct_check():
    return {"status": "ok"}
