"""
Economic Value Added (EVA) Calculator
Measures true economic profit by accounting for cost of capital
"""
from typing import Dict, List, Any, Optional


class EVACalculator:
    """
    Calculates Economic Value Added and related metrics
    EVA = NOPAT - (Capital Employed × WACC)
    """

    def calculate_nopat(
        self,
        ebit: float,
        tax_rate: float,
        tax_adjustments: float = 0
    ) -> float:
        """
        Calculate Net Operating Profit After Tax

        Args:
            ebit: Earnings Before Interest and Tax
            tax_rate: Effective tax rate
            tax_adjustments: Tax shield adjustments

        Returns:
            NOPAT value
        """
        nopat = ebit * (1 - tax_rate) + tax_adjustments
        return nopat

    def calculate_invested_capital(
        self,
        total_assets: float,
        current_liabilities: float,
        cash: float = 0,
        non_operating_assets: float = 0
    ) -> float:
        """
        Calculate invested capital (capital employed)

        Args:
            total_assets: Total assets
            current_liabilities: Non-interest bearing current liabilities
            cash: Excess cash (optional adjustment)
            non_operating_assets: Non-operating assets to exclude

        Returns:
            Invested capital
        """
        invested_capital = total_assets - current_liabilities - cash - non_operating_assets
        return invested_capital

    def calculate_eva(
        self,
        nopat: float,
        invested_capital: float,
        wacc: float
    ) -> Dict[str, Any]:
        """
        Calculate Economic Value Added

        Args:
            nopat: Net Operating Profit After Tax
            invested_capital: Capital employed in the business
            wacc: Weighted Average Cost of Capital

        Returns:
            Dictionary with EVA metrics
        """
        capital_charge = invested_capital * wacc
        eva = nopat - capital_charge

        # Calculate return on invested capital
        roic = (nopat / invested_capital) if invested_capital != 0 else 0

        # EVA spread (ROIC - WACC)
        eva_spread = roic - wacc

        return {
            'nopat': round(nopat, 2),
            'invested_capital': round(invested_capital, 2),
            'wacc': round(wacc * 100, 2),
            'capital_charge': round(capital_charge, 2),
            'eva': round(eva, 2),
            'roic': round(roic * 100, 2),
            'eva_spread': round(eva_spread * 100, 2),
            'value_creation': eva > 0
        }

    def calculate_market_value_added(
        self,
        market_capitalization: float,
        invested_capital: float
    ) -> Dict[str, Any]:
        """
        Calculate Market Value Added (MVA)
        MVA = Market Cap - Invested Capital

        Args:
            market_capitalization: Current market cap
            invested_capital: Book value of invested capital

        Returns:
            Dictionary with MVA metrics
        """
        mva = market_capitalization - invested_capital

        return {
            'market_capitalization': round(market_capitalization, 2),
            'invested_capital': round(invested_capital, 2),
            'mva': round(mva, 2),
            'mva_to_capital_ratio': round(mva / invested_capital, 2) if invested_capital != 0 else 0
        }

    def multi_period_eva_analysis(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        wacc: float,
        tax_rate: float
    ) -> Dict[str, Any]:
        """
        Calculate EVA for multiple periods

        Args:
            income_statements: List of income statements (newest first)
            balance_sheets: List of balance sheets (newest first)
            wacc: Weighted Average Cost of Capital
            tax_rate: Effective tax rate

        Returns:
            Multi-period EVA analysis
        """
        if not income_statements or not balance_sheets:
            return {'error': 'Insufficient data for analysis'}

        eva_results = []

        # Sort by period (oldest first)
        sorted_income = sorted(income_statements, key=lambda x: x.get('period_end', ''))
        sorted_balance = sorted(balance_sheets, key=lambda x: x.get('period_end', ''))

        for i, income_stmt in enumerate(sorted_income):
            # Find matching balance sheet
            period = income_stmt.get('period_end')
            balance_data = next(
                (b for b in sorted_balance if b.get('period_end') == period),
                None
            )

            if not balance_data:
                continue

            income_data = income_stmt.get('data', {})
            balance_data_dict = balance_data.get('data', {})

            # Calculate NOPAT
            ebit = income_data.get('operating_income', 0)
            if not ebit:
                ebit = income_data.get('ebit', 0)

            nopat = self.calculate_nopat(ebit, tax_rate)

            # Calculate invested capital
            total_assets = balance_data_dict.get('total_assets', 0)
            current_liabilities = balance_data_dict.get('total_current_liabilities', 0)
            cash = balance_data_dict.get('cash_and_cash_equivalents', 0) or balance_data_dict.get('cash', 0)

            invested_capital = self.calculate_invested_capital(
                total_assets,
                current_liabilities,
                cash * 0.5  # Assume 50% of cash is excess
            )

            # Calculate EVA
            eva_metrics = self.calculate_eva(nopat, invested_capital, wacc)

            eva_results.append({
                'period': period,
                'fiscal_year': income_stmt.get('fiscal_year'),
                **eva_metrics
            })

        if not eva_results:
            return {'error': 'Unable to calculate EVA'}

        # Calculate trends
        eva_values = [r['eva'] for r in eva_results]
        roic_values = [r['roic'] for r in eva_results]

        return {
            'periods': eva_results,
            'latest_eva': eva_results[-1]['eva'] if eva_results else None,
            'eva_trend': 'improving' if len(eva_values) >= 2 and eva_values[-1] > eva_values[-2] else 'declining',
            'average_eva': round(sum(eva_values) / len(eva_values), 2) if eva_values else None,
            'average_roic': round(sum(roic_values) / len(roic_values), 2) if roic_values else None,
            'cumulative_eva': round(sum(eva_values), 2) if eva_values else None
        }

    def calculate_eva_momentum(
        self,
        current_eva: float,
        previous_eva: float
    ) -> Dict[str, Any]:
        """
        Calculate EVA momentum (change in EVA)

        Args:
            current_eva: Current period EVA
            previous_eva: Previous period EVA

        Returns:
            EVA momentum metrics
        """
        eva_change = current_eva - previous_eva

        if previous_eva != 0:
            eva_change_percent = (eva_change / abs(previous_eva)) * 100
        else:
            eva_change_percent = 0

        return {
            'current_eva': round(current_eva, 2),
            'previous_eva': round(previous_eva, 2),
            'eva_change': round(eva_change, 2),
            'eva_change_percent': round(eva_change_percent, 2),
            'momentum': 'positive' if eva_change > 0 else 'negative' if eva_change < 0 else 'neutral'
        }

    def calculate_residual_income(
        self,
        net_income: float,
        equity: float,
        cost_of_equity: float
    ) -> Dict[str, Any]:
        """
        Calculate Residual Income (similar to EVA but for equity)
        RI = Net Income - (Equity × Cost of Equity)

        Args:
            net_income: Net income
            equity: Book value of equity
            cost_of_equity: Required return on equity

        Returns:
            Residual income metrics
        """
        equity_charge = equity * cost_of_equity
        residual_income = net_income - equity_charge

        roe = (net_income / equity) if equity != 0 else 0

        return {
            'net_income': round(net_income, 2),
            'equity': round(equity, 2),
            'cost_of_equity': round(cost_of_equity * 100, 2),
            'equity_charge': round(equity_charge, 2),
            'residual_income': round(residual_income, 2),
            'roe': round(roe * 100, 2),
            'excess_return': round((roe - cost_of_equity) * 100, 2)
        }
