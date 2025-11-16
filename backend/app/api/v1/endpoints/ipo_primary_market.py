"""
IPO and Primary Market API Endpoints
Provides IPO tracking, rights issues, OFS, and buyback data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.core.deps import get_current_user
from app.models.user import User
from app.services.ipo_tracker import IPOTrackerService
from app.services.primary_market import PrimaryMarketService

router = APIRouter()


# ==================== IPO Endpoints ====================

@router.get("/ipos")
def get_ipos(
    status: Optional[str] = Query(None, description="Filter by status: upcoming, open, closed, listed, withdrawn"),
    limit: int = Query(50, description="Maximum number of IPOs to return"),
    current_user: User = Depends(get_current_user),
):
    """Get list of IPOs filtered by status"""
    service = IPOTrackerService()

    valid_statuses = ['upcoming', 'open', 'closed', 'listed', 'withdrawn']
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    ipos = service.get_ipo_list(status, limit)

    return {
        'ipos': ipos,
        'count': len(ipos),
        'filter': status or 'all'
    }


@router.get("/ipos/{ipo_id}")
def get_ipo_details(
    ipo_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get detailed information about a specific IPO"""
    service = IPOTrackerService()
    ipo = service.get_ipo_details(ipo_id)

    if not ipo:
        raise HTTPException(status_code=404, detail="IPO not found")

    return ipo


@router.get("/ipos/{ipo_id}/subscription")
def get_ipo_subscription(
    ipo_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get real-time subscription data for an IPO"""
    service = IPOTrackerService()

    # Verify IPO exists
    ipo = service.get_ipo_details(ipo_id)
    if not ipo:
        raise HTTPException(status_code=404, detail="IPO not found")

    # Only return subscription for open/closed/listed IPOs
    if ipo['status'] not in ['open', 'closed', 'listed']:
        raise HTTPException(
            status_code=400,
            detail="Subscription data only available for open, closed, or listed IPOs"
        )

    subscription = service.get_subscription_data(ipo_id)
    return subscription


@router.get("/ipos/{ipo_id}/listing-gains")
def get_ipo_listing_gains(
    ipo_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get listing gains and performance for an IPO"""
    service = IPOTrackerService()

    # Verify IPO exists
    ipo = service.get_ipo_details(ipo_id)
    if not ipo:
        raise HTTPException(status_code=404, detail="IPO not found")

    # Only return listing gains for listed IPOs
    if ipo['status'] != 'listed':
        raise HTTPException(
            status_code=400,
            detail="Listing gains only available for listed IPOs"
        )

    gains = service.get_listing_gains(ipo_id)
    return gains


@router.get("/ipos/{ipo_id}/gmp")
def get_ipo_grey_market_premium(
    ipo_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get grey market premium for an IPO"""
    service = IPOTrackerService()

    # Verify IPO exists
    ipo = service.get_ipo_details(ipo_id)
    if not ipo:
        raise HTTPException(status_code=404, detail="IPO not found")

    # Only return GMP for upcoming/open IPOs
    if ipo['status'] not in ['upcoming', 'open']:
        raise HTTPException(
            status_code=400,
            detail="Grey market premium only available for upcoming or open IPOs"
        )

    gmp = service.get_grey_market_premium(ipo_id)
    return gmp


@router.get("/ipos/{ipo_id}/allotment/{application_number}")
def check_ipo_allotment(
    ipo_id: str,
    application_number: str,
    current_user: User = Depends(get_current_user),
):
    """Check IPO allotment status"""
    service = IPOTrackerService()

    # Verify IPO exists
    ipo = service.get_ipo_details(ipo_id)
    if not ipo:
        raise HTTPException(status_code=404, detail="IPO not found")

    allotment = service.get_allotment_status(ipo_id, application_number)
    return allotment


# ==================== Rights Issue Endpoints ====================

@router.get("/rights-issues")
def get_rights_issues(
    status: Optional[str] = Query(None, description="Filter by status: upcoming, open, closed"),
    limit: int = Query(20, description="Maximum number to return"),
    current_user: User = Depends(get_current_user),
):
    """Get list of rights issues"""
    service = PrimaryMarketService()

    valid_statuses = ['upcoming', 'open', 'closed']
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    issues = service.get_rights_issues(status, limit)

    return {
        'rights_issues': issues,
        'count': len(issues),
        'filter': status or 'all'
    }


@router.get("/rights-issues/{issue_id}")
def get_rights_issue_details(
    issue_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get detailed information about a rights issue"""
    service = PrimaryMarketService()
    issue = service.get_rights_issue_details(issue_id)

    if not issue:
        raise HTTPException(status_code=404, detail="Rights issue not found")

    return issue


# ==================== OFS Endpoints ====================

@router.get("/ofs")
def get_ofs_list(
    status: Optional[str] = Query(None, description="Filter by status: upcoming, open, closed"),
    limit: int = Query(20, description="Maximum number to return"),
    current_user: User = Depends(get_current_user),
):
    """Get list of OFS (Offer for Sale)"""
    service = PrimaryMarketService()

    valid_statuses = ['upcoming', 'open', 'closed']
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    ofs_list = service.get_ofs_list(status, limit)

    return {
        'ofs': ofs_list,
        'count': len(ofs_list),
        'filter': status or 'all'
    }


@router.get("/ofs/{ofs_id}")
def get_ofs_details(
    ofs_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get detailed information about an OFS"""
    service = PrimaryMarketService()
    ofs = service.get_ofs_details(ofs_id)

    if not ofs:
        raise HTTPException(status_code=404, detail="OFS not found")

    return ofs


# ==================== Buyback Endpoints ====================

@router.get("/buybacks")
def get_buybacks(
    status: Optional[str] = Query(None, description="Filter by status: upcoming, open, closed"),
    limit: int = Query(20, description="Maximum number to return"),
    current_user: User = Depends(get_current_user),
):
    """Get list of buyback offers"""
    service = PrimaryMarketService()

    valid_statuses = ['upcoming', 'open', 'closed']
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    buybacks = service.get_buyback_list(status, limit)

    return {
        'buybacks': buybacks,
        'count': len(buybacks),
        'filter': status or 'all'
    }


@router.get("/buybacks/{buyback_id}")
def get_buyback_details(
    buyback_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get detailed information about a buyback"""
    service = PrimaryMarketService()
    buyback = service.get_buyback_details(buyback_id)

    if not buyback:
        raise HTTPException(status_code=404, detail="Buyback not found")

    return buyback
