"""
Stock Screening Service
Multi-criteria stock filtering and screening templates
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_


class StockScreenerService:
    """Service for screening stocks based on various criteria"""

    # Pre-built screening templates
    TEMPLATES = {
        'value': {
            'name': 'Value Stocks',
            'description': 'Undervalued companies with strong fundamentals',
            'criteria': {
                'pe_ratio_max': 15,
                'pb_ratio_max': 1.5,
                'debt_to_equity_max': 0.5,
                'roe_min': 15,
                'revenue_growth_min': 5
            }
        },
        'growth': {
            'name': 'Growth Stocks',
            'description': 'Fast-growing companies with strong revenue expansion',
            'criteria': {
                'revenue_growth_min': 20,
                'earnings_growth_min': 15,
                'roe_min': 20,
                'market_cap_min': 1000000000  # $1B
            }
        },
        'dividend': {
            'name': 'Dividend Stocks',
            'description': 'High dividend yield with stable payouts',
            'criteria': {
                'dividend_yield_min': 3,
                'payout_ratio_max': 60,
                'roe_min': 12,
                'debt_to_equity_max': 1.0
            }
        },
        'quality': {
            'name': 'Quality Stocks',
            'description': 'High-quality companies with strong financials',
            'criteria': {
                'roe_min': 20,
                'roic_min': 15,
                'current_ratio_min': 1.5,
                'debt_to_equity_max': 0.5,
                'profit_margin_min': 15
            }
        },
        'momentum': {
            'name': 'Momentum Stocks',
            'description': 'Stocks with strong price and earnings momentum',
            'criteria': {
                'revenue_growth_min': 15,
                'earnings_growth_min': 20,
                'roe_min': 15
            }
        },
        'small_cap_growth': {
            'name': 'Small Cap Growth',
            'description': 'Small cap companies with high growth potential',
            'criteria': {
                'market_cap_min': 300000000,    # $300M
                'market_cap_max': 2000000000,   # $2B
                'revenue_growth_min': 25,
                'roe_min': 15
            }
        },
        'large_cap_stable': {
            'name': 'Large Cap Stable',
            'description': 'Large, stable companies with consistent performance',
            'criteria': {
                'market_cap_min': 10000000000,  # $10B
                'roe_min': 12,
                'debt_to_equity_max': 0.8,
                'dividend_yield_min': 2
            }
        }
    }

    def get_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all available screening templates"""
        return self.TEMPLATES

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific screening template"""
        return self.TEMPLATES.get(template_id)

    def screen_stocks(
        self,
        db: Session,
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Screen stocks based on provided criteria

        Args:
            db: Database session
            criteria: Dictionary of screening criteria

        Returns:
            List of companies matching the criteria
        """
        from app.models.company import Company

        # Start with base query
        query = db.query(Company)

        # Apply filters based on criteria
        conditions = []

        # Market cap filters
        if 'market_cap_min' in criteria:
            conditions.append(Company.market_cap >= criteria['market_cap_min'])
        if 'market_cap_max' in criteria:
            conditions.append(Company.market_cap <= criteria['market_cap_max'])

        # Valuation filters
        if 'pe_ratio_min' in criteria:
            conditions.append(Company.pe_ratio >= criteria['pe_ratio_min'])
        if 'pe_ratio_max' in criteria:
            conditions.append(Company.pe_ratio <= criteria['pe_ratio_max'])
            conditions.append(Company.pe_ratio != None)

        if 'pb_ratio_min' in criteria:
            conditions.append(Company.pb_ratio >= criteria['pb_ratio_min'])
        if 'pb_ratio_max' in criteria:
            conditions.append(Company.pb_ratio <= criteria['pb_ratio_max'])
            conditions.append(Company.pb_ratio != None)

        if 'ps_ratio_min' in criteria:
            conditions.append(Company.ps_ratio >= criteria['ps_ratio_min'])
        if 'ps_ratio_max' in criteria:
            conditions.append(Company.ps_ratio <= criteria['ps_ratio_max'])
            conditions.append(Company.ps_ratio != None)

        # Profitability filters
        if 'roe_min' in criteria:
            conditions.append(Company.roe >= criteria['roe_min'])
            conditions.append(Company.roe != None)
        if 'roe_max' in criteria:
            conditions.append(Company.roe <= criteria['roe_max'])

        if 'roa_min' in criteria:
            conditions.append(Company.roa >= criteria['roa_min'])
            conditions.append(Company.roa != None)
        if 'roa_max' in criteria:
            conditions.append(Company.roa <= criteria['roa_max'])

        if 'roic_min' in criteria:
            conditions.append(Company.roic >= criteria['roic_min'])
            conditions.append(Company.roic != None)
        if 'roic_max' in criteria:
            conditions.append(Company.roic <= criteria['roic_max'])

        if 'profit_margin_min' in criteria:
            conditions.append(Company.profit_margin >= criteria['profit_margin_min'])
            conditions.append(Company.profit_margin != None)
        if 'profit_margin_max' in criteria:
            conditions.append(Company.profit_margin <= criteria['profit_margin_max'])

        # Growth filters
        if 'revenue_growth_min' in criteria:
            conditions.append(Company.revenue_growth >= criteria['revenue_growth_min'])
            conditions.append(Company.revenue_growth != None)
        if 'revenue_growth_max' in criteria:
            conditions.append(Company.revenue_growth <= criteria['revenue_growth_max'])

        if 'earnings_growth_min' in criteria:
            conditions.append(Company.earnings_growth >= criteria['earnings_growth_min'])
            conditions.append(Company.earnings_growth != None)
        if 'earnings_growth_max' in criteria:
            conditions.append(Company.earnings_growth <= criteria['earnings_growth_max'])

        # Dividend filters
        if 'dividend_yield_min' in criteria:
            conditions.append(Company.dividend_yield >= criteria['dividend_yield_min'])
            conditions.append(Company.dividend_yield != None)
        if 'dividend_yield_max' in criteria:
            conditions.append(Company.dividend_yield <= criteria['dividend_yield_max'])

        if 'payout_ratio_min' in criteria:
            conditions.append(Company.payout_ratio >= criteria['payout_ratio_min'])
            conditions.append(Company.payout_ratio != None)
        if 'payout_ratio_max' in criteria:
            conditions.append(Company.payout_ratio <= criteria['payout_ratio_max'])

        # Financial health filters
        if 'current_ratio_min' in criteria:
            conditions.append(Company.current_ratio >= criteria['current_ratio_min'])
            conditions.append(Company.current_ratio != None)
        if 'current_ratio_max' in criteria:
            conditions.append(Company.current_ratio <= criteria['current_ratio_max'])

        if 'debt_to_equity_min' in criteria:
            conditions.append(Company.debt_to_equity >= criteria['debt_to_equity_min'])
            conditions.append(Company.debt_to_equity != None)
        if 'debt_to_equity_max' in criteria:
            conditions.append(Company.debt_to_equity <= criteria['debt_to_equity_max'])

        if 'interest_coverage_min' in criteria:
            conditions.append(Company.interest_coverage >= criteria['interest_coverage_min'])
            conditions.append(Company.interest_coverage != None)

        # Sector/Industry filters
        if 'sector' in criteria and criteria['sector']:
            if isinstance(criteria['sector'], list):
                conditions.append(Company.sector.in_(criteria['sector']))
            else:
                conditions.append(Company.sector == criteria['sector'])

        if 'industry' in criteria and criteria['industry']:
            if isinstance(criteria['industry'], list):
                conditions.append(Company.industry.in_(criteria['industry']))
            else:
                conditions.append(Company.industry == criteria['industry'])

        # Exchange filter
        if 'exchange' in criteria and criteria['exchange']:
            if isinstance(criteria['exchange'], list):
                conditions.append(Company.exchange.in_(criteria['exchange']))
            else:
                conditions.append(Company.exchange == criteria['exchange'])

        # Country filter
        if 'country' in criteria and criteria['country']:
            if isinstance(criteria['country'], list):
                conditions.append(Company.country.in_(criteria['country']))
            else:
                conditions.append(Company.country == criteria['country'])

        # Apply all conditions
        if conditions:
            query = query.filter(and_(*conditions))

        # Apply limit (default to 100)
        limit = criteria.get('limit', 100)
        query = query.limit(limit)

        # Execute query
        companies = query.all()

        # Convert to dictionaries
        results = []
        for company in companies:
            results.append({
                'ticker': company.ticker,
                'name': company.name,
                'sector': company.sector,
                'industry': company.industry,
                'market_cap': company.market_cap,
                'pe_ratio': company.pe_ratio,
                'pb_ratio': company.pb_ratio,
                'ps_ratio': company.ps_ratio,
                'roe': company.roe,
                'roa': company.roa,
                'roic': company.roic,
                'profit_margin': company.profit_margin,
                'revenue_growth': company.revenue_growth,
                'earnings_growth': company.earnings_growth,
                'dividend_yield': company.dividend_yield,
                'payout_ratio': company.payout_ratio,
                'current_ratio': company.current_ratio,
                'debt_to_equity': company.debt_to_equity,
                'interest_coverage': company.interest_coverage,
                'exchange': company.exchange,
                'country': company.country,
                'currency': company.currency
            })

        return results

    def screen_by_template(
        self,
        db: Session,
        template_id: str,
        additional_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Screen stocks using a pre-built template

        Args:
            db: Database session
            template_id: ID of the template to use
            additional_criteria: Additional criteria to add/override

        Returns:
            List of companies matching the template criteria
        """
        template = self.get_template(template_id)

        if not template:
            return []

        # Start with template criteria
        criteria = template['criteria'].copy()

        # Merge with additional criteria
        if additional_criteria:
            criteria.update(additional_criteria)

        return self.screen_stocks(db, criteria)
