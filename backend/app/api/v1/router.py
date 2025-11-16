"""
API v1 router aggregating all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, companies, financials, valuations, analysis, advanced_valuations, earnings_quality, portfolios, watchlists, indian_market, ipo_primary_market, options_derivatives, realtime_data

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(financials.router, prefix="/financials", tags=["financials"])
api_router.include_router(valuations.router, prefix="/valuations", tags=["valuations"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(advanced_valuations.router, prefix="/advanced-valuations", tags=["advanced-valuations"])
api_router.include_router(earnings_quality.router, prefix="/earnings-quality", tags=["earnings-quality"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])
api_router.include_router(watchlists.router, prefix="/screening", tags=["screening"])
api_router.include_router(indian_market.router, prefix="", tags=["indian-market", "sebi", "currency"])
api_router.include_router(ipo_primary_market.router, prefix="/primary-market", tags=["ipo", "rights-issues", "ofs", "buybacks"])
api_router.include_router(options_derivatives.router, prefix="/derivatives", tags=["options", "futures", "fno"])
api_router.include_router(realtime_data.router, prefix="/realtime", tags=["realtime", "broker-data", "openalgo"])
