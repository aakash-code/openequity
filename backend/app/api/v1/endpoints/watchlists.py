"""
Watchlist and Stock Screening Endpoints
Provides watchlist management and stock screening functionality
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.watchlist import Watchlist, WatchlistItem
from app.models.company import Company
from app.services.stock_screener import StockScreenerService

router = APIRouter()


# Pydantic models
class WatchlistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    tags: Optional[List[str]] = None


class WatchlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class WatchlistItemCreate(BaseModel):
    ticker: str
    notes: Optional[str] = None
    target_price: Optional[float] = None


class ScreeningCriteria(BaseModel):
    # Market cap
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None

    # Valuation
    pe_ratio_min: Optional[float] = None
    pe_ratio_max: Optional[float] = None
    pb_ratio_min: Optional[float] = None
    pb_ratio_max: Optional[float] = None
    ps_ratio_min: Optional[float] = None
    ps_ratio_max: Optional[float] = None

    # Profitability
    roe_min: Optional[float] = None
    roe_max: Optional[float] = None
    roa_min: Optional[float] = None
    roa_max: Optional[float] = None
    roic_min: Optional[float] = None
    roic_max: Optional[float] = None
    profit_margin_min: Optional[float] = None
    profit_margin_max: Optional[float] = None

    # Growth
    revenue_growth_min: Optional[float] = None
    revenue_growth_max: Optional[float] = None
    earnings_growth_min: Optional[float] = None
    earnings_growth_max: Optional[float] = None

    # Dividend
    dividend_yield_min: Optional[float] = None
    dividend_yield_max: Optional[float] = None
    payout_ratio_min: Optional[float] = None
    payout_ratio_max: Optional[float] = None

    # Financial health
    current_ratio_min: Optional[float] = None
    current_ratio_max: Optional[float] = None
    debt_to_equity_min: Optional[float] = None
    debt_to_equity_max: Optional[float] = None
    interest_coverage_min: Optional[float] = None

    # Categorical
    sector: Optional[List[str]] = None
    industry: Optional[List[str]] = None
    exchange: Optional[List[str]] = None
    country: Optional[List[str]] = None

    # Limit
    limit: int = 100


# ==================== Watchlist Endpoints ====================

@router.post("/watchlists")
def create_watchlist(
    watchlist_data: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new watchlist"""
    watchlist = Watchlist(
        user_id=current_user.id,
        name=watchlist_data.name,
        description=watchlist_data.description,
        is_public=watchlist_data.is_public,
        tags=watchlist_data.tags or []
    )

    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)

    return {
        'id': str(watchlist.id),
        'name': watchlist.name,
        'description': watchlist.description,
        'is_public': watchlist.is_public,
        'tags': watchlist.tags,
        'created_at': watchlist.created_at.isoformat(),
        'item_count': 0
    }


