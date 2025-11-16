"""
Financial statements and ratios endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db, get_current_user
from app.models.company import Company
from app.models.financial_statement import FinancialStatement, StatementType
from app.models.user import User
from app.services.financial_data import FinancialDataService
from app.services.ratios import FinancialRatiosCalculator
from app.schemas.financial import (
    FinancialStatementResponse,
    FinancialRatiosResponse,
    RefreshFinancialsRequest,
)

router = APIRouter()


@router.get("/{ticker}/statements", response_model=List[FinancialStatementResponse])
def get_financial_statements(
    ticker: str,
    statement_type: Optional[StatementType] = None,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get financial statements for a company

    Args:
        ticker: Company ticker symbol
        statement_type: Filter by statement type (income, balance, cashflow)
        limit: Number of periods to return
        db: Database session
        current_user: Authenticated user

    Returns:
        List of financial statements
    """
    # Verify company exists
    company = db.query(Company).filter(
        Company.ticker == ticker.upper(), Company.is_active == True
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company {ticker} not found",
        )

    # Query financial statements
    query = db.query(FinancialStatement).filter(
        FinancialStatement.ticker == ticker.upper()
    )

    if statement_type:
        query = query.filter(FinancialStatement.statement_type == statement_type)

    statements = query.order_by(FinancialStatement.period_end.desc()).limit(limit).all()

    return statements


@router.get("/{ticker}/ratios", response_model=FinancialRatiosResponse)
def get_financial_ratios(
    ticker: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate and return financial ratios for a company

    Args:
        ticker: Company ticker symbol
        db: Database session
        current_user: Authenticated user

    Returns:
        Calculated financial ratios
    """
    # Verify company exists
    company = db.query(Company).filter(
        Company.ticker == ticker.upper(), Company.is_active == True
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company {ticker} not found",
        )

    # Get latest statements
    latest_income = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker.upper(),
            FinancialStatement.statement_type == StatementType.INCOME,
        )
        .order_by(FinancialStatement.period_end.desc())
        .first()
    )

    latest_balance = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker.upper(),
            FinancialStatement.statement_type == StatementType.BALANCE,
        )
        .order_by(FinancialStatement.period_end.desc())
        .first()
    )

    latest_cashflow = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker.upper(),
            FinancialStatement.statement_type == StatementType.CASHFLOW,
        )
        .order_by(FinancialStatement.period_end.desc())
        .first()
    )

    if not latest_income or not latest_balance or not latest_cashflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Financial statements not found for {ticker}. Try refreshing data first.",
        )

    # Calculate ratios
    calculator = FinancialRatiosCalculator()

    # Add market data if available
    market_data = {
        "market_cap": company.market_cap,
        "stock_price": 0,  # TODO: Get from price API
        "shares_outstanding": 0,  # TODO: Calculate or get from API
    }

    ratios = calculator.calculate_all_ratios(
        income_statement=latest_income.data,
        balance_sheet=latest_balance.data,
        cashflow_statement=latest_cashflow.data,
        market_data=market_data if company.market_cap else None,
    )

    # Add DuPont analysis
    ratios["dupont"] = calculator.calculate_dupont_analysis(
        latest_income.data, latest_balance.data
    )

    return {
        "ticker": ticker,
        "period_end": latest_income.period_end.isoformat(),
        "ratios": ratios,
    }


@router.post("/{ticker}/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_financial_data(
    ticker: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Refresh financial data for a company from external sources

    Args:
        ticker: Company ticker symbol
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user

    Returns:
        Status message
    """
    # Verify company exists
    company = db.query(Company).filter(
        Company.ticker == ticker.upper(), Company.is_active == True
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company {ticker} not found",
        )

    # Determine market based on exchange
    market = "US"
    if company.exchange in ["NSE", "BSE"]:
        market = company.exchange

    # Add background task to fetch and store data
    background_tasks.add_task(
        fetch_and_store_financials, ticker.upper(), market, db
    )

    return {
        "message": f"Financial data refresh initiated for {ticker}",
        "status": "processing",
    }


async def fetch_and_store_financials(ticker: str, market: str, db: Session):
    """Background task to fetch and store financial data"""
    try:
        service = FinancialDataService(db)

        # Fetch data
        financial_data = await service.fetch_financials(ticker, market)

        # Store data
        if financial_data:
            await service.store_financials(ticker, financial_data)
            print(f"Successfully refreshed financials for {ticker}")
        else:
            print(f"No financial data found for {ticker}")

    except Exception as e:
        print(f"Error refreshing financials for {ticker}: {e}")
