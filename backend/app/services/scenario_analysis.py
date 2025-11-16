"""
Scenario Analysis Service
Provides best/base/worst case analysis for valuation models
"""
from typing import Dict, List, Any, Optional
from app.services.dcf import DCFCalculator


class ScenarioAnalyzer:
    """
    Performs scenario analysis on valuation models
    """

    def __init__(self):
        self.dcf_calculator = DCFCalculator()

    def create_scenarios(
        self,
        base_params: Dict[str, Any],
        optimistic_adjustments: Dict[str, float] = None,
        pessimistic_adjustments: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Create best/base/worst case scenarios

        Args:
            base_params: Base case parameters
            optimistic_adjustments: % adjustments for optimistic case (e.g., {'revenue_growth': 0.20})
            pessimistic_adjustments: % adjustments for pessimistic case (e.g., {'revenue_growth': -0.20})

        Returns:
            Dictionary with all three scenarios
        """
        # Default adjustments if not provided
        if optimistic_adjustments is None:
            optimistic_adjustments = {
                'revenue_growth': 0.20,  # 20% higher
                'margin': 0.10,  # 10% higher
                'terminal_growth': 0.10,  # 10% higher
                'wacc': -0.05  # 5% lower (better)
            }

        if pessimistic_adjustments is None:
            pessimistic_adjustments = {
                'revenue_growth': -0.30,  # 30% lower
                'margin': -0.15,  # 15% lower
                'terminal_growth': -0.20,  # 20% lower
                'wacc': 0.10  # 10% higher (worse)
            }

        scenarios = {
            'base_case': base_params.copy(),
            'optimistic_case': self._apply_adjustments(base_params, optimistic_adjustments),
            'pessimistic_case': self._apply_adjustments(base_params, pessimistic_adjustments)
        }

        return scenarios

    def _apply_adjustments(
        self,
        base_params: Dict[str, Any],
        adjustments: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Apply percentage adjustments to base parameters

        Args:
            base_params: Base case parameters
            adjustments: Percentage adjustments to apply

        Returns:
            Adjusted parameters
        """
        adjusted = base_params.copy()

        # Adjust revenue growth rates
        if 'revenue_growth' in adjustments and 'revenue_growth_rates' in adjusted:
            growth_adjustment = adjustments['revenue_growth']
            adjusted['revenue_growth_rates'] = [
                rate * (1 + growth_adjustment) for rate in adjusted['revenue_growth_rates']
            ]

        # Adjust margin assumptions
        if 'margin' in adjustments and 'ebitda_margin' in adjusted:
            margin_adjustment = adjustments['margin']
            adjusted['ebitda_margin'] = adjusted['ebitda_margin'] * (1 + margin_adjustment)

        # Adjust WACC
        if 'wacc' in adjustments and 'wacc' in adjusted:
            wacc_adjustment = adjustments['wacc']
            adjusted['wacc'] = adjusted['wacc'] * (1 + wacc_adjustment)

        # Adjust terminal growth
        if 'terminal_growth' in adjustments and 'terminal_growth_rate' in adjusted:
            tg_adjustment = adjustments['terminal_growth']
            adjusted['terminal_growth_rate'] = adjusted['terminal_growth_rate'] * (1 + tg_adjustment)

        return adjusted

    def dcf_scenario_analysis(
        self,
        base_revenue: float,
        revenue_growth_rates: List[float],
        ebitda_margin: float,
        tax_rate: float,
        capex_percent: float,
        nwc_change_percent: float,
        wacc: float,
        terminal_growth_rate: float,
        shares_outstanding: float,
        net_debt: float = 0
    ) -> Dict[str, Any]:
        """
        Run DCF scenario analysis with best/base/worst cases

        Args:
            base_revenue: Starting revenue
            revenue_growth_rates: Base case growth rates
            ebitda_margin: Base case EBITDA margin
            tax_rate: Tax rate
            capex_percent: CapEx as % of revenue
            nwc_change_percent: NWC change as % of revenue
            wacc: Base case WACC
            terminal_growth_rate: Base case terminal growth
            shares_outstanding: Number of shares
            net_debt: Net debt

        Returns:
            Scenario analysis results with valuations
        """
        base_params = {
            'base_revenue': base_revenue,
            'revenue_growth_rates': revenue_growth_rates,
            'ebitda_margin': ebitda_margin,
            'tax_rate': tax_rate,
            'capex_percent': capex_percent,
            'nwc_change_percent': nwc_change_percent,
            'wacc': wacc,
            'terminal_growth_rate': terminal_growth_rate,
            'shares_outstanding': shares_outstanding,
            'net_debt': net_debt
        }

        scenarios = self.create_scenarios(base_params)
        results = {}

        for scenario_name, params in scenarios.items():
            # Calculate DCF for this scenario
            dcf_result = self.dcf_calculator.calculate_dcf(
                base_revenue=params['base_revenue'],
                revenue_growth_rates=params['revenue_growth_rates'],
                ebitda_margin=params['ebitda_margin'],
                tax_rate=params['tax_rate'],
                capex_percent=params['capex_percent'],
                nwc_change_percent=params['nwc_change_percent'],
                wacc=params['wacc'],
                terminal_growth_rate=params['terminal_growth_rate'],
                shares_outstanding=params['shares_outstanding'],
                net_debt=params['net_debt']
            )

            results[scenario_name] = {
                'parameters': params,
                'valuation': dcf_result
            }

        # Calculate scenario statistics
        base_value = results['base_case']['valuation']['equity_value_per_share']
        optimistic_value = results['optimistic_case']['valuation']['equity_value_per_share']
        pessimistic_value = results['pessimistic_case']['valuation']['equity_value_per_share']

        upside_potential = ((optimistic_value - base_value) / base_value) * 100 if base_value else 0
        downside_risk = ((base_value - pessimistic_value) / base_value) * 100 if base_value else 0
        value_range = optimistic_value - pessimistic_value

        return {
            'scenarios': results,
            'summary': {
                'base_value': round(base_value, 2),
                'optimistic_value': round(optimistic_value, 2),
                'pessimistic_value': round(pessimistic_value, 2),
                'upside_potential_percent': round(upside_potential, 2),
                'downside_risk_percent': round(downside_risk, 2),
                'value_range': round(value_range, 2),
                'risk_reward_ratio': round(upside_potential / downside_risk, 2) if downside_risk > 0 else None
            }
        }

    def sensitivity_matrix(
        self,
        base_revenue: float,
        revenue_growth_rates: List[float],
        ebitda_margin: float,
        tax_rate: float,
        capex_percent: float,
        nwc_change_percent: float,
        base_wacc: float,
        base_terminal_growth: float,
        shares_outstanding: float,
        net_debt: float,
        wacc_range: List[float] = None,
        terminal_growth_range: List[float] = None
    ) -> Dict[str, Any]:
        """
        Create 2D sensitivity matrix (WACC vs Terminal Growth)

        Args:
            base_revenue: Starting revenue
            revenue_growth_rates: Growth rates
            ebitda_margin: EBITDA margin
            tax_rate: Tax rate
            capex_percent: CapEx as % of revenue
            nwc_change_percent: NWC change as % of revenue
            base_wacc: Base WACC
            base_terminal_growth: Base terminal growth rate
            shares_outstanding: Number of shares
            net_debt: Net debt
            wacc_range: List of WACC values to test
            terminal_growth_range: List of terminal growth values to test

        Returns:
            2D sensitivity matrix
        """
        # Default ranges if not provided
        if wacc_range is None:
            wacc_range = [
                base_wacc - 0.02,
                base_wacc - 0.01,
                base_wacc,
                base_wacc + 0.01,
                base_wacc + 0.02
            ]

        if terminal_growth_range is None:
            terminal_growth_range = [
                base_terminal_growth - 0.02,
                base_terminal_growth - 0.01,
                base_terminal_growth,
                base_terminal_growth + 0.01,
                base_terminal_growth + 0.02
            ]

        # Build sensitivity matrix
        matrix = []

        for wacc in wacc_range:
            row = []
            for tg in terminal_growth_range:
                if wacc <= tg:
                    row.append(None)  # Invalid scenario
                    continue

                dcf_result = self.dcf_calculator.calculate_dcf(
                    base_revenue=base_revenue,
                    revenue_growth_rates=revenue_growth_rates,
                    ebitda_margin=ebitda_margin,
                    tax_rate=tax_rate,
                    capex_percent=capex_percent,
                    nwc_change_percent=nwc_change_percent,
                    wacc=wacc,
                    terminal_growth_rate=tg,
                    shares_outstanding=shares_outstanding,
                    net_debt=net_debt
                )

                row.append(round(dcf_result['equity_value_per_share'], 2))

            matrix.append(row)

        return {
            'wacc_range': [round(w * 100, 2) for w in wacc_range],
            'terminal_growth_range': [round(tg * 100, 2) for tg in terminal_growth_range],
            'matrix': matrix,
            'base_case_wacc': round(base_wacc * 100, 2),
            'base_case_terminal_growth': round(base_terminal_growth * 100, 2)
        }

    def what_if_analysis(
        self,
        base_params: Dict[str, Any],
        variable_to_test: str,
        test_values: List[float]
    ) -> Dict[str, Any]:
        """
        Test impact of changing a single variable

        Args:
            base_params: Base DCF parameters
            variable_to_test: Name of variable to test (e.g., 'wacc', 'ebitda_margin')
            test_values: Values to test for the variable

        Returns:
            What-if analysis results
        """
        results = []

        for test_value in test_values:
            params = base_params.copy()
            params[variable_to_test] = test_value

            dcf_result = self.dcf_calculator.calculate_dcf(**params)

            results.append({
                'variable_value': round(test_value, 4),
                'equity_value_per_share': round(dcf_result['equity_value_per_share'], 2)
            })

        return {
            'variable_tested': variable_to_test,
            'base_value': base_params.get(variable_to_test),
            'results': results
        }
