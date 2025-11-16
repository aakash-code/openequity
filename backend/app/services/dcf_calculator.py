"""
DCF Calculator Service
Handles DCF valuation calculations including WACC, projections, and terminal value
"""
from typing import Dict, List, Optional, Tuple
import numpy as np


class WACCCalculator:
    """
    Weighted Average Cost of Capital (WACC) calculator
    WACC = (E/V * Re) + (D/V * Rd * (1 - Tc))
    where:
    - E = Market value of equity
    - D = Market value of debt
    - V = E + D (Total firm value)
    - Re = Cost of equity (using CAPM)
    - Rd = Cost of debt
    - Tc = Corporate tax rate
    """

    @staticmethod
    def calculate_cost_of_equity(
        risk_free_rate: float, beta: float, equity_risk_premium: float
    ) -> float:
        """
        Calculate cost of equity using CAPM
        Re = Rf + β * (Rm - Rf)

        Args:
            risk_free_rate: Risk-free rate (e.g., 10-year Treasury yield)
            beta: Stock's beta
            equity_risk_premium: Expected market return - risk-free rate

        Returns:
            Cost of equity as decimal (e.g., 0.12 for 12%)
        """
        return risk_free_rate + (beta * equity_risk_premium)

    @staticmethod
    def calculate_wacc(
        equity_weight: float,
        debt_weight: float,
        cost_of_equity: float,
        cost_of_debt: float,
        tax_rate: float,
    ) -> float:
        """
        Calculate WACC

        Args:
            equity_weight: Weight of equity (E/V)
            debt_weight: Weight of debt (D/V)
            cost_of_equity: Cost of equity
            cost_of_debt: Cost of debt
            tax_rate: Corporate tax rate

        Returns:
            WACC as decimal
        """
        return (equity_weight * cost_of_equity) + (
            debt_weight * cost_of_debt * (1 - tax_rate)
        )

    @staticmethod
    def calculate_full_wacc(
        risk_free_rate: float,
        beta: float,
        equity_risk_premium: float,
        cost_of_debt: float,
        tax_rate: float,
        equity_weight: float,
        debt_weight: float,
    ) -> Tuple[float, float]:
        """
        Calculate WACC with all components

        Returns:
            Tuple of (cost_of_equity, wacc)
        """
        cost_of_equity = WACCCalculator.calculate_cost_of_equity(
            risk_free_rate, beta, equity_risk_premium
        )
        wacc = WACCCalculator.calculate_wacc(
            equity_weight, debt_weight, cost_of_equity, cost_of_debt, tax_rate
        )
        return cost_of_equity, wacc