@router.get("/watchlists")
def get_watchlists(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all watchlists for the current user"""
    watchlists = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).count()

    result_watchlists = []
    for wl in watchlists:
        item_count = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == wl.id).count()
        result_watchlists.append({
            'id': str(wl.id),
            'name': wl.name,
            'description': wl.description,
            'is_public': wl.is_public,
            'tags': wl.tags,
            'created_at': wl.created_at.isoformat(),
            'updated_at': wl.updated_at.isoformat() if wl.updated_at else None,
            'item_count': item_count
        })

    return {
        'watchlists': result_watchlists,
        'total': total,
        'skip': skip,
        'limit': limit
    }


@router.get("/watchlists/{watchlist_id}")
def get_watchlist(
    watchlist_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific watchlist with its items"""
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    # Get items with company data
    items = (
        db.query(WatchlistItem, Company)
        .join(Company, WatchlistItem.ticker == Company.ticker)
        .filter(WatchlistItem.watchlist_id == watchlist_id)
        .all()
    )

    items_data = []
    for item, company in items:
        items_data.append({
            'id': str(item.id),
            'ticker': item.ticker,
            'notes': item.notes,
            'target_price': item.target_price,
            'added_at': item.added_at.isoformat(),
            'company': {
                'name': company.name,
                'sector': company.sector,
                'industry': company.industry,
                'market_cap': company.market_cap,
                'pe_ratio': company.pe_ratio,
                'dividend_yield': company.dividend_yield,
                'revenue_growth': company.revenue_growth
            }
        })

    return {
        'id': str(watchlist.id),
        'name': watchlist.name,
        'description': watchlist.description,
        'is_public': watchlist.is_public,
        'tags': watchlist.tags,
        'created_at': watchlist.created_at.isoformat(),
        'updated_at': watchlist.updated_at.isoformat() if watchlist.updated_at else None,
        'items': items_data,
        'item_count': len(items_data)
    }


@router.put("/watchlists/{watchlist_id}")
def update_watchlist(
    watchlist_id: str,
    watchlist_data: WatchlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a watchlist"""
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    # Update fields
    if watchlist_data.name is not None:
        watchlist.name = watchlist_data.name
    if watchlist_data.description is not None:
        watchlist.description = watchlist_data.description
    if watchlist_data.tags is not None:
        watchlist.tags = watchlist_data.tags
    if watchlist_data.is_public is not None:
        watchlist.is_public = watchlist_data.is_public

    db.commit()
    db.refresh(watchlist)

    return {
        'id': str(watchlist.id),
        'name': watchlist.name,
        'description': watchlist.description,
        'is_public': watchlist.is_public,
        'tags': watchlist.tags,
        'updated_at': watchlist.updated_at.isoformat() if watchlist.updated_at else None
    }


@router.delete("/watchlists/{watchlist_id}")
def delete_watchlist(
    watchlist_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a watchlist"""
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    db.delete(watchlist)
    db.commit()

    return {'message': 'Watchlist deleted successfully'}


# ==================== Watchlist Item Endpoints ====================

@router.post("/watchlists/{watchlist_id}/items")
def add_watchlist_item(
    watchlist_id: str,
    item_data: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a stock to a watchlist"""
    # Verify watchlist ownership
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    # Verify company exists
    company = db.query(Company).filter(Company.ticker == item_data.ticker.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if already in watchlist
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.watchlist_id == watchlist_id,
        WatchlistItem.ticker == item_data.ticker.upper()
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")

    # Create item
    item = WatchlistItem(
        watchlist_id=watchlist_id,
        ticker=item_data.ticker.upper(),
        notes=item_data.notes,
        target_price=item_data.target_price
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        'id': str(item.id),
        'watchlist_id': str(watchlist_id),
        'ticker': item.ticker,
        'notes': item.notes,
        'target_price': item.target_price,
        'added_at': item.added_at.isoformat()
    }


@router.delete("/watchlists/{watchlist_id}/items/{item_id}")
def remove_watchlist_item(
    watchlist_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a stock from a watchlist"""
    # Verify watchlist ownership
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    # Find and delete item
    item = db.query(WatchlistItem).filter(
        WatchlistItem.id == item_id,
        WatchlistItem.watchlist_id == watchlist_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return {'message': 'Item removed from watchlist'}


# ==================== Stock Screening Endpoints ====================

@router.get("/screening/templates")
def get_screening_templates():
    """Get all available screening templates"""
    screener = StockScreenerService()
    templates = screener.get_templates()

    return {'templates': templates}


@router.get("/screening/templates/{template_id}")
def get_screening_template(template_id: str):
    """Get a specific screening template"""
    screener = StockScreenerService()
    template = screener.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.post("/screening/screen")
def screen_stocks(
    criteria: ScreeningCriteria,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Screen stocks based on custom criteria"""
    screener = StockScreenerService()

    # Convert Pydantic model to dict, excluding None values
    criteria_dict = {k: v for k, v in criteria.dict().items() if v is not None}

    results = screener.screen_stocks(db, criteria_dict)

    return {
        'results': results,
        'count': len(results),
        'criteria': criteria_dict
    }


@router.post("/screening/screen-by-template/{template_id}")
def screen_by_template(
    template_id: str,
    additional_criteria: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Screen stocks using a pre-built template"""
    screener = StockScreenerService()

    results = screener.screen_by_template(db, template_id, additional_criteria)

    if not results and not screener.get_template(template_id):
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        'results': results,
        'count': len(results),
        'template_id': template_id,
        'template_name': screener.get_template(template_id)['name'] if screener.get_template(template_id) else None
    }
