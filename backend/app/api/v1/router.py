"""
API v1 router aggregating all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, companies

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
