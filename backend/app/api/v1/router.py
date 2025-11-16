"""
API v1 router aggregating all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, companies, financials, valuations, analysis, advanced_valuations

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(financials.router, prefix="/financials", tags=["financials"])
api_router.include_router(valuations.router, prefix="/valuations", tags=["valuations"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(advanced_valuations.router, prefix="/advanced-valuations", tags=["advanced-valuations"])
