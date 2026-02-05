"""API v1 router."""
from fastapi import APIRouter
from app.api.routes import requests_router

api_router = APIRouter()
api_router.include_router(requests_router)
