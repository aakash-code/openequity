"""
Monte Carlo Simulation Service
Provides probabilistic valuation analysis for DCF models
"""
import random
import statistics
from typing import Dict, List, Any, Optional
import numpy as np


class MonteCarloSimulator:
    """
    Runs Monte Carlo simulations on DCF models to provide probabilistic valuations
    """

    def __init__(self, num_simulations: int = 10000):
        """
        Initialize Monte Carlo simulator

        Args:
            num_simulations: Number of simulations to run (default: 10000)
        """
        self.num_simulations = num_simulations
        random.seed(42)  # For reproducibility
        np.random.seed(42)

    def generate_random_variable(
        self,
        base_value: float,
        volatility: float,
        distribution: str = 'normal'
    ) -> float:
        """
        Generate a random variable based on distribution

        Args:
            base_value: Expected/mean value
            volatility: Standard deviation or range
            distribution: Type of distribution ('normal', 'triangular', 'uniform')

        Returns:
            Random value from the specified distribution
        """
        if distribution == 'normal':
            return np.random.normal(base_value, volatility)
        elif distribution == 'triangular':
            # Triangular distribution with mode at base_value
            low = base_value - volatility
            high = base_value + volatility
            return np.random.triangular(low, base_value, high)
        elif distribution == 'uniform':
            low = base_value - volatility
            high = base_value + volatility
            return np.random.uniform(low, high)
        else:
            return base_value

    def calculate_dcf_value(
        self,
        base_revenue: float,
        revenue_growth_rates: List[float],
        ebitda_margins: List[float],
        capex_percent: float,
        nwc_change_percent: float,
        tax_rate: float,
        wacc: float,
        terminal_growth_rate: float,
        shares_outstanding: float
    ) -> float:
        """
        Calculate DCF valuation for a single simulation iteration

        Args:
            base_revenue: Starting revenue
            revenue_growth_rates: List of growth rates for each projection year
            ebitda_margins: List of EBITDA margins for each year
            capex_percent: CapEx as % of revenue
            nwc_change_percent: NWC change as % of revenue
            tax_rate: Effective tax rate
            wacc: Weighted average cost of capital
            terminal_growth_rate: Perpetual growth rate
            shares_outstanding: Number of shares

        Returns:
            Per-share valuation
        """
        fcf_projections = []
        revenue = base_revenue

        # Project free cash flows
        for i, growth in enumerate(revenue_growth_rates):
            revenue = revenue * (1 + growth)
            ebitda = revenue * ebitda_margins[i]

            # Approximate free cash flow
            depreciation = revenue * 0.05  # Assume 5% of revenue
            ebit = ebitda - depreciation
            nopat = ebit * (1 - tax_rate)

            # Add back depreciation, subtract CapEx and NWC changes
            capex = revenue * capex_percent
            nwc_change = revenue * nwc_change_percent

            fcf = nopat + depreciation - capex - nwc_change
            fcf_projections.append(fcf)

        # Calculate terminal value
        final_fcf = fcf_projections[-1]
        terminal_value = (final_fcf * (1 + terminal_growth_rate)) / (wacc - terminal_growth_rate)

        # Discount cash flows to present value
        present_values = []
        for i, fcf in enumerate(fcf_projections):
            pv = fcf / ((1 + wacc) ** (i + 1))
            present_values.append(pv)

        # Discount terminal value
        terminal_pv = terminal_value / ((1 + wacc) ** len(fcf_projections))

        # Calculate enterprise value and equity value per share
        enterprise_value = sum(present_values) + terminal_pv
        equity_value_per_share = enterprise_value / shares_outstanding

        return equity_value_per_share

    def run_simulation(
        self,
        base_revenue: float,
        base_revenue_growth: float,
        revenue_growth_volatility: float,
        base_ebitda_margin: float,
        ebitda_margin_volatility: float,
        projection_years: int,
        base_wacc: float,
        wacc_volatility: float,
        base_terminal_growth: float,
        terminal_growth_volatility: float,
        capex_percent: float = 0.05,
        nwc_change_percent: float = 0.02,
        tax_rate: float = 0.25,
        shares_outstanding: float = 1000000,
        distribution: str = 'normal'
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation on DCF model

        Args:
            base_revenue: Current/base year revenue
            base_revenue_growth: Expected revenue growth rate
            revenue_growth_volatility: Standard deviation of growth rate
            base_ebitda_margin: Expected EBITDA margin
            ebitda_margin_volatility: Standard deviation of margin
            projection_years: Number of years to project
            base_wacc: Expected WACC
            wacc_volatility: Standard deviation of WACC
            base_terminal_growth: Expected terminal growth rate
            terminal_growth_volatility: Standard deviation of terminal growth
            capex_percent: CapEx as % of revenue
            nwc_change_percent: NWC change as % of revenue
            tax_rate: Effective tax rate
            shares_outstanding: Number of shares outstanding
            distribution: Type of distribution for random variables

        Returns:
            Dictionary with simulation results and statistics
        """
        valuations = []

        for _ in range(self.num_simulations):
            # Generate random parameters for this iteration
            revenue_growth_rates = [
                self.generate_random_variable(
                    base_revenue_growth * (0.95 ** i),  # Declining growth over time
                    revenue_growth_volatility,
                    distribution
                )
                for i in range(projection_years)
            ]

            ebitda_margins = [
                self.generate_random_variable(
                    base_ebitda_margin,
                    ebitda_margin_volatility,
                    distribution
                )
                for _ in range(projection_years)
            ]

            wacc = self.generate_random_variable(
                base_wacc,
                wacc_volatility,
                distribution
            )

            terminal_growth = self.generate_random_variable(
                base_terminal_growth,
                terminal_growth_volatility,
                distribution
            )

            # Ensure WACC > terminal growth (required for DCF)
            if wacc <= terminal_growth:
                terminal_growth = wacc - 0.01

            # Ensure margins and rates are within reasonable bounds
            ebitda_margins = [max(0.01, min(0.99, margin)) for margin in ebitda_margins]
            revenue_growth_rates = [max(-0.50, min(2.0, rate)) for rate in revenue_growth_rates]
            wacc = max(0.01, min(0.50, wacc))
            terminal_growth = max(0.0, min(0.10, terminal_growth))

            # Calculate valuation for this iteration
            try:
                valuation = self.calculate_dcf_value(
                    base_revenue=base_revenue,
                    revenue_growth_rates=revenue_growth_rates,
                    ebitda_margins=ebitda_margins,
                    capex_percent=capex_percent,
                    nwc_change_percent=nwc_change_percent,
                    tax_rate=tax_rate,
                    wacc=wacc,
                    terminal_growth_rate=terminal_growth,
                    shares_outstanding=shares_outstanding
                )

                if valuation > 0 and not np.isnan(valuation) and not np.isinf(valuation):
                    valuations.append(valuation)
            except (ValueError, ZeroDivisionError):
                continue

        if not valuations:
            return {
                'error': 'No valid valuations generated',
                'num_simulations': 0
            }

        # Calculate statistics
        valuations_sorted = sorted(valuations)

        return {
            'num_simulations': len(valuations),
            'mean': round(statistics.mean(valuations), 2),
            'median': round(statistics.median(valuations), 2),
            'std_dev': round(statistics.stdev(valuations), 2),
            'min': round(min(valuations), 2),
            'max': round(max(valuations), 2),
            'percentiles': {
                'p10': round(valuations_sorted[int(len(valuations_sorted) * 0.10)], 2),
                'p25': round(valuations_sorted[int(len(valuations_sorted) * 0.25)], 2),
                'p50': round(valuations_sorted[int(len(valuations_sorted) * 0.50)], 2),
                'p75': round(valuations_sorted[int(len(valuations_sorted) * 0.75)], 2),
                'p90': round(valuations_sorted[int(len(valuations_sorted) * 0.90)], 2),
            },
            'distribution': self._create_histogram(valuations, bins=50),
            'probability_ranges': self._calculate_probability_ranges(valuations)
        }

    def _create_histogram(self, valuations: List[float], bins: int = 50) -> List[Dict[str, Any]]:
        """
        Create histogram data for visualization

        Args:
            valuations: List of valuation results
            bins: Number of histogram bins

        Returns:
            List of histogram bins with counts
        """
        hist, bin_edges = np.histogram(valuations, bins=bins)

        histogram_data = []
        for i in range(len(hist)):
            histogram_data.append({
                'range_start': round(bin_edges[i], 2),
                'range_end': round(bin_edges[i + 1], 2),
                'count': int(hist[i]),
                'frequency': round(hist[i] / len(valuations), 4)
            })

        return histogram_data

    def _calculate_probability_ranges(self, valuations: List[float]) -> Dict[str, Any]:
        """
        Calculate probability of different valuation ranges

        Args:
            valuations: List of valuation results

        Returns:
            Dictionary with probability ranges
        """
        mean_val = statistics.mean(valuations)

        # Calculate probabilities for different ranges relative to mean
        return {
            'above_mean': round(sum(1 for v in valuations if v > mean_val) / len(valuations), 4),
            'within_10_percent': round(
                sum(1 for v in valuations if abs(v - mean_val) / mean_val <= 0.10) / len(valuations), 4
            ),
            'within_25_percent': round(
                sum(1 for v in valuations if abs(v - mean_val) / mean_val <= 0.25) / len(valuations), 4
            ),
        }
