"""
Altman Z-Score Calculator
Predicts bankruptcy probability using 5 financial ratios
"""
from typing import Dict, List, Any, Optional


class AltmanZScoreCalculator:
    """
    Calculates Altman Z-Score to predict bankruptcy risk

    Original Z-Score (for public manufacturing companies):
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

    Z > 2.99: Safe zone (low bankruptcy risk)
    1.81 < Z < 2.99: Grey zone (moderate risk)
    Z < 1.81: Distress zone (high bankruptcy risk)
    """

    # Original Z-Score coefficients (public manufacturing)
    COEFFICIENTS_PUBLIC = {
        'x1': 1.2,   # Working Capital / Total Assets
        'x2': 1.4,   # Retained Earnings / Total Assets
        'x3': 3.3,   # EBIT / Total Assets
        'x4': 0.6,   # Market Value of Equity / Total Liabilities
        'x5': 1.0    # Sales / Total Assets
    }

    # Z'-Score coefficients (private manufacturing)
    COEFFICIENTS_PRIVATE = {
        'x1': 0.717,
        'x2': 0.847,
        'x3': 3.107,
        'x4': 0.420,  # Book Value of Equity / Total Liabilities
        'x5': 0.998
    }

    # Z''-Score coefficients (non-manufacturing / service)
    COEFFICIENTS_SERVICE = {
        'x1': 6.56,
        'x2': 3.26,
        'x3': 6.72,
        'x4': 1.05,
        'x5': 0.0    # Sales not used in service model
    }

    def calculate_x1(
        self,
        current_assets: float,
        current_liabilities: float,
        total_assets: float
    ) -> Optional[float]:
        """
        Calculate X1: Working Capital / Total Assets

        Measures liquid assets relative to total assets
        """
        if total_assets == 0:
            return None

        working_capital = current_assets - current_liabilities
        return working_capital / total_assets

    def calculate_x2(
        self,
        retained_earnings: float,
        total_assets: float
    ) -> Optional[float]:
        """
        Calculate X2: Retained Earnings / Total Assets

        Measures cumulative profitability and age of firm
        """
        if total_assets == 0:
            return None

        return retained_earnings / total_assets

    def calculate_x3(
        self,
        ebit: float,
        total_assets: float
    ) -> Optional[float]:
        """
        Calculate X3: EBIT / Total Assets

        Measures productivity of assets
        """
        if total_assets == 0:
            return None

        return ebit / total_assets

    def calculate_x4_public(
        self,
        market_cap: float,
        total_liabilities: float
    ) -> Optional[float]:
        """
        Calculate X4 (Public): Market Value of Equity / Total Liabilities

        Measures how much assets can decline before liabilities exceed assets
        """
        if total_liabilities == 0:
            return None

        return market_cap / total_liabilities

    def calculate_x4_private(
        self,
        total_equity: float,
        total_liabilities: float
    ) -> Optional[float]:
        """
        Calculate X4 (Private): Book Value of Equity / Total Liabilities

        Private company version using book value
        """
        if total_liabilities == 0:
            return None

        return total_equity / total_liabilities

    def calculate_x5(
        self,
        revenue: float,
        total_assets: float
    ) -> Optional[float]:
        """
        Calculate X5: Sales / Total Assets

        Measures asset turnover
        """
        if total_assets == 0:
            return None

        return revenue / total_assets

    def calculate_zscore(
        self,
        income_statement: Dict[str, Any],
        balance_sheet: Dict[str, Any],
        market_cap: Optional[float] = None,
        company_type: str = 'public_manufacturing'
    ) -> Dict[str, Any]:
        """
        Calculate Altman Z-Score

        Args:
            income_statement: Income statement data
            balance_sheet: Balance sheet data
            market_cap: Market capitalization (required for public companies)
            company_type: 'public_manufacturing', 'private_manufacturing', or 'service'

        Returns:
            Dictionary with Z-Score and component ratios
        """
        income_data = income_statement.get('data', {})
        balance_data = balance_sheet.get('data', {})

        # Get total assets
        total_assets = balance_data.get('total_assets', 0)

        if total_assets == 0:
            return {'error': 'Total assets is zero or missing'}

        # Calculate X1: Working Capital / Total Assets
        x1 = self.calculate_x1(
            current_assets=balance_data.get('total_current_assets', 0),
            current_liabilities=balance_data.get('total_current_liabilities', 0),
            total_assets=total_assets
        )

        # Calculate X2: Retained Earnings / Total Assets
        x2 = self.calculate_x2(
            retained_earnings=balance_data.get('retained_earnings', 0),
            total_assets=total_assets
        )

        # Calculate X3: EBIT / Total Assets
        ebit = income_data.get('operating_income', 0) or income_data.get('ebit', 0)
        x3 = self.calculate_x3(
            ebit=ebit,
            total_assets=total_assets
        )

        # Calculate X4 based on company type
        if company_type == 'public_manufacturing' and market_cap:
            total_liabilities = balance_data.get('total_liabilities', 0)
            x4 = self.calculate_x4_public(market_cap, total_liabilities)
        else:
            total_equity = balance_data.get('total_equity', 0) or balance_data.get('total_stockholder_equity', 0)
            total_liabilities = balance_data.get('total_liabilities', 0)
            x4 = self.calculate_x4_private(total_equity, total_liabilities)

        # Calculate X5: Sales / Total Assets
        revenue = income_data.get('total_revenue', 0) or income_data.get('revenue', 0)
        x5 = self.calculate_x5(revenue, total_assets)

        # Select appropriate coefficients
        if company_type == 'public_manufacturing':
            coefficients = self.COEFFICIENTS_PUBLIC
            thresholds = {'safe': 2.99, 'distress': 1.81}
        elif company_type == 'private_manufacturing':
            coefficients = self.COEFFICIENTS_PRIVATE
            thresholds = {'safe': 2.90, 'distress': 1.23}
        else:  # service
            coefficients = self.COEFFICIENTS_SERVICE
            thresholds = {'safe': 2.60, 'distress': 1.10}

        # Calculate Z-Score
        variables = {'x1': x1, 'x2': x2, 'x3': x3, 'x4': x4, 'x5': x5}

        # Check for missing variables
        missing = [k for k, v in variables.items() if v is None]

        if missing:
            return {
                'error': 'Insufficient data to calculate Z-Score',
                'missing_variables': missing,
                'variables': variables
            }

        zscore = sum(coefficients[k] * v for k, v in variables.items() if v is not None)

        # Determine risk zone
        if zscore > thresholds['safe']:
            risk_zone = 'Safe'
            risk_level = 'Low'
        elif zscore > thresholds['distress']:
            risk_zone = 'Grey'
            risk_level = 'Moderate'
        else:
            risk_zone = 'Distress'
            risk_level = 'High'

        return {
            'zscore': round(zscore, 2),
            'risk_zone': risk_zone,
            'risk_level': risk_level,
            'thresholds': thresholds,
            'company_type': company_type,
            'variables': {k: round(v, 4) if v is not None else None for k, v in variables.items()},
            'interpretation': self._interpret_zscore(zscore, risk_zone, variables)
        }

    def multi_period_zscore(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        market_caps: Optional[List[float]] = None,
        company_type: str = 'public_manufacturing'
    ) -> Dict[str, Any]:
        """
        Calculate Z-Score for multiple periods to show trend

        Args:
            income_statements: List of income statements (newest first)
            balance_sheets: List of balance sheets (newest first)
            market_caps: List of market caps (newest first)
            company_type: Type of company

        Returns:
            Multi-period Z-Score analysis
        """
        if not income_statements or not balance_sheets:
            return {'error': 'Insufficient data for multi-period analysis'}

        results = []

        # Sort by period (oldest first for chronological display)
        sorted_income = sorted(income_statements, key=lambda x: x.get('period_end', ''))
        sorted_balance = sorted(balance_sheets, key=lambda x: x.get('period_end', ''))

        for i, income_stmt in enumerate(sorted_income):
            period = income_stmt.get('period_end')

            # Find matching balance sheet
            balance = next(
                (b for b in sorted_balance if b.get('period_end') == period),
                None
            )

            if not balance:
                continue

            # Get market cap for this period if available
            market_cap = None
            if market_caps and i < len(market_caps):
                market_cap = market_caps[i]

            # Calculate Z-Score for this period
            zscore_result = self.calculate_zscore(
                income_statement=income_stmt,
                balance_sheet=balance,
                market_cap=market_cap,
                company_type=company_type
            )

            if 'error' not in zscore_result:
                results.append({
                    'period': period,
                    'fiscal_year': income_stmt.get('fiscal_year'),
                    **zscore_result
                })

        if not results:
            return {'error': 'Unable to calculate Z-Score for any period'}

        # Analyze trend
        zscores = [r['zscore'] for r in results]
        latest_zscore = zscores[-1]
        trend = 'improving' if len(zscores) >= 2 and zscores[-1] > zscores[-2] else 'deteriorating'

        return {
            'periods': results,
            'latest_zscore': latest_zscore,
            'latest_risk_zone': results[-1]['risk_zone'],
            'trend': trend,
            'average_zscore': round(sum(zscores) / len(zscores), 2),
            'min_zscore': min(zscores),
            'max_zscore': max(zscores)
        }

    def _interpret_zscore(
        self,
        zscore: float,
        risk_zone: str,
        variables: Dict[str, Optional[float]]
    ) -> str:
        """
        Provide interpretation of Z-Score
        """
        if risk_zone == 'Safe':
            return f"Z-Score of {zscore:.2f} indicates low bankruptcy risk. The company appears financially healthy with strong fundamentals."
        elif risk_zone == 'Grey':
            concerns = []

            if variables.get('x1') and variables['x1'] < 0:
                concerns.append('negative working capital')

            if variables.get('x2') and variables['x2'] < 0:
                concerns.append('accumulated losses')

            if variables.get('x3') and variables['x3'] < 0.05:
                concerns.append('low asset productivity')

            interpretation = f"Z-Score of {zscore:.2f} indicates moderate bankruptcy risk. "

            if concerns:
                interpretation += "Concerns: " + ", ".join(concerns) + ". "

            interpretation += "Close monitoring recommended."

            return interpretation
        else:  # Distress
            return f"Z-Score of {zscore:.2f} indicates high bankruptcy risk. The company shows significant financial distress and may face bankruptcy within 2 years without improvement."
