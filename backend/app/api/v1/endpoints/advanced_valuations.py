"""
Advanced Valuation Endpoints
Provides Monte Carlo, DDM, EVA, and Scenario Analysis endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.financial_statement import FinancialStatement
from app.services.monte_carlo import MonteCarloSimulator
from app.services.ddm import DividendDiscountModel
from app.services.eva import EVACalculator
from app.services.scenario_analysis import ScenarioAnalyzer

router = APIRouter()


# Pydantic models for request bodies
class MonteCarloRequest(BaseModel):
    base_revenue: float
    base_revenue_growth: float
    revenue_growth_volatility: float = 0.05
    base_ebitda_margin: float
    ebitda_margin_volatility: float = 0.02
    projection_years: int = 5
    base_wacc: float
    wacc_volatility: float = 0.01
    base_terminal_growth: float
    terminal_growth_volatility: float = 0.005
    capex_percent: float = 0.05
    nwc_change_percent: float = 0.02
    tax_rate: float = 0.25
    shares_outstanding: float
    num_simulations: int = 10000
    distribution: str = 'normal'


class GordonGrowthRequest(BaseModel):
    current_dividend: float
    growth_rate: float
    required_return: float


class TwoStageDDMRequest(BaseModel):
    current_dividend: float
    high_growth_rate: float
    high_growth_years: int
    stable_growth_rate: float
    required_return: float


class ThreeStageDDMRequest(BaseModel):
    current_dividend: float
    high_growth_rate: float
    high_growth_years: int
    transition_growth_rate: float
    transition_years: int
    stable_growth_rate: float
    required_return: float


class ScenarioAnalysisRequest(BaseModel):
    base_revenue: float
    revenue_growth_rates: List[float]
    ebitda_margin: float
    tax_rate: float
    capex_percent: float
    nwc_change_percent: float
    wacc: float
    terminal_growth_rate: float
    shares_outstanding: float
    net_debt: float = 0


@router.post("/monte-carlo")
def run_monte_carlo_simulation(
    request: MonteCarloRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Run Monte Carlo simulation on DCF valuation

    Returns probabilistic distribution of valuations
    """
    simulator = MonteCarloSimulator(num_simulations=request.num_simulations)

    results = simulator.run_simulation(
        base_revenue=request.base_revenue,
        base_revenue_growth=request.base_revenue_growth,
        revenue_growth_volatility=request.revenue_growth_volatility,
        base_ebitda_margin=request.base_ebitda_margin,
        ebitda_margin_volatility=request.ebitda_margin_volatility,
        projection_years=request.projection_years,
        base_wacc=request.base_wacc,
        wacc_volatility=request.wacc_volatility,
        base_terminal_growth=request.base_terminal_growth,
        terminal_growth_volatility=request.terminal_growth_volatility,
        capex_percent=request.capex_percent,
        nwc_change_percent=request.nwc_change_percent,
        tax_rate=request.tax_rate,
        shares_outstanding=request.shares_outstanding,
        distribution=request.distribution
    )

    return results


@router.post("/ddm/gordon-growth")
def calculate_gordon_growth(
    request: GordonGrowthRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate stock valuation using Gordon Growth Model
    """
    ddm = DividendDiscountModel()

    result = ddm.gordon_growth_model(
        current_dividend=request.current_dividend,
        growth_rate=request.growth_rate,
        required_return=request.required_return
    )

    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])

    return result


@router.post("/ddm/two-stage")
def calculate_two_stage_ddm(
    request: TwoStageDDMRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate stock valuation using Two-Stage DDM
    """
    ddm = DividendDiscountModel()

    result = ddm.two_stage_ddm(
        current_dividend=request.current_dividend,
        high_growth_rate=request.high_growth_rate,
        high_growth_years=request.high_growth_years,
        stable_growth_rate=request.stable_growth_rate,
        required_return=request.required_return
    )

    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])

    return result


@router.post("/ddm/three-stage")
def calculate_three_stage_ddm(
    request: ThreeStageDDMRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate stock valuation using Three-Stage DDM
    """
    ddm = DividendDiscountModel()

    result = ddm.three_stage_ddm(
        current_dividend=request.current_dividend,
        high_growth_rate=request.high_growth_rate,
        high_growth_years=request.high_growth_years,
        transition_growth_rate=request.transition_growth_rate,
        transition_years=request.transition_years,
        stable_growth_rate=request.stable_growth_rate,
        required_return=request.required_return
    )

    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])

    return result


@router.get("/{ticker}/eva")
def get_eva_analysis(
    ticker: str,
    wacc: float,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get Economic Value Added (EVA) analysis for a company

    Args:
        ticker: Company ticker symbol
        wacc: Weighted Average Cost of Capital
        limit: Number of periods to analyze

    Returns:
        Multi-period EVA analysis
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
        raise HTTPException(status_code=404, detail="Insufficient financial data for EVA analysis")

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

    # Calculate EVA
    eva_calculator = EVACalculator()

    # Assume average tax rate of 25% (can be improved by calculating from financials)
    tax_rate = 0.25

    analysis = eva_calculator.multi_period_eva_analysis(
        income_statements=income_dicts,
        balance_sheets=balance_dicts,
        wacc=wacc,
        tax_rate=tax_rate
    )

    return {
        'ticker': ticker,
        'wacc': wacc,
        'tax_rate': tax_rate,
        'eva_analysis': analysis
    }


@router.post("/scenario-analysis")
def run_scenario_analysis(
    request: ScenarioAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Run scenario analysis (best/base/worst case) on DCF model

    Returns valuations for all three scenarios
    """
    analyzer = ScenarioAnalyzer()

    results = analyzer.dcf_scenario_analysis(
        base_revenue=request.base_revenue,
        revenue_growth_rates=request.revenue_growth_rates,
        ebitda_margin=request.ebitda_margin,
        tax_rate=request.tax_rate,
        capex_percent=request.capex_percent,
        nwc_change_percent=request.nwc_change_percent,
        wacc=request.wacc,
        terminal_growth_rate=request.terminal_growth_rate,
        shares_outstanding=request.shares_outstanding,
        net_debt=request.net_debt
    )

    return results
