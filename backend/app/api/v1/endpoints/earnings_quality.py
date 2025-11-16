"""
Earnings Quality Analysis Endpoints
Provides Beneish M-Score, Altman Z-Score, and earnings quality metrics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.financial_statement import FinancialStatement
from app.services.beneish_mscore import BeneishMScoreCalculator
from app.services.altman_zscore import AltmanZScoreCalculator
from app.services.earnings_quality import EarningsQualityAnalyzer

router = APIRouter()


@router.get("/{ticker}/beneish-mscore")
def get_beneish_mscore(
    ticker: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate Beneish M-Score for earnings manipulation detection

    M-Score > -2.22 suggests possible earnings manipulation
    """
    # Fetch latest 2 annual income statements
    income_statements = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == 'income',
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(2)
        .all()
    )

    # Fetch latest 2 annual balance sheets
    balance_sheets = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == 'balance',
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(2)
        .all()
    )

    # Fetch latest 2 annual cash flow statements
    cashflow_statements = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == 'cashflow',
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(2)
        .all()
    )

    if len(income_statements) < 2 or len(balance_sheets) < 2 or len(cashflow_statements) < 2:
        raise HTTPException(
            status_code=404,
            detail="Insufficient data for Beneish M-Score calculation (need 2 years of data)"
        )

    # Prepare financial data with all statement types
    current_financials = {
        'period_end': str(income_statements[0].period_end),
        'fiscal_year': income_statements[0].fiscal_year,
        'data': income_statements[0].data,
        'balance_data': balance_sheets[0].data,
        'cashflow_data': cashflow_statements[0].data
    }

    prior_financials = {
        'period_end': str(income_statements[1].period_end),
        'fiscal_year': income_statements[1].fiscal_year,
        'data': income_statements[1].data,
        'balance_data': balance_sheets[1].data,
        'cashflow_data': cashflow_statements[1].data
    }

    # Calculate M-Score
    calculator = BeneishMScoreCalculator()
    result = calculator.calculate_mscore(current_financials, prior_financials)

    return {
        'ticker': ticker,
        'current_period': current_financials['period_end'],
        'prior_period': prior_financials['period_end'],
        **result
    }


@router.get("/{ticker}/altman-zscore")
def get_altman_zscore(
    ticker: str,
    market_cap: Optional[float] = None,
    company_type: str = 'public_manufacturing',
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate Altman Z-Score for bankruptcy prediction

    Args:
        ticker: Company ticker symbol
        market_cap: Market capitalization (required for public companies)
        company_type: 'public_manufacturing', 'private_manufacturing', or 'service'
        limit: Number of periods for trend analysis

    Z > 2.99: Safe zone
    1.81 < Z < 2.99: Grey zone
    Z < 1.81: Distress zone
    """
    # Fetch income statements
    income_statements = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == 'income',
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(limit)
        .all()
    )

    # Fetch balance sheets
    balance_sheets = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == 'balance',
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(limit)
        .all()
    )

    if not income_statements or not balance_sheets:
        raise HTTPException(status_code=404, detail="Insufficient financial data for Z-Score calculation")

    # Convert to dict format
    income_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in income_statements
    ]

    balance_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in balance_sheets
    ]

    # Calculate Z-Score
    calculator = AltmanZScoreCalculator()

    result = calculator.multi_period_zscore(
        income_statements=income_dicts,
        balance_sheets=balance_dicts,
        market_caps=None,  # Could be enhanced to accept historical market caps
        company_type=company_type
    )

    return {
        'ticker': ticker,
        'company_type': company_type,
        **result
    }


@router.get("/{ticker}/earnings-quality")
def get_earnings_quality(
    ticker: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Comprehensive earnings quality analysis

    Includes:
    - Accruals analysis
    - Cash flow quality
    - Revenue quality
    - Earnings persistence
    - Overall quality score
    """
    # Fetch income statements
    income_statements = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == 'income',
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(limit)
        .all()
    )

    # Fetch balance sheets
    balance_sheets = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == 'balance',
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(limit)
        .all()
    )

    # Fetch cash flow statements
    cashflow_statements = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == 'cashflow',
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(limit)
        .all()
    )

    if not income_statements or not cashflow_statements:
        raise HTTPException(
            status_code=404,
            detail="Insufficient data for earnings quality analysis"
        )

    # Convert to dict format
    income_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in income_statements
    ]

    balance_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in balance_sheets
    ]

    cashflow_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in cashflow_statements
    ]

    # Perform comprehensive analysis
    analyzer = EarningsQualityAnalyzer()

    result = analyzer.comprehensive_quality_analysis(
        income_statements=income_dicts,
        balance_sheets=balance_dicts,
        cashflow_statements=cashflow_dicts
    )

    return {
        'ticker': ticker,
        **result
    }


@router.get("/{ticker}/quality-dashboard")
def get_quality_dashboard(
    ticker: str,
    market_cap: Optional[float] = None,
    company_type: str = 'public_manufacturing',
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Complete earnings quality dashboard

    Combines Beneish M-Score, Altman Z-Score, and earnings quality metrics
    """
    # Get Beneish M-Score
    try:
        beneish_result = get_beneish_mscore(ticker, db, current_user)
    except HTTPException:
        beneish_result = {'error': 'Insufficient data for M-Score'}

    # Get Altman Z-Score
    try:
        altman_result = get_altman_zscore(ticker, market_cap, company_type, 5, db, current_user)
    except HTTPException:
        altman_result = {'error': 'Insufficient data for Z-Score'}

    # Get earnings quality
    try:
        quality_result = get_earnings_quality(ticker, 5, db, current_user)
    except HTTPException:
        quality_result = {'error': 'Insufficient data for quality analysis'}

    return {
        'ticker': ticker,
        'beneish_mscore': beneish_result,
        'altman_zscore': altman_result,
        'earnings_quality': quality_result
    }
