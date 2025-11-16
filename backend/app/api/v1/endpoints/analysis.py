"""
Enhanced Financial Analysis Endpoints
Provides common-size statements and trend analysis
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.financial_statement import FinancialStatement
from app.services.common_size import CommonSizeCalculator
from app.services.trend_analyzer import TrendAnalyzer

router = APIRouter()
common_size_calculator = CommonSizeCalculator()
trend_analyzer = TrendAnalyzer()


@router.get("/{ticker}/common-size/{statement_type}")
def get_common_size_statements(
    ticker: str,
    statement_type: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get common-size financial statements for a company

    Args:
        ticker: Company ticker symbol
        statement_type: Type of statement ('income', 'balance', 'cashflow')
        limit: Number of periods to retrieve

    Returns:
        Common-size statements with period information
    """
    if statement_type not in ['income', 'balance', 'cashflow']:
        raise HTTPException(status_code=400, detail="Invalid statement type")

    # Fetch financial statements
    statements = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.ticker == ticker,
            FinancialStatement.statement_type == statement_type,
            FinancialStatement.period_type == 'annual'
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(limit)
        .all()
    )

    if not statements:
        raise HTTPException(status_code=404, detail="No financial statements found")

    # Convert to dict format for calculator
    statement_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in statements
    ]

    # Calculate common-size statements
    common_size_results = common_size_calculator.calculate_multi_period_common_size(
        statement_dicts, statement_type
    )

    return {
        'ticker': ticker,
        'statement_type': statement_type,
        'periods': common_size_results
    }


@router.get("/{ticker}/trends")
def get_trend_analysis(
    ticker: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get comprehensive trend analysis for a company

    Args:
        ticker: Company ticker symbol
        limit: Number of periods to analyze

    Returns:
        Comprehensive trend analysis including revenue, profitability, balance sheet, and cash flow trends
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

    if not income_statements and not balance_sheets and not cashflow_statements:
        raise HTTPException(status_code=404, detail="No financial data found for this company")

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

    # Generate comprehensive analysis
    analysis = trend_analyzer.generate_comprehensive_analysis(
        income_dicts, balance_dicts, cashflow_dicts
    )

    return {
        'ticker': ticker,
        'analysis': analysis
    }


@router.get("/{ticker}/revenue-trend")
def get_revenue_trend(
    ticker: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get revenue trend analysis for a company

    Args:
        ticker: Company ticker symbol
        limit: Number of periods to analyze

    Returns:
        Revenue trend with YoY growth and CAGR
    """
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

    if not income_statements:
        raise HTTPException(status_code=404, detail="No income statements found")

    income_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in income_statements
    ]

    revenue_trend = trend_analyzer.analyze_revenue_trend(income_dicts)

    return {
        'ticker': ticker,
        'revenue_trend': revenue_trend
    }


@router.get("/{ticker}/profitability-trend")
def get_profitability_trend(
    ticker: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get profitability margin trends for a company

    Args:
        ticker: Company ticker symbol
        limit: Number of periods to analyze

    Returns:
        Profitability trends (gross, operating, net margins)
    """
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

    if not income_statements:
        raise HTTPException(status_code=404, detail="No income statements found")

    income_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in income_statements
    ]

    profitability_trend = trend_analyzer.analyze_profitability_trend(income_dicts)

    return {
        'ticker': ticker,
        'profitability_trend': profitability_trend
    }


@router.get("/{ticker}/balance-sheet-trend")
def get_balance_sheet_trend(
    ticker: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get balance sheet trends for a company

    Args:
        ticker: Company ticker symbol
        limit: Number of periods to analyze

    Returns:
        Balance sheet trends (assets, liabilities, equity)
    """
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

    if not balance_sheets:
        raise HTTPException(status_code=404, detail="No balance sheets found")

    balance_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in balance_sheets
    ]

    balance_trend = trend_analyzer.analyze_balance_sheet_trend(balance_dicts)

    return {
        'ticker': ticker,
        'balance_sheet_trend': balance_trend
    }


@router.get("/{ticker}/cashflow-trend")
def get_cashflow_trend(
    ticker: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get cash flow trends for a company

    Args:
        ticker: Company ticker symbol
        limit: Number of periods to analyze

    Returns:
        Cash flow trends (operating, investing, financing, free cash flow)
    """
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

    if not cashflow_statements:
        raise HTTPException(status_code=404, detail="No cash flow statements found")

    cashflow_dicts = [
        {
            'period_end': str(stmt.period_end),
            'fiscal_year': stmt.fiscal_year,
            'data': stmt.data
        }
        for stmt in cashflow_statements
    ]

    cashflow_trend = trend_analyzer.analyze_cashflow_trend(cashflow_dicts)

    return {
        'ticker': ticker,
        'cashflow_trend': cashflow_trend
    }
