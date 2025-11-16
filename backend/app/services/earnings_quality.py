"""
Earnings Quality Analysis Service
Analyzes the quality and sustainability of reported earnings
"""
from typing import Dict, List, Any, Optional


class EarningsQualityAnalyzer:
    """
    Comprehensive earnings quality analysis including:
    - Accruals analysis
    - Cash flow quality
    - Revenue quality
    - Earnings persistence
    """

    def calculate_accruals_ratio(
        self,
        net_income: float,
        operating_cash_flow: float
    ) -> Optional[float]:
        """
        Calculate accruals ratio

        Accruals Ratio = (Net Income - Operating Cash Flow) / Net Income

        Higher accruals relative to cash flow suggests lower earnings quality
        """
        if net_income == 0:
            return None

        accruals = net_income - operating_cash_flow
        return accruals / abs(net_income)

    def calculate_cash_flow_to_income_ratio(
        self,
        operating_cash_flow: float,
        net_income: float
    ) -> Optional[float]:
        """
        Calculate cash flow to income ratio

        CF/NI Ratio = Operating Cash Flow / Net Income

        Ratio > 1 indicates high quality earnings (cash-backed)
        Ratio < 1 indicates potential earnings quality concerns
        """
        if net_income == 0:
            return None

        return operating_cash_flow / net_income

    def calculate_earnings_persistence(
        self,
        earnings_history: List[float]
    ) -> Dict[str, Any]:
        """
        Measure earnings persistence and stability

        Analyzes consistency and growth of earnings over time
        """
        if len(earnings_history) < 3:
            return {'error': 'Insufficient data for persistence analysis'}

        # Count positive earnings years
        positive_years = sum(1 for e in earnings_history if e > 0)
        positive_ratio = positive_years / len(earnings_history)

        # Calculate coefficient of variation (volatility)
        if len(earnings_history) >= 3:
            mean_earnings = sum(earnings_history) / len(earnings_history)
            variance = sum((e - mean_earnings) ** 2 for e in earnings_history) / len(earnings_history)
            std_dev = variance ** 0.5

            if mean_earnings != 0:
                coefficient_of_variation = (std_dev / abs(mean_earnings))
            else:
                coefficient_of_variation = None
        else:
            coefficient_of_variation = None

        # Determine earnings quality based on persistence
        if positive_ratio >= 0.8 and coefficient_of_variation and coefficient_of_variation < 0.5:
            quality_rating = 'High'
        elif positive_ratio >= 0.6:
            quality_rating = 'Moderate'
        else:
            quality_rating = 'Low'

        return {
            'positive_earnings_ratio': round(positive_ratio, 2),
            'coefficient_of_variation': round(coefficient_of_variation, 3) if coefficient_of_variation else None,
            'quality_rating': quality_rating,
            'consecutive_positive_years': self._count_consecutive_positive(earnings_history)
        }

    def _count_consecutive_positive(self, earnings: List[float]) -> int:
        """Count consecutive years of positive earnings from most recent"""
        count = 0
        for e in reversed(earnings):
            if e > 0:
                count += 1
            else:
                break
        return count

    def analyze_revenue_quality(
        self,
        current_revenue: float,
        current_receivables: float,
        prior_revenue: float,
        prior_receivables: float
    ) -> Dict[str, Any]:
        """
        Analyze revenue quality

        High-quality revenue converts to cash quickly
        """
        # Days Sales Outstanding (DSO)
        if current_revenue == 0:
            return {'error': 'Current revenue is zero'}

        current_dso = (current_receivables / current_revenue) * 365

        prior_dso = None
        dso_change = None

        if prior_revenue and prior_revenue > 0:
            prior_dso = (prior_receivables / prior_revenue) * 365
            dso_change = current_dso - prior_dso

        # Receivables to Revenue ratio
        receivables_ratio = current_receivables / current_revenue

        # Quality assessment
        if current_dso < 45:
            quality = 'High'
        elif current_dso < 60:
            quality = 'Moderate'
        else:
            quality = 'Low'

        # Check for deterioration
        if dso_change and dso_change > 5:
            quality_trend = 'Deteriorating'
        elif dso_change and dso_change < -5:
            quality_trend = 'Improving'
        else:
            quality_trend = 'Stable'

        return {
            'days_sales_outstanding': round(current_dso, 1),
            'prior_dso': round(prior_dso, 1) if prior_dso else None,
            'dso_change': round(dso_change, 1) if dso_change else None,
            'receivables_to_revenue_ratio': round(receivables_ratio, 3),
            'quality': quality,
            'trend': quality_trend
        }

    def analyze_working_capital_quality(
        self,
        current_assets: float,
        current_liabilities: float,
        cash: float,
        revenue: float
    ) -> Dict[str, Any]:
        """
        Analyze working capital quality
        """
        working_capital = current_assets - current_liabilities

        # Working capital ratio
        if current_liabilities > 0:
            current_ratio = current_assets / current_liabilities
        else:
            current_ratio = None

        # Quick ratio (acid test)
        if current_liabilities > 0:
            quick_ratio = (current_assets - (current_assets * 0.3)) / current_liabilities  # Approximate inventory
        else:
            quick_ratio = None

        # Working capital to revenue
        if revenue > 0:
            wc_to_revenue = working_capital / revenue
        else:
            wc_to_revenue = None

        # Quality assessment
        if current_ratio and current_ratio > 2.0 and quick_ratio and quick_ratio > 1.0:
            quality = 'High'
        elif current_ratio and current_ratio > 1.5:
            quality = 'Moderate'
        else:
            quality = 'Low'

        return {
            'working_capital': round(working_capital, 2),
            'current_ratio': round(current_ratio, 2) if current_ratio else None,
            'quick_ratio': round(quick_ratio, 2) if quick_ratio else None,
            'wc_to_revenue': round(wc_to_revenue, 3) if wc_to_revenue else None,
            'quality': quality
        }

    def comprehensive_quality_analysis(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        cashflow_statements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive earnings quality analysis

        Args:
            income_statements: List of income statements (newest first)
            balance_sheets: List of balance sheets (newest first)
            cashflow_statements: List of cash flow statements (newest first)

        Returns:
            Comprehensive quality metrics
        """
        if not income_statements or not cashflow_statements:
            return {'error': 'Insufficient data for quality analysis'}

        # Get latest period data
        latest_income = income_statements[0]
        latest_cashflow = cashflow_statements[0]
        latest_balance = balance_sheets[0] if balance_sheets else None

        income_data = latest_income.get('data', {})
        cashflow_data = latest_cashflow.get('data', {})
        balance_data = latest_balance.get('data', {}) if latest_balance else {}

        # 1. Accruals Analysis
        net_income = income_data.get('net_income', 0)
        operating_cash_flow = cashflow_data.get('operating_cash_flow', 0)

        accruals_ratio = self.calculate_accruals_ratio(net_income, operating_cash_flow)
        cf_to_income = self.calculate_cash_flow_to_income_ratio(operating_cash_flow, net_income)

        # 2. Earnings Persistence
        earnings_history = [stmt.get('data', {}).get('net_income', 0) for stmt in income_statements]
        persistence = self.calculate_earnings_persistence(earnings_history)

        # 3. Revenue Quality
        revenue_quality = None
        if len(income_statements) >= 2 and len(balance_sheets) >= 2:
            current_revenue = income_data.get('total_revenue', 0)
            current_receivables = balance_data.get('accounts_receivable', 0)

            prior_income = income_statements[1].get('data', {})
            prior_balance = balance_sheets[1].get('data', {})

            prior_revenue = prior_income.get('total_revenue', 0)
            prior_receivables = prior_balance.get('accounts_receivable', 0)

            revenue_quality = self.analyze_revenue_quality(
                current_revenue, current_receivables,
                prior_revenue, prior_receivables
            )

        # 4. Working Capital Quality
        wc_quality = None
        if latest_balance:
            wc_quality = self.analyze_working_capital_quality(
                current_assets=balance_data.get('total_current_assets', 0),
                current_liabilities=balance_data.get('total_current_liabilities', 0),
                cash=balance_data.get('cash_and_cash_equivalents', 0) or balance_data.get('cash', 0),
                revenue=income_data.get('total_revenue', 0)
            )

        # Overall Quality Score (0-100)
        quality_score = self._calculate_overall_quality_score(
            accruals_ratio, cf_to_income, persistence, revenue_quality, wc_quality
        )

        return {
            'quality_score': quality_score,
            'accruals_analysis': {
                'accruals_ratio': round(accruals_ratio, 3) if accruals_ratio else None,
                'cf_to_income_ratio': round(cf_to_income, 3) if cf_to_income else None,
                'assessment': self._assess_accruals(accruals_ratio, cf_to_income)
            },
            'earnings_persistence': persistence,
            'revenue_quality': revenue_quality,
            'working_capital_quality': wc_quality,
            'overall_assessment': self._overall_assessment(quality_score)
        }

    def _calculate_overall_quality_score(
        self,
        accruals_ratio: Optional[float],
        cf_to_income: Optional[float],
        persistence: Dict[str, Any],
        revenue_quality: Optional[Dict[str, Any]],
        wc_quality: Optional[Dict[str, Any]]
    ) -> int:
        """
        Calculate overall quality score (0-100)
        """
        score = 50  # Start at neutral

        # Accruals component (up to ±20 points)
        if accruals_ratio is not None:
            if accruals_ratio < 0.1:
                score += 20
            elif accruals_ratio < 0.3:
                score += 10
            elif accruals_ratio > 0.7:
                score -= 20
            elif accruals_ratio > 0.5:
                score -= 10

        # Cash flow component (up to ±15 points)
        if cf_to_income is not None:
            if cf_to_income > 1.2:
                score += 15
            elif cf_to_income > 1.0:
                score += 10
            elif cf_to_income < 0.8:
                score -= 15
            elif cf_to_income < 0.9:
                score -= 10

        # Persistence component (up to ±15 points)
        if 'error' not in persistence:
            if persistence.get('quality_rating') == 'High':
                score += 15
            elif persistence.get('quality_rating') == 'Low':
                score -= 15

        # Revenue quality component (up to ±10 points)
        if revenue_quality and 'error' not in revenue_quality:
            if revenue_quality.get('quality') == 'High':
                score += 10
            elif revenue_quality.get('quality') == 'Low':
                score -= 10

        return max(0, min(100, score))  # Clamp between 0 and 100

    def _assess_accruals(
        self,
        accruals_ratio: Optional[float],
        cf_to_income: Optional[float]
    ) -> str:
        """
        Assess accruals quality
        """
        if accruals_ratio is None or cf_to_income is None:
            return 'Insufficient data'

        if cf_to_income > 1.2 and accruals_ratio < 0.2:
            return 'High quality - earnings are well-supported by cash flow'
        elif cf_to_income > 1.0:
            return 'Good quality - earnings exceed cash generation'
        elif cf_to_income > 0.8:
            return 'Moderate quality - some reliance on accruals'
        else:
            return 'Low quality - earnings rely heavily on accruals, cash flow is weak'

    def _overall_assessment(self, quality_score: int) -> str:
        """
        Provide overall assessment based on quality score
        """
        if quality_score >= 75:
            return 'Excellent - High quality earnings with strong cash generation and persistence'
        elif quality_score >= 60:
            return 'Good - Above average earnings quality with some strong indicators'
        elif quality_score >= 40:
            return 'Fair - Mixed earnings quality signals, further investigation recommended'
        else:
            return 'Poor - Significant earnings quality concerns, exercise caution'
