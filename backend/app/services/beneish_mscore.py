"""
Beneish M-Score Calculator
Detects potential earnings manipulation using 8 financial ratios
"""
from typing import Dict, List, Any, Optional


class BeneishMScoreCalculator:
    """
    Calculates Beneish M-Score to identify potential earnings manipulation

    M-Score > -2.22 suggests possible earnings manipulation
    M-Score < -2.22 suggests earnings are likely legitimate
    """

    # M-Score formula coefficients
    COEFFICIENTS = {
        'constant': -4.84,
        'dsri': 0.92,
        'gmi': 0.528,
        'aqi': 0.404,
        'sgi': 0.892,
        'depi': 0.115,
        'sgai': -0.172,
        'tata': 4.679,
        'lvgi': -0.327
    }

    def calculate_dsri(
        self,
        current_receivables: float,
        current_revenue: float,
        prior_receivables: float,
        prior_revenue: float
    ) -> Optional[float]:
        """
        Calculate Days Sales in Receivables Index (DSRI)

        DSRI = (Receivables_t / Revenue_t) / (Receivables_t-1 / Revenue_t-1)

        Measures whether receivables are growing faster than sales
        """
        if prior_revenue == 0 or prior_receivables == 0 or current_revenue == 0:
            return None

        current_ratio = current_receivables / current_revenue
        prior_ratio = prior_receivables / prior_revenue

        if prior_ratio == 0:
            return None

        return current_ratio / prior_ratio

    def calculate_gmi(
        self,
        prior_gross_margin: float,
        current_gross_margin: float
    ) -> Optional[float]:
        """
        Calculate Gross Margin Index (GMI)

        GMI = Gross_Margin_t-1 / Gross_Margin_t

        Measures deterioration in gross margin (negative sign for growth)
        """
        if current_gross_margin == 0:
            return None

        return prior_gross_margin / current_gross_margin

    def calculate_aqi(
        self,
        current_total_assets: float,
        current_ppe: float,
        current_current_assets: float,
        prior_total_assets: float,
        prior_ppe: float,
        prior_current_assets: float
    ) -> Optional[float]:
        """
        Calculate Asset Quality Index (AQI)

        AQI = [1 - (Current_Assets_t + PPE_t) / Total_Assets_t] /
              [1 - (Current_Assets_t-1 + PPE_t-1) / Total_Assets_t-1]

        Measures proportion of assets that may be of lower quality
        """
        if prior_total_assets == 0 or current_total_assets == 0:
            return None

        current_quality = 1 - ((current_current_assets + current_ppe) / current_total_assets)
        prior_quality = 1 - ((prior_current_assets + prior_ppe) / prior_total_assets)

        if prior_quality == 0:
            return None

        return current_quality / prior_quality

    def calculate_sgi(
        self,
        current_revenue: float,
        prior_revenue: float
    ) -> Optional[float]:
        """
        Calculate Sales Growth Index (SGI)

        SGI = Revenue_t / Revenue_t-1

        Measures revenue growth (companies with high growth may be under pressure to manipulate)
        """
        if prior_revenue == 0:
            return None

        return current_revenue / prior_revenue

    def calculate_depi(
        self,
        prior_depreciation: float,
        prior_ppe: float,
        current_depreciation: float,
        current_ppe: float
    ) -> Optional[float]:
        """
        Calculate Depreciation Index (DEPI)

        DEPI = (Depreciation_t-1 / (PPE_t-1 + Depreciation_t-1)) /
               (Depreciation_t / (PPE_t + Depreciation_t))

        Measures rate of depreciation
        """
        if current_ppe + current_depreciation == 0:
            return None
        if prior_ppe + prior_depreciation == 0:
            return None

        prior_rate = prior_depreciation / (prior_ppe + prior_depreciation)
        current_rate = current_depreciation / (current_ppe + current_depreciation)

        if current_rate == 0:
            return None

        return prior_rate / current_rate

    def calculate_sgai(
        self,
        current_sga: float,
        current_revenue: float,
        prior_sga: float,
        prior_revenue: float
    ) -> Optional[float]:
        """
        Calculate Sales, General and Administrative expenses Index (SGAI)

        SGAI = (SGA_t / Revenue_t) / (SGA_t-1 / Revenue_t-1)

        Measures SGA expense as percentage of sales
        """
        if prior_revenue == 0 or current_revenue == 0:
            return None

        current_ratio = current_sga / current_revenue
        prior_ratio = prior_sga / prior_revenue

        if prior_ratio == 0:
            return None

        return current_ratio / prior_ratio

    def calculate_lvgi(
        self,
        current_total_debt: float,
        current_total_assets: float,
        prior_total_debt: float,
        prior_total_assets: float
    ) -> Optional[float]:
        """
        Calculate Leverage Index (LVGI)

        LVGI = (Total_Debt_t / Total_Assets_t) / (Total_Debt_t-1 / Total_Assets_t-1)

        Measures change in leverage
        """
        if prior_total_assets == 0 or current_total_assets == 0:
            return None

        current_leverage = current_total_debt / current_total_assets
        prior_leverage = prior_total_debt / prior_total_assets

        if prior_leverage == 0:
            return None

        return current_leverage / prior_leverage

    def calculate_tata(
        self,
        net_income: float,
        operating_cash_flow: float,
        total_assets: float
    ) -> Optional[float]:
        """
        Calculate Total Accruals to Total Assets (TATA)

        TATA = (Net_Income - Operating_Cash_Flow) / Total_Assets

        Measures accruals as a proportion of total assets
        """
        if total_assets == 0:
            return None

        total_accruals = net_income - operating_cash_flow
        return total_accruals / total_assets

    def calculate_mscore(
        self,
        current_financials: Dict[str, Any],
        prior_financials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate complete Beneish M-Score

        Args:
            current_financials: Current period financial data
            prior_financials: Prior period financial data

        Returns:
            Dictionary with M-Score and all component variables
        """
        # Extract current period data
        current_data = current_financials.get('data', {})
        prior_data = prior_financials.get('data', {})

        # Calculate DSRI
        dsri = self.calculate_dsri(
            current_receivables=current_data.get('accounts_receivable', 0),
            current_revenue=current_data.get('total_revenue', 0),
            prior_receivables=prior_data.get('accounts_receivable', 0),
            prior_revenue=prior_data.get('total_revenue', 0)
        )

        # Calculate GMI
        current_gross_margin = 0
        prior_gross_margin = 0

        if current_data.get('total_revenue', 0) != 0:
            current_gross_margin = (current_data.get('gross_profit', 0) / current_data.get('total_revenue', 1)) if current_data.get('total_revenue', 0) != 0 else 0

        if prior_data.get('total_revenue', 0) != 0:
            prior_gross_margin = (prior_data.get('gross_profit', 0) / prior_data.get('total_revenue', 1)) if prior_data.get('total_revenue', 0) != 0 else 0

        gmi = self.calculate_gmi(prior_gross_margin, current_gross_margin) if current_gross_margin != 0 else None

        # Calculate AQI (using balance sheet data)
        current_balance = current_financials.get('balance_data', {})
        prior_balance = prior_financials.get('balance_data', {})

        aqi = self.calculate_aqi(
            current_total_assets=current_balance.get('total_assets', 0),
            current_ppe=current_balance.get('property_plant_equipment', 0),
            current_current_assets=current_balance.get('total_current_assets', 0),
            prior_total_assets=prior_balance.get('total_assets', 0),
            prior_ppe=prior_balance.get('property_plant_equipment', 0),
            prior_current_assets=prior_balance.get('total_current_assets', 0)
        )

        # Calculate SGI
        sgi = self.calculate_sgi(
            current_revenue=current_data.get('total_revenue', 0),
            prior_revenue=prior_data.get('total_revenue', 0)
        )

        # Calculate DEPI
        depi = self.calculate_depi(
            prior_depreciation=prior_data.get('depreciation_amortization', 0),
            prior_ppe=prior_balance.get('property_plant_equipment', 0),
            current_depreciation=current_data.get('depreciation_amortization', 0),
            current_ppe=current_balance.get('property_plant_equipment', 0)
        )

        # Calculate SGAI
        sgai = self.calculate_sgai(
            current_sga=current_data.get('selling_general_administrative', 0),
            current_revenue=current_data.get('total_revenue', 0),
            prior_sga=prior_data.get('selling_general_administrative', 0),
            prior_revenue=prior_data.get('total_revenue', 0)
        )

        # Calculate LVGI
        lvgi = self.calculate_lvgi(
            current_total_debt=current_balance.get('total_debt', 0) or (current_balance.get('short_term_debt', 0) + current_balance.get('long_term_debt', 0)),
            current_total_assets=current_balance.get('total_assets', 0),
            prior_total_debt=prior_balance.get('total_debt', 0) or (prior_balance.get('short_term_debt', 0) + prior_balance.get('long_term_debt', 0)),
            prior_total_assets=prior_balance.get('total_assets', 0)
        )

        # Calculate TATA (using cash flow data)
        current_cashflow = current_financials.get('cashflow_data', {})

        tata = self.calculate_tata(
            net_income=current_data.get('net_income', 0),
            operating_cash_flow=current_cashflow.get('operating_cash_flow', 0),
            total_assets=current_balance.get('total_assets', 0)
        )

        # Calculate M-Score
        variables = {
            'dsri': dsri,
            'gmi': gmi,
            'aqi': aqi,
            'sgi': sgi,
            'depi': depi,
            'sgai': sgai,
            'lvgi': lvgi,
            'tata': tata
        }

        # Check if we have enough data
        missing_variables = [k for k, v in variables.items() if v is None]

        if len(missing_variables) > 2:  # Allow up to 2 missing variables
            return {
                'error': 'Insufficient data to calculate M-Score',
                'missing_variables': missing_variables,
                'variables': variables
            }

        # Calculate M-Score (use 0 for missing variables)
        mscore = self.COEFFICIENTS['constant']

        for var_name, var_value in variables.items():
            if var_value is not None:
                mscore += self.COEFFICIENTS[var_name] * var_value

        # Determine manipulation likelihood
        manipulation_risk = 'High' if mscore > -2.22 else 'Low'

        return {
            'mscore': round(mscore, 3),
            'manipulation_risk': manipulation_risk,
            'threshold': -2.22,
            'variables': {k: round(v, 3) if v is not None else None for k, v in variables.items()},
            'interpretation': self._interpret_mscore(mscore, variables)
        }

    def _interpret_mscore(self, mscore: float, variables: Dict[str, Optional[float]]) -> str:
        """
        Provide interpretation of M-Score
        """
        if mscore > -2.22:
            flags = []

            if variables.get('dsri') and variables['dsri'] > 1.031:
                flags.append('Receivables growing faster than sales')

            if variables.get('gmi') and variables['gmi'] > 1.014:
                flags.append('Deteriorating gross margins')

            if variables.get('aqi') and variables['aqi'] > 1.039:
                flags.append('Increasing proportion of soft assets')

            if variables.get('sgi') and variables['sgi'] > 1.134:
                flags.append('Rapid revenue growth')

            if variables.get('tata') and variables['tata'] > 0.031:
                flags.append('High accruals relative to assets')

            interpretation = f"M-Score of {mscore:.3f} suggests possible earnings manipulation. "

            if flags:
                interpretation += "Red flags: " + "; ".join(flags)

            return interpretation
        else:
            return f"M-Score of {mscore:.3f} suggests earnings are likely not manipulated. Company appears to have legitimate earnings quality."