class DCFCalculator:
    """
    Discounted Cash Flow (DCF) calculator for equity valuation
    """

    def __init__(self):
        self.wacc_calculator = WACCCalculator()

    def project_revenue(
        self, base_revenue: float, growth_rates: List[float]
    ) -> List[float]:
        """
        Project revenue based on growth rates

        Args:
            base_revenue: Current year revenue
            growth_rates: List of annual growth rates

        Returns:
            List of projected revenues
        """
        revenues = [base_revenue]
        for growth_rate in growth_rates:
            next_revenue = revenues[-1] * (1 + growth_rate)
            revenues.append(next_revenue)
        return revenues[1:]  # Return projected years only

    def calculate_free_cash_flow(
        self,
        revenue: float,
        ebitda_margin: float,
        depreciation_pct: float,
        tax_rate: float,
        capex_pct: float,
        nwc_change_pct: float,
    ) -> float:
        """
        Calculate unlevered free cash flow (UFCF)
        FCF = EBITDA - D&A - Taxes on EBIT + D&A - CapEx - Change in NWC
            = EBIT(1-T) + D&A - CapEx - Change in NWC

        Args:
            revenue: Revenue for the period
            ebitda_margin: EBITDA as % of revenue
            depreciation_pct: D&A as % of revenue
            tax_rate: Tax rate
            capex_pct: CapEx as % of revenue
            nwc_change_pct: Change in NWC as % of revenue

        Returns:
            Free cash flow
        """
        ebitda = revenue * ebitda_margin
        depreciation = revenue * depreciation_pct
        ebit = ebitda - depreciation
        nopat = ebit * (1 - tax_rate)  # Net Operating Profit After Tax
        fcf = nopat + depreciation - (revenue * capex_pct) - (revenue * nwc_change_pct)
        return fcf

    def calculate_terminal_value_growth(
        self, final_year_fcf: float, terminal_growth_rate: float, wacc: float
    ) -> float:
        """
        Calculate terminal value using Gordon Growth Model
        TV = FCF(n+1) / (WACC - g)
           = FCF(n) * (1 + g) / (WACC - g)

        Args:
            final_year_fcf: Free cash flow in final projection year
            terminal_growth_rate: Perpetual growth rate
            wacc: Weighted average cost of capital

        Returns:
            Terminal value
        """
        if wacc <= terminal_growth_rate:
            raise ValueError(
                "WACC must be greater than terminal growth rate for Gordon Growth Model"
            )
        return (final_year_fcf * (1 + terminal_growth_rate)) / (
            wacc - terminal_growth_rate
        )

    def calculate_terminal_value_multiple(
        self, final_year_ebitda: float, exit_multiple: float
    ) -> float:
        """
        Calculate terminal value using exit multiple approach
        TV = EBITDA(final year) * Exit Multiple

        Args:
            final_year_ebitda: EBITDA in final projection year
            exit_multiple: EV/EBITDA exit multiple

        Returns:
            Terminal value
        """
        return final_year_ebitda * exit_multiple

    def discount_cash_flows(
        self, cash_flows: List[float], wacc: float
    ) -> Tuple[List[float], float]:
        """
        Discount cash flows to present value
        PV = CF / (1 + WACC)^t

        Args:
            cash_flows: List of future cash flows
            wacc: Discount rate

        Returns:
            Tuple of (list of PV for each year, sum of PVs)
        """
        present_values = []
        for year, cf in enumerate(cash_flows, start=1):
            pv = cf / ((1 + wacc) ** year)
            present_values.append(pv)
        return present_values, sum(present_values)

    def calculate_dcf_valuation(
        self,
        base_revenue: float,
        revenue_growth_rates: List[float],
        ebitda_margin: float,
        depreciation_pct_revenue: float,
        capex_pct_revenue: float,
        nwc_pct_revenue: float,
        tax_rate: float,
        wacc: float,
        terminal_growth_rate: Optional[float] = None,
        terminal_ebitda_multiple: Optional[float] = None,
        net_debt: float = 0,
        shares_outstanding: float = 1,
        current_price: Optional[float] = None,
    ) -> Dict:
        """
        Perform complete DCF valuation

        Args:
            base_revenue: Current revenue
            revenue_growth_rates: List of growth rates for projection period
            ebitda_margin: Target EBITDA margin
            depreciation_pct_revenue: D&A as % of revenue
            capex_pct_revenue: CapEx as % of revenue
            nwc_pct_revenue: Change in NWC as % of revenue
            tax_rate: Corporate tax rate
            wacc: Weighted average cost of capital
            terminal_growth_rate: Perpetual growth rate (for Gordon Growth)
            terminal_ebitda_multiple: Exit multiple (alternative to growth)
            net_debt: Net debt (Total Debt - Cash)
            shares_outstanding: Number of shares outstanding
            current_price: Current stock price for upside/downside calculation

        Returns:
            Dictionary containing complete DCF results
        """
        # Project revenues
        projected_revenues = self.project_revenue(base_revenue, revenue_growth_rates)

        # Calculate FCFs for each year
        fcf_projections = []
        ebitda_projections = []
        for revenue in projected_revenues:
            fcf = self.calculate_free_cash_flow(
                revenue,
                ebitda_margin,
                depreciation_pct_revenue,
                tax_rate,
                capex_pct_revenue,
                nwc_pct_revenue,
            )
            fcf_projections.append(fcf)
            ebitda_projections.append(revenue * ebitda_margin)

        # Calculate terminal value
        if terminal_growth_rate is not None:
            terminal_value = self.calculate_terminal_value_growth(
                fcf_projections[-1], terminal_growth_rate, wacc
            )
            terminal_method = "Gordon Growth"
        elif terminal_ebitda_multiple is not None:
            terminal_value = self.calculate_terminal_value_multiple(
                ebitda_projections[-1], terminal_ebitda_multiple
            )
            terminal_method = "Exit Multiple"
        else:
            raise ValueError(
                "Must provide either terminal_growth_rate or terminal_ebitda_multiple"
            )

        # Discount FCFs
        pv_fcfs, pv_fcf_sum = self.discount_cash_flows(fcf_projections, wacc)

        # Discount terminal value
        terminal_year = len(fcf_projections)
        pv_terminal_value = terminal_value / ((1 + wacc) ** terminal_year)

        # Calculate enterprise value and equity value
        enterprise_value = pv_fcf_sum + pv_terminal_value
        equity_value = enterprise_value - net_debt

        # Calculate per-share value
        value_per_share = equity_value / shares_outstanding

        # Calculate upside/downside
        upside_downside = None
        if current_price:
            upside_downside = ((value_per_share - current_price) / current_price) * 100

        return {
            "projections": {
                "revenues": projected_revenues,
                "ebitda": ebitda_projections,
                "fcf": fcf_projections,
            },
            "pv_fcf": {
                "yearly": pv_fcfs,
                "total": pv_fcf_sum,
            },
            "terminal_value": {
                "value": terminal_value,
                "pv": pv_terminal_value,
                "method": terminal_method,
            },
            "valuation": {
                "enterprise_value": enterprise_value,
                "equity_value": equity_value,
                "value_per_share": value_per_share,
                "current_price": current_price,
                "upside_downside_pct": upside_downside,
            },
        }

    def generate_sensitivity_analysis(
        self,
        base_revenue: float,
        revenue_growth_rates: List[float],
        ebitda_margin: float,
        depreciation_pct_revenue: float,
        capex_pct_revenue: float,
        nwc_pct_revenue: float,
        tax_rate: float,
        base_wacc: float,
        base_terminal_growth: float,
        net_debt: float,
        shares_outstanding: float,
        wacc_range: List[float] = None,
        terminal_growth_range: List[float] = None,
    ) -> Dict:
        """
        Generate sensitivity analysis grid
        Varies WACC and terminal growth rate to show impact on valuation

        Returns:
            Dictionary with sensitivity grid
        """
        if wacc_range is None:
            # Default: +/- 1% from base WACC in 0.25% increments
            wacc_range = [
                base_wacc - 0.02,
                base_wacc - 0.01,
                base_wacc,
                base_wacc + 0.01,
                base_wacc + 0.02,
            ]

        if terminal_growth_range is None:
            # Default: +/- 1% from base terminal growth in 0.25% increments
            terminal_growth_range = [
                base_terminal_growth - 0.02,
                base_terminal_growth - 0.01,
                base_terminal_growth,
                base_terminal_growth + 0.01,
                base_terminal_growth + 0.02,
            ]

        sensitivity_grid = []
        for tg in terminal_growth_range:
            row = []
            for wacc in wacc_range:
                try:
                    result = self.calculate_dcf_valuation(
                        base_revenue=base_revenue,
                        revenue_growth_rates=revenue_growth_rates,
                        ebitda_margin=ebitda_margin,
                        depreciation_pct_revenue=depreciation_pct_revenue,
                        capex_pct_revenue=capex_pct_revenue,
                        nwc_pct_revenue=nwc_pct_revenue,
                        tax_rate=tax_rate,
                        wacc=wacc,
                        terminal_growth_rate=tg,
                        net_debt=net_debt,
                        shares_outstanding=shares_outstanding,
                    )
                    value_per_share = result["valuation"]["value_per_share"]
                except (ValueError, ZeroDivisionError):
                    value_per_share = None
                row.append(value_per_share)
            sensitivity_grid.append(row)

        return {
            "wacc_range": wacc_range,
            "terminal_growth_range": terminal_growth_range,
            "grid": sensitivity_grid,
        }
