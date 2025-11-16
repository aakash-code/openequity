"""
Real-time Market Data API Endpoints
Provides live data from Indian brokers via OpenAlgo
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User
from app.services.openalgo_connector import OpenAlgoConnector

router = APIRouter()


# Pydantic models
class QuotesRequest(BaseModel):
    symbols: List[str]
    exchange: str = 'NSE'


class HistoryRequest(BaseModel):
    symbol: str
    exchange: str = 'NSE'
    interval: str = '1d'
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class OrderRequest(BaseModel):
    symbol: str
    exchange: str
    action: str  # BUY or SELL
    quantity: int
    price: Optional[float] = None
    order_type: str = 'MARKET'
    product: str = 'MIS'


# ==================== Market Data Endpoints ====================

@router.get("/ping")
async def ping_openalgo(
    current_user: User = Depends(get_current_user),
):
    """Test OpenAlgo connectivity"""
    connector = OpenAlgoConnector()

    try:
        result = await connector.ping()
        return {
            'status': 'connected',
            'openalgo_status': result
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"OpenAlgo connection failed: {str(e)}"
        )


@router.post("/quotes")
async def get_live_quotes(
    request: QuotesRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Get real-time quotes for symbols

    Example:
    {
        "symbols": ["RELIANCE", "TCS", "INFY"],
        "exchange": "NSE"
    }
    """
    connector = OpenAlgoConnector()

    try:
        quotes = await connector.get_quotes(request.symbols, request.exchange)
        return quotes
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch quotes: {str(e)}"
        )


@router.post("/history")
async def get_historical_data(
    request: HistoryRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Get historical OHLC data

    Example:
    {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "interval": "1d",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    """
    connector = OpenAlgoConnector()

    try:
        history = await connector.get_history(
            request.symbol,
            request.exchange,
            request.interval,
            request.start_date,
            request.end_date
        )
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch historical data: {str(e)}"
        )


@router.get("/depth/{symbol}")
async def get_market_depth(
    symbol: str,
    exchange: str = Query('NSE', description="Exchange code"),
    current_user: User = Depends(get_current_user),
):
    """Get market depth (order book) for a symbol"""
    connector = OpenAlgoConnector()

    try:
        depth = await connector.get_depth(symbol.upper(), exchange)
        return depth
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch market depth: {str(e)}"
        )


@router.get("/search")
async def search_symbols(
    query: str = Query(..., description="Search query"),
    exchange: Optional[str] = Query(None, description="Exchange filter"),
    current_user: User = Depends(get_current_user),
):
    """Search for symbols"""
    connector = OpenAlgoConnector()

    try:
        results = await connector.search_symbols(query, exchange)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search symbols: {str(e)}"
        )


# ==================== Account & Portfolio Endpoints ====================

@router.get("/positions")
async def get_broker_positions(
    current_user: User = Depends(get_current_user),
):
    """Get current positions from connected broker"""
    connector = OpenAlgoConnector()

    try:
        positions = await connector.get_positions()
        return positions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch positions: {str(e)}"
        )


@router.get("/holdings")
async def get_broker_holdings(
    current_user: User = Depends(get_current_user),
):
    """Get demat holdings from connected broker"""
    connector = OpenAlgoConnector()

    try:
        holdings = await connector.get_holdings()
        return holdings
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch holdings: {str(e)}"
        )


@router.get("/funds")
async def get_account_funds(
    current_user: User = Depends(get_current_user),
):
    """Get account funds and margins"""
    connector = OpenAlgoConnector()

    try:
        funds = await connector.get_funds()
        return funds
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch funds: {str(e)}"
        )


@router.get("/orders")
async def get_order_book(
    current_user: User = Depends(get_current_user),
):
    """Get order book from broker"""
    connector = OpenAlgoConnector()

    try:
        orders = await connector.get_orderbook()
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch orders: {str(e)}"
        )


# ==================== Trading Endpoints ====================

@router.post("/place-order")
async def place_broker_order(
    order: OrderRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Place order through connected broker

    Example:
    {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "action": "BUY",
        "quantity": 10,
        "order_type": "LIMIT",
        "price": 2500.00,
        "product": "CNC"
    }
    """
    connector = OpenAlgoConnector()

    try:
        result = await connector.place_order(
            symbol=order.symbol,
            exchange=order.exchange,
            action=order.action,
            quantity=order.quantity,
            price=order.price,
            order_type=order.order_type,
            product=order.product
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to place order: {str(e)}"
        )


@router.delete("/cancel-order/{order_id}")
async def cancel_broker_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
):
    """Cancel an order"""
    connector = OpenAlgoConnector()

    try:
        result = await connector.cancel_order(order_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel order: {str(e)}"
        )
