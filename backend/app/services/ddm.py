"""
Dividend Discount Model (DDM) Service
Provides multiple dividend-based valuation models
"""
from typing import Dict, List, Any, Optional


class DividendDiscountModel:
    """
    Calculates stock valuations using various dividend discount models
    """

    def gordon_growth_model(
        self,
        current_dividend: float,
        growth_rate: float,
        required_return: float
    ) -> Dict[str, Any]:
        """
        Calculate stock value using Gordon Growth Model (single-stage constant growth)
        Formula: Value = D1 / (r - g) where D1 = D0 * (1 + g)

        Args:
            current_dividend: Most recent annual dividend (D0)
            growth_rate: Perpetual dividend growth rate
            required_return: Required rate of return (cost of equity)

        Returns:
            Dictionary with valuation results
        """
        if required_return <= growth_rate:
            return {
                'error': 'Required return must be greater than growth rate',
                'value_per_share': None
            }

        if current_dividend <= 0:
            return {
                'error': 'Current dividend must be positive',
                'value_per_share': None
            }

        # Calculate next year's expected dividend
        next_dividend = current_dividend * (1 + growth_rate)

        # Calculate intrinsic value
        value_per_share = next_dividend / (required_return - growth_rate)

        return {
            'model': 'Gordon Growth Model',
            'current_dividend': round(current_dividend, 2),
            'next_dividend': round(next_dividend, 2),
            'growth_rate': round(growth_rate * 100, 2),
            'required_return': round(required_return * 100, 2),
            'value_per_share': round(value_per_share, 2),
            'dividend_yield': round((next_dividend / value_per_share) * 100, 2)
        }

    def two_stage_ddm(
        self,
        current_dividend: float,
        high_growth_rate: float,
        high_growth_years: int,
        stable_growth_rate: float,
        required_return: float
    ) -> Dict[str, Any]:
        """
        Calculate stock value using Two-Stage DDM
        Stage 1: High growth period
        Stage 2: Perpetual stable growth (Gordon Growth)

        Args:
            current_dividend: Most recent annual dividend
            high_growth_rate: Growth rate during high growth period
            high_growth_years: Number of years of high growth
            stable_growth_rate: Perpetual growth rate after high growth
            required_return: Required rate of return

        Returns:
            Dictionary with valuation results
        """
        if required_return <= stable_growth_rate:
            return {
                'error': 'Required return must be greater than stable growth rate',
                'value_per_share': None
            }

        if current_dividend <= 0:
            return {
                'error': 'Current dividend must be positive',
                'value_per_share': None
            }

        high_growth_pv = 0
        dividend = current_dividend
        dividends_projection = []

        # Stage 1: Present value of high growth dividends
        for year in range(1, high_growth_years + 1):
            dividend = dividend * (1 + high_growth_rate)
            pv = dividend / ((1 + required_return) ** year)
            high_growth_pv += pv

            dividends_projection.append({
                'year': year,
                'dividend': round(dividend, 2),
                'present_value': round(pv, 2),
                'stage': 'high_growth'
            })

        # Stage 2: Terminal value using Gordon Growth Model
        terminal_dividend = dividend * (1 + stable_growth_rate)
        terminal_value = terminal_dividend / (required_return - stable_growth_rate)
        terminal_pv = terminal_value / ((1 + required_return) ** high_growth_years)

        # Total value
        value_per_share = high_growth_pv + terminal_pv

        return {
            'model': 'Two-Stage DDM',
            'current_dividend': round(current_dividend, 2),
            'high_growth_rate': round(high_growth_rate * 100, 2),
            'high_growth_years': high_growth_years,
            'stable_growth_rate': round(stable_growth_rate * 100, 2),
            'required_return': round(required_return * 100, 2),
            'high_growth_pv': round(high_growth_pv, 2),
            'terminal_value': round(terminal_value, 2),
            'terminal_pv': round(terminal_pv, 2),
            'value_per_share': round(value_per_share, 2),
            'dividends_projection': dividends_projection
        }

    def three_stage_ddm(
        self,
        current_dividend: float,
        high_growth_rate: float,
        high_growth_years: int,
        transition_growth_rate: float,
        transition_years: int,
        stable_growth_rate: float,
        required_return: float
    ) -> Dict[str, Any]:
        """
        Calculate stock value using Three-Stage DDM
        Stage 1: High growth period
        Stage 2: Transition period with declining growth
        Stage 3: Perpetual stable growth

        Args:
            current_dividend: Most recent annual dividend
            high_growth_rate: Growth rate during high growth period
            high_growth_years: Number of years of high growth
            transition_growth_rate: Average growth rate during transition
            transition_years: Number of transition years
            stable_growth_rate: Perpetual growth rate
            required_return: Required rate of return

        Returns:
            Dictionary with valuation results
        """
        if required_return <= stable_growth_rate:
            return {
                'error': 'Required return must be greater than stable growth rate',
                'value_per_share': None
            }

        if current_dividend <= 0:
            return {
                'error': 'Current dividend must be positive',
                'value_per_share': None
            }

        total_pv = 0
        dividend = current_dividend
        dividends_projection = []
        year_counter = 0

        # Stage 1: High growth period
        for year in range(1, high_growth_years + 1):
            dividend = dividend * (1 + high_growth_rate)
            year_counter += 1
            pv = dividend / ((1 + required_return) ** year_counter)
            total_pv += pv

            dividends_projection.append({
                'year': year_counter,
                'dividend': round(dividend, 2),
                'growth_rate': round(high_growth_rate * 100, 2),
                'present_value': round(pv, 2),
                'stage': 'high_growth'
            })

        # Stage 2: Transition period with linearly declining growth
        growth_decline_per_year = (high_growth_rate - stable_growth_rate) / (transition_years + 1)

        for year in range(1, transition_years + 1):
            growth_rate = high_growth_rate - (growth_decline_per_year * year)
            dividend = dividend * (1 + growth_rate)
            year_counter += 1
            pv = dividend / ((1 + required_return) ** year_counter)
            total_pv += pv

            dividends_projection.append({
                'year': year_counter,
                'dividend': round(dividend, 2),
                'growth_rate': round(growth_rate * 100, 2),
                'present_value': round(pv, 2),
                'stage': 'transition'
            })

        # Stage 3: Terminal value using Gordon Growth Model
        terminal_dividend = dividend * (1 + stable_growth_rate)
        terminal_value = terminal_dividend / (required_return - stable_growth_rate)
        terminal_pv = terminal_value / ((1 + required_return) ** year_counter)
        total_pv += terminal_pv

        return {
            'model': 'Three-Stage DDM',
            'current_dividend': round(current_dividend, 2),
            'high_growth_rate': round(high_growth_rate * 100, 2),
            'high_growth_years': high_growth_years,
            'transition_growth_rate': round(transition_growth_rate * 100, 2),
            'transition_years': transition_years,
            'stable_growth_rate': round(stable_growth_rate * 100, 2),
            'required_return': round(required_return * 100, 2),
            'terminal_value': round(terminal_value, 2),
            'terminal_pv': round(terminal_pv, 2),
            'value_per_share': round(total_pv, 2),
            'dividends_projection': dividends_projection
        }

    def calculate_required_return_capm(
        self,
        risk_free_rate: float,
        beta: float,
        market_return: float
    ) -> float:
        """
        Calculate required return using Capital Asset Pricing Model (CAPM)
        Formula: r = rf + β(rm - rf)

        Args:
            risk_free_rate: Risk-free rate (e.g., 10-year treasury)
            beta: Stock's beta
            market_return: Expected market return

        Returns:
            Required return (cost of equity)
        """
        required_return = risk_free_rate + beta * (market_return - risk_free_rate)
        return required_return

    def dividend_payout_analysis(
        self,
        net_income: float,
        dividends_paid: float,
        shares_outstanding: float
    ) -> Dict[str, Any]:
        """
        Analyze dividend metrics

        Args:
            net_income: Annual net income
            dividends_paid: Total annual dividends paid
            shares_outstanding: Number of shares outstanding

        Returns:
            Dictionary with dividend metrics
        """
        if shares_outstanding <= 0:
            return {'error': 'Shares outstanding must be positive'}

        eps = net_income / shares_outstanding
        dps = dividends_paid / shares_outstanding
        payout_ratio = (dividends_paid / net_income) if net_income > 0 else 0
        retention_ratio = 1 - payout_ratio

        return {
            'earnings_per_share': round(eps, 2),
            'dividend_per_share': round(dps, 2),
            'payout_ratio': round(payout_ratio * 100, 2),
            'retention_ratio': round(retention_ratio * 100, 2),
            'dividends_paid': round(dividends_paid, 2),
            'net_income': round(net_income, 2)
        }
