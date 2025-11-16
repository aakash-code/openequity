"""
Company endpoints for equity research
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.core.deps import get_db, get_current_user, get_current_admin_user
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyResponse, CompanyCreate, CompanyUpdate, CompanySearch

router = APIRouter()


@router.get("/search", response_model=List[CompanySearch])
def search_companies(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search companies by ticker, name, or sector

    Args:
        q: Search query string
        limit: Maximum number of results
        db: Database session
        current_user: Authenticated user

    Returns:
        List of matching companies
    """
    search_term = f"%{q}%"

    companies = db.query(Company).filter(
        or_(
            Company.ticker.ilike(search_term),
            Company.name.ilike(search_term),
            Company.sector.ilike(search_term),
            Company.industry.ilike(search_term)
        ),
        Company.is_active == True
    ).limit(limit).all()

    return companies


@router.get("", response_model=List[CompanyResponse])
def get_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of companies with optional filters

    Args:
        skip: Number of records to skip (pagination)
        limit: Number of records to return
        sector: Filter by sector
        exchange: Filter by exchange
        db: Database session
        current_user: Authenticated user

    Returns:
        List of companies
    """
    query = db.query(Company).filter(Company.is_active == True)

    if sector:
        query = query.filter(Company.sector == sector)

    if exchange:
        query = query.filter(Company.exchange == exchange)

    companies = query.offset(skip).limit(limit).all()
    return companies


@router.get("/{ticker}", response_model=CompanyResponse)
def get_company(
    ticker: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get company details by ticker

    Args:
        ticker: Company ticker symbol
        db: Database session
        current_user: Authenticated user

    Returns:
        Company details

    Raises:
        HTTPException: If company not found
    """
    company = db.query(Company).filter(
        Company.ticker == ticker.upper(),
        Company.is_active == True
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker {ticker} not found"
        )

    return company


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new company (Admin only)

    Args:
        company_data: Company creation data
        db: Database session
        current_user: Authenticated admin user

    Returns:
        Created company

    Raises:
        HTTPException: If company already exists
    """
    # Check if company already exists
    existing_company = db.query(Company).filter(
        Company.ticker == company_data.ticker.upper()
    ).first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with ticker {company_data.ticker} already exists"
        )

    # Create company
    company = Company(**company_data.dict())
    company.ticker = company.ticker.upper()

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@router.patch("/{ticker}", response_model=CompanyResponse)
def update_company(
    ticker: str,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update company information (Admin only)

    Args:
        ticker: Company ticker symbol
        company_data: Company update data
        db: Database session
        current_user: Authenticated admin user

    Returns:
        Updated company

    Raises:
        HTTPException: If company not found
    """
    company = db.query(Company).filter(Company.ticker == ticker.upper()).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker {ticker} not found"
        )

    # Update fields
    update_data = company_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    ticker: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete (deactivate) a company (Admin only)

    Args:
        ticker: Company ticker symbol
        db: Database session
        current_user: Authenticated admin user

    Raises:
        HTTPException: If company not found
    """
    company = db.query(Company).filter(Company.ticker == ticker.upper()).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker {ticker} not found"
        )

    # Soft delete
    company.is_active = False
    db.commit()

    return None
