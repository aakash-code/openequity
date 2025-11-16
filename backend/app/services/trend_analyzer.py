"""
Trend Analysis Service
Calculates growth rates, trends, and historical analysis
"""
from typing import Dict, List, Any, Optional
import statistics


class TrendAnalyzer:
    """
    Analyzes financial trends and calculates growth metrics
    """

    def calculate_growth_rate(self, current: float, previous: float) -> Optional[float]:
        """
        Calculate year-over-year growth rate

        Args:
            current: Current period value
            previous: Previous period value

        Returns:
            Growth rate as percentage (e.g., 15.5 for 15.5% growth)
        """
        if not previous or previous == 0:
            return None

        growth = ((current - previous) / abs(previous)) * 100
        return round(growth, 2)

    def calculate_cagr(self, beginning_value: float, ending_value: float, num_years: int) -> Optional[float]:
        """
        Calculate Compound Annual Growth Rate

        Args:
            beginning_value: Starting value
            ending_value: Ending value
            num_years: Number of years

        Returns:
            CAGR as percentage
        """
        if not beginning_value or beginning_value == 0 or num_years <= 0:
            return None

        try:
            cagr = (((ending_value / beginning_value) ** (1 / num_years)) - 1) * 100
            return round(cagr, 2)
        except (ValueError, ZeroDivisionError):
            return None

    def analyze_revenue_trend(self, income_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze revenue trends over multiple periods

        Args:
            income_statements: List of income statements (newest first)

        Returns:
            Revenue trend analysis
        """
        if not income_statements or len(income_statements) < 2:
            return {}

        # Sort by period_end (oldest first for trend analysis)
        sorted_statements = sorted(income_statements, key=lambda x: x.get('period_end', ''))

        revenues = []
        periods = []

        for statement in sorted_statements:
            revenue = statement.get('data', {}).get('total_revenue', 0) or statement.get('data', {}).get('revenue', 0)
            if revenue:
                revenues.append(revenue)
                periods.append(statement.get('period_end'))

        if len(revenues) < 2:
            return {}

        # Calculate YoY growth rates
        yoy_growth = []
        for i in range(1, len(revenues)):
            growth = self.calculate_growth_rate(revenues[i], revenues[i-1])
            if growth is not None:
                yoy_growth.append({
                    'period': periods[i],
                    'growth_rate': growth,
                    'revenue': revenues[i]
                })

        # Calculate CAGR if we have multiple years
        cagr = None
        if len(revenues) >= 2:
            num_years = len(revenues) - 1
            cagr = self.calculate_cagr(revenues[0], revenues[-1], num_years)

        # Calculate average growth rate
        avg_growth = None
        if yoy_growth:
            growth_rates = [g['growth_rate'] for g in yoy_growth]
            avg_growth = round(statistics.mean(growth_rates), 2)

        return {
            'current_revenue': revenues[-1] if revenues else None,
            'previous_revenue': revenues[-2] if len(revenues) >= 2 else None,
            'latest_growth': yoy_growth[-1]['growth_rate'] if yoy_growth else None,
            'yoy_growth': yoy_growth,
            'cagr': cagr,
            'average_growth': avg_growth,
            'periods': periods,
            'revenues': revenues
        }

    def analyze_profitability_trend(self, income_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze profitability metrics trends

        Args:
            income_statements: List of income statements

        Returns:
            Profitability trend analysis
        """
        if not income_statements or len(income_statements) < 2:
            return {}

        sorted_statements = sorted(income_statements, key=lambda x: x.get('period_end', ''))

        margins = {
            'gross_margin': [],
            'operating_margin': [],
            'net_margin': []
        }
        periods = []

        for statement in sorted_statements:
            data = statement.get('data', {})
            revenue = data.get('total_revenue', 0) or data.get('revenue', 0)

            if revenue and revenue != 0:
                # Gross margin
                gross_profit = data.get('gross_profit', 0)
                if gross_profit:
                    margins['gross_margin'].append((gross_profit / revenue) * 100)
                else:
                    margins['gross_margin'].append(None)

                # Operating margin
                operating_income = data.get('operating_income', 0)
                if operating_income:
                    margins['operating_margin'].append((operating_income / revenue) * 100)
                else:
                    margins['operating_margin'].append(None)

                # Net margin
                net_income = data.get('net_income', 0)
                if net_income:
                    margins['net_margin'].append((net_income / revenue) * 100)
                else:
                    margins['net_margin'].append(None)

                periods.append(statement.get('period_end'))

        # Calculate margin trends (improvement/decline)
        margin_trends = {}
        for margin_type, values in margins.items():
            non_null_values = [v for v in values if v is not None]
            if len(non_null_values) >= 2:
                latest = non_null_values[-1]
                previous = non_null_values[-2]
                change = round(latest - previous, 2)
                margin_trends[margin_type] = {
                    'current': round(latest, 2),
                    'previous': round(previous, 2),
                    'change': change,
                    'trend': 'improving' if change > 0 else 'declining' if change < 0 else 'stable',
                    'historical': [round(v, 2) if v is not None else None for v in values]
                }

        return {
            'periods': periods,
            'margins': margin_trends
        }

    def analyze_balance_sheet_trend(self, balance_sheets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze balance sheet trends

        Args:
            balance_sheets: List of balance sheets

        Returns:
            Balance sheet trend analysis
        """
        if not balance_sheets or len(balance_sheets) < 2:
            return {}

        sorted_statements = sorted(balance_sheets, key=lambda x: x.get('period_end', ''))

        assets = []
        liabilities = []
        equity = []
        periods = []

        for statement in sorted_statements:
            data = statement.get('data', {})

            total_assets = data.get('total_assets', 0)
            total_liabilities = data.get('total_liabilities', 0)
            total_equity = data.get('total_stockholder_equity', 0)

            if total_assets:
                assets.append(total_assets)
                liabilities.append(total_liabilities if total_liabilities else 0)
                equity.append(total_equity if total_equity else 0)
                periods.append(statement.get('period_end'))

        if len(assets) < 2:
            return {}

        # Calculate growth rates
        asset_growth = self.calculate_growth_rate(assets[-1], assets[-2])
        liability_growth = self.calculate_growth_rate(liabilities[-1], liabilities[-2]) if liabilities[-2] != 0 else None
        equity_growth = self.calculate_growth_rate(equity[-1], equity[-2]) if equity[-2] != 0 else None

        # Calculate debt-to-equity trend
        debt_to_equity_ratios = []
        for i in range(len(assets)):
            if equity[i] and equity[i] != 0:
                ratio = (liabilities[i] / equity[i])
                debt_to_equity_ratios.append(round(ratio, 2))
            else:
                debt_to_equity_ratios.append(None)

        return {
            'periods': periods,
            'total_assets': assets,
            'total_liabilities': liabilities,
            'total_equity': equity,
            'asset_growth': asset_growth,
            'liability_growth': liability_growth,
            'equity_growth': equity_growth,
            'debt_to_equity_trend': debt_to_equity_ratios
        }

    def analyze_cashflow_trend(self, cashflow_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze cash flow trends

        Args:
            cashflow_statements: List of cash flow statements

        Returns:
            Cash flow trend analysis
        """
        if not cashflow_statements or len(cashflow_statements) < 2:
            return {}

        sorted_statements = sorted(cashflow_statements, key=lambda x: x.get('period_end', ''))

        operating_cf = []
        investing_cf = []
        financing_cf = []
        free_cf = []
        periods = []

        for statement in sorted_statements:
            data = statement.get('data', {})

            op_cf = data.get('operating_cashflow', 0) or data.get('total_cash_from_operating_activities', 0)
            inv_cf = data.get('total_cashflows_from_investing_activities', 0)
            fin_cf = data.get('total_cash_from_financing_activities', 0)
            capex = data.get('capital_expenditures', 0) or 0

            if op_cf:
                operating_cf.append(op_cf)
                investing_cf.append(inv_cf if inv_cf else 0)
                financing_cf.append(fin_cf if fin_cf else 0)
                fcf = op_cf + capex  # capex is usually negative
                free_cf.append(fcf)
                periods.append(statement.get('period_end'))

        if len(operating_cf) < 2:
            return {}

        # Calculate growth rates
        op_cf_growth = self.calculate_growth_rate(operating_cf[-1], operating_cf[-2])
        fcf_growth = self.calculate_growth_rate(free_cf[-1], free_cf[-2]) if len(free_cf) >= 2 else None

        return {
            'periods': periods,
            'operating_cashflow': operating_cf,
            'investing_cashflow': investing_cf,
            'financing_cashflow': financing_cf,
            'free_cashflow': free_cf,
            'operating_cf_growth': op_cf_growth,
            'fcf_growth': fcf_growth
        }

    def generate_comprehensive_analysis(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        cashflow_statements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive trend analysis across all statements

        Args:
            income_statements: List of income statements
            balance_sheets: List of balance sheets
            cashflow_statements: List of cash flow statements

        Returns:
            Comprehensive trend analysis
        """
        return {
            'revenue_analysis': self.analyze_revenue_trend(income_statements),
            'profitability_analysis': self.analyze_profitability_trend(income_statements),
            'balance_sheet_analysis': self.analyze_balance_sheet_trend(balance_sheets),
            'cashflow_analysis': self.analyze_cashflow_trend(cashflow_statements)
        }
