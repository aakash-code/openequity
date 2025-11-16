"""
Indian Market Data API Endpoints
Provides NSE/BSE data, SEBI filings, and currency conversion
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.indian_market import IndianMarketService
from app.services.sebi_filings import SEBIFilingsService
from app.services.currency_conversion import CurrencyConversionService

router = APIRouter()


# Pydantic models for requests
class CurrencyConvertRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


class MetricsConvertRequest(BaseModel):
    metrics: Dict[str, float]
    from_currency: str
    to_currency: str


# ==================== Indian Market Endpoints ====================

@router.get("/indian-market/indices")
def get_indian_indices(
    current_user: User = Depends(get_current_user),
):
    """Get all Indian market indices (NIFTY, SENSEX, etc.)"""
    service = IndianMarketService()
    indices = service.get_indian_indices()

    return {
        'indices': indices,
        'count': len(indices)
    }


@router.get("/indian-market/market-status")
def get_market_status(
    current_user: User = Depends(get_current_user),
):
    """Check if Indian market is currently open"""
    service = IndianMarketService()
    status = service.get_market_status()

    return status


@router.get("/indian-market/corporate-actions/{ticker}")
def get_corporate_actions(
    ticker: str,
    action_type: Optional[str] = None,
    days: int = 90,
    current_user: User = Depends(get_current_user),
):
    """Get corporate actions for a stock (dividends, bonus, splits)"""
    service = IndianMarketService()

    valid_types = ['dividend', 'bonus', 'split', 'rights']
    if action_type and action_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action_type. Must be one of: {', '.join(valid_types)}"
        )

    actions = service.get_corporate_actions(ticker.upper(), action_type, days)

    return {
        'ticker': ticker.upper(),
        'actions': actions,
        'count': len(actions),
        'period_days': days
    }


@router.get("/indian-market/price-bands/{ticker}")
def get_price_bands(
    ticker: str,
    current_price: float = Query(..., description="Current market price"),
    current_user: User = Depends(get_current_user),
):
    """Get price circuit limits for a stock"""
    service = IndianMarketService()
    bands = service.get_price_bands(ticker.upper(), current_price)

    return {
        'ticker': ticker.upper(),
        **bands
    }


@router.get("/indian-market/delivery/{ticker}")
def get_delivery_percentage(
    ticker: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
):
    """Get delivery percentage data for a stock"""
    service = IndianMarketService()
    delivery_data = service.get_delivery_percentage(ticker.upper(), days)

    return {
        'ticker': ticker.upper(),
        'data': delivery_data,
        'period_days': days
    }


@router.get("/indian-market/fii-dii")
def get_fii_dii_activity(
    days: int = 30,
    current_user: User = Depends(get_current_user),
):
    """Get FII/DII (institutional investor) activity"""
    service = IndianMarketService()
    activity = service.get_fii_dii_activity(days)

    return {
        'data': activity,
        'period_days': days
    }


@router.get("/indian-market/sectors")
def get_nse_sectors(
    current_user: User = Depends(get_current_user),
):
    """Get list of NSE sectors"""
    service = IndianMarketService()
    sectors = service.get_nse_sectors()

    return {
        'sectors': sectors,
        'count': len(sectors)
    }


# ==================== SEBI Filings Endpoints ====================

@router.get("/sebi/filing-types")
def get_filing_types(
    current_user: User = Depends(get_current_user),
):
    """Get all SEBI filing types"""
    service = SEBIFilingsService()
    filing_types = service.get_filing_types()

    return {
        'filing_types': filing_types,
        'count': len(filing_types)
    }


@router.get("/sebi/filings/{ticker}")
def get_recent_filings(
    ticker: str,
    filing_type: Optional[str] = None,
    days: int = 90,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """Get recent SEBI filings for a company"""
    service = SEBIFilingsService()

    # Validate filing_type if provided
    if filing_type:
        valid_types = service.get_filing_types()
        if filing_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filing_type. Use /sebi/filing-types to see valid types"
            )

    filings = service.get_recent_filings(ticker.upper(), filing_type, days, limit)

    return {
        'ticker': ticker.upper(),
        'filings': filings,
        'count': len(filings),
        'period_days': days
    }


@router.get("/sebi/shareholding/{ticker}")
def get_shareholding_pattern(
    ticker: str,
    quarter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Get shareholding pattern for a company"""
    service = SEBIFilingsService()

    # If quarter not provided, use current quarter
    if not quarter:
        now = datetime.now()
        quarter_month = ((now.month - 1) // 3) * 3 + 1
        quarter = f"Q{((quarter_month - 1) // 3) + 1} {now.year}"

    pattern = service.get_shareholding_pattern(ticker.upper(), quarter)

    return {
        'ticker': ticker.upper(),
        'quarter': quarter,
        **pattern
    }


@router.get("/sebi/board-meetings/{ticker}")
def get_board_meetings(
    ticker: str,
    days_ahead: int = 30,
    days_back: int = 90,
    current_user: User = Depends(get_current_user),
):
    """Get board meeting information"""
    service = SEBIFilingsService()
    meetings = service.get_board_meetings(ticker.upper(), days_ahead, days_back)

    return {
        'ticker': ticker.upper(),
        **meetings
    }


@router.get("/sebi/insider-trading/{ticker}")
def get_insider_trading(
    ticker: str,
    days: int = 180,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """Get insider trading disclosures"""
    service = SEBIFilingsService()
    trades = service.get_insider_trading(ticker.upper(), days, limit)

    return {
        'ticker': ticker.upper(),
        'trades': trades,
        'count': len(trades),
        'period_days': days
    }


@router.get("/sebi/compliance/{ticker}")
def get_compliance_status(
    ticker: str,
    current_user: User = Depends(get_current_user),
):
    """Get SEBI compliance status"""
    service = SEBIFilingsService()
    compliance = service.get_compliance_status(ticker.upper())

    return {
        'ticker': ticker.upper(),
        **compliance
    }


# ==================== Currency Conversion Endpoints ====================

@router.get("/currency/supported")
def get_supported_currencies(
    current_user: User = Depends(get_current_user),
):
    """Get all supported currencies with their info"""
    service = CurrencyConversionService()
    currencies = service.get_supported_currencies()

    return {
        'currencies': currencies,
        'count': len(currencies)
    }


@router.get("/currency/rate")
def get_exchange_rate(
    from_currency: str = Query(..., description="Source currency code (e.g., USD)"),
    to_currency: str = Query(..., description="Target currency code (e.g., INR)"),
    current_user: User = Depends(get_current_user),
):
    """Get exchange rate between two currencies"""
    service = CurrencyConversionService()

    try:
        rate = service.get_exchange_rate(from_currency, to_currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        'from_currency': from_currency.upper(),
        'to_currency': to_currency.upper(),
        'rate': rate,
        'from_symbol': service.get_currency_symbol(from_currency),
        'to_symbol': service.get_currency_symbol(to_currency),
        'timestamp': datetime.now().isoformat()
    }


@router.post("/currency/convert")
def convert_currency(
    request: CurrencyConvertRequest,
    current_user: User = Depends(get_current_user),
):
    """Convert an amount from one currency to another"""
    service = CurrencyConversionService()

    try:
        converted_amount = service.convert_amount(
            request.amount,
            request.from_currency,
            request.to_currency
        )
        rate = service.get_exchange_rate(request.from_currency, request.to_currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        'original_amount': request.amount,
        'converted_amount': converted_amount,
        'from_currency': request.from_currency.upper(),
        'to_currency': request.to_currency.upper(),
        'exchange_rate': rate,
        'from_formatted': service.format_amount(request.amount, request.from_currency),
        'to_formatted': service.format_amount(converted_amount, request.to_currency),
        'to_formatted_indian': service.format_amount(
            converted_amount,
            request.to_currency,
            indian_format=(request.to_currency.upper() == 'INR')
        ),
        'timestamp': datetime.now().isoformat()
    }


@router.post("/currency/convert-metrics")
def convert_financial_metrics(
    request: MetricsConvertRequest,
    current_user: User = Depends(get_current_user),
):
    """Convert a dictionary of financial metrics from one currency to another"""
    service = CurrencyConversionService()

    try:
        converted_metrics = service.convert_financial_metrics(
            request.metrics,
            request.from_currency,
            request.to_currency
        )
        rate = service.get_exchange_rate(request.from_currency, request.to_currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        'original_metrics': request.metrics,
        'converted_metrics': converted_metrics,
        'from_currency': request.from_currency.upper(),
        'to_currency': request.to_currency.upper(),
        'exchange_rate': rate,
        'timestamp': datetime.now().isoformat()
    }


@router.get("/currency/historical")
def get_historical_rates(
    from_currency: str = Query(..., description="Source currency code"),
    to_currency: str = Query(..., description="Target currency code"),
    days: int = Query(30, description="Number of days of historical data"),
    current_user: User = Depends(get_current_user),
):
    """Get historical exchange rates"""
    service = CurrencyConversionService()

    if days < 1 or days > 365:
        raise HTTPException(
            status_code=400,
            detail="Days must be between 1 and 365"
        )

    try:
        historical_rates = service.get_historical_rates(
            from_currency,
            to_currency,
            days
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        'from_currency': from_currency.upper(),
        'to_currency': to_currency.upper(),
        'rates': historical_rates,
        'count': len(historical_rates),
        'period_days': days
    }
