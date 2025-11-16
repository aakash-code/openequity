"""
Options and Derivatives API Endpoints
Provides options chain, futures data, Greeks, and F&O analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User
from app.services.options_chain import OptionsChainService
from app.services.derivatives import DerivativesService

router = APIRouter()


# Pydantic models
class StrategyLeg(BaseModel):
    strike: float
    option_type: str  # 'call' or 'put'
    position: str  # 'buy' or 'sell'
    quantity: int
    time_to_expiry: Optional[float] = 0.1
    volatility: Optional[float] = 0.3


class StrategyRequest(BaseModel):
    ticker: str
    legs: List[StrategyLeg]


class PositionRequest(BaseModel):
    positions: List[dict]


# ==================== Options Endpoints ====================

@router.get("/options/chain/{ticker}")
def get_options_chain(
    ticker: str,
    expiry_date: Optional[str] = Query(None, description="Expiry date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
):
    """Get complete options chain for a ticker"""
    service = OptionsChainService()
    chain = service.get_options_chain(ticker.upper(), expiry_date)

    return chain


@router.get("/options/greeks")
def calculate_option_greeks(
    spot_price: float = Query(..., description="Current stock price"),
    strike: float = Query(..., description="Strike price"),
    time_to_expiry: float = Query(..., description="Time to expiry in years"),
    volatility: float = Query(..., description="Implied volatility (as decimal)"),
    risk_free_rate: float = Query(0.05, description="Risk-free rate"),
    option_type: str = Query(..., description="'call' or 'put'"),
    current_user: User = Depends(get_current_user),
):
    """Calculate option Greeks"""
    service = OptionsChainService()

    if option_type.lower() not in ['call', 'put']:
        raise HTTPException(status_code=400, detail="option_type must be 'call' or 'put'")

    greeks = service.get_option_greeks(
        spot_price,
        strike,
        time_to_expiry,
        volatility,
        risk_free_rate,
        option_type.lower()
    )

    return {
        'spot_price': spot_price,
        'strike': strike,
        'time_to_expiry': time_to_expiry,
        'volatility': volatility,
        'option_type': option_type.lower(),
        'greeks': greeks
    }


@router.post("/options/strategy")
def analyze_options_strategy(
    strategy: StrategyRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze an options strategy"""
    service = OptionsChainService()

    # Convert Pydantic models to dicts
    legs = [leg.dict() for leg in strategy.legs]

    analysis = service.analyze_strategy(strategy.ticker.upper(), legs)

    return analysis


# ==================== Futures Endpoints ====================

@router.get("/futures/chain/{ticker}")
def get_futures_chain(
    ticker: str,
    expiry_date: Optional[str] = Query(None, description="Expiry date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
):
    """Get futures chain for a ticker"""
    service = DerivativesService()
    chain = service.get_futures_chain(ticker.upper(), expiry_date)

    return chain


@router.post("/futures/margin")
def calculate_margin(
    positions: PositionRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate margin requirements for F&O positions"""
    service = DerivativesService()
    margin_calc = service.calculate_position_margin(positions.positions)

    return margin_calc


@router.post("/futures/analyze-positions")
def analyze_fno_portfolio(
    positions: PositionRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze F&O position portfolio"""
    service = DerivativesService()
    analysis = service.analyze_fno_positions(positions.positions)

    return analysis


@router.get("/futures/oi-analysis/{ticker}")
def get_oi_analysis(
    ticker: str,
    instrument_type: str = Query('options', description="'options' or 'futures'"),
    current_user: User = Depends(get_current_user),
):
    """Analyze open interest build-up"""
    service = DerivativesService()

    if instrument_type.lower() not in ['options', 'futures']:
        raise HTTPException(status_code=400, detail="instrument_type must be 'options' or 'futures'")

    analysis = service.get_oi_analysis(ticker.upper(), instrument_type.lower())

    return analysis
