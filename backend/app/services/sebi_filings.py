"""
SEBI Filings Service
Handles SEBI (Securities and Exchange Board of India) regulatory filings
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random


class SEBIFilingsService:
    """Service for SEBI regulatory filings"""

    # Types of SEBI filings
    FILING_TYPES = {
        'shareholding': 'Shareholding Pattern',
        'financial_results': 'Financial Results',
        'board_meeting': 'Board Meeting Intimation/Outcome',
        'corporate_action': 'Corporate Action',
        'compliance': 'Compliance Certificate',
        'material_event': 'Material Event/Information',
        'insider_trading': 'Insider Trading Disclosure',
        'annual_report': 'Annual Report',
        'agm_egm': 'AGM/EGM Notice',
        'related_party': 'Related Party Transactions',
        'acquisition': 'Acquisition/Takeover',
        'pledge': 'Pledge/Encumbrance of Shares'
    }

    def get_filing_types(self) -> Dict[str, str]:
        """Get all SEBI filing types"""
        return self.FILING_TYPES

    def get_recent_filings(
        self,
        ticker: str,
        limit: int = 20,
        filing_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent SEBI filings for a company

        Args:
            ticker: Company ticker
            limit: Number of filings to return
            filing_type: Filter by specific filing type

        Returns:
            List of filings
        """
        filings = []
        current_date = datetime.now()

        # Generate sample filings
        filing_types = [filing_type] if filing_type else list(self.FILING_TYPES.keys())

        for i in range(limit):
            filing_date = current_date - timedelta(days=random.randint(1, 180))
            ftype = random.choice(filing_types)

            filing = {
                'id': f"SEBI{random.randint(100000, 999999)}",
                'ticker': ticker,
                'filing_type': ftype,
                'filing_type_name': self.FILING_TYPES[ftype],
                'filing_date': filing_date.strftime('%Y-%m-%d'),
                'subject': self._generate_filing_subject(ftype, ticker),
                'category': self._get_filing_category(ftype),
                'exchange': random.choice(['NSE', 'BSE', 'Both']),
                'url': f"https://www.bseindia.com/filing/{ticker}/{filing_date.strftime('%Y%m%d')}.pdf",
                'size_kb': random.randint(50, 5000)
            }

            filings.append(filing)

        return sorted(filings, key=lambda x: x['filing_date'], reverse=True)

    def get_shareholding_pattern(
        self,
        ticker: str,
        quarter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get shareholding pattern for a company

        Args:
            ticker: Company ticker
            quarter: Quarter (Q1FY24, Q2FY24, etc.)

        Returns:
            Shareholding pattern data
        """
        # Generate shareholding pattern
        promoter_holding = round(random.uniform(40, 75), 2)
        fii_holding = round(random.uniform(10, 30), 2)
        dii_holding = round(random.uniform(5, 20), 2)
        public_holding = round(100 - promoter_holding, 2)

        return {
            'ticker': ticker,
            'quarter': quarter or 'Q4FY24',
            'as_of_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'promoter_holding': {
                'percentage': promoter_holding,
                'shares': random.randint(10000000, 100000000),
                'pledged_percentage': round(random.uniform(0, 20), 2) if random.random() > 0.7 else 0.0
            },
            'public_holding': {
                'percentage': public_holding,
                'shares': random.randint(5000000, 50000000)
            },
            'institutional_holding': {
                'fii': {
                    'percentage': fii_holding,
                    'shares': random.randint(2000000, 20000000)
                },
                'dii': {
                    'percentage': dii_holding,
                    'shares': random.randint(1000000, 15000000)
                },
                'mutual_funds': {
                    'percentage': round(dii_holding * 0.6, 2),
                    'shares': random.randint(500000, 10000000)
                }
            },
            'retail_holding': {
                'percentage': round(public_holding - fii_holding - dii_holding, 2),
                'number_of_shareholders': random.randint(50000, 500000)
            },
            'changes': {
                'promoter_change': round(random.uniform(-2, 2), 2),
                'fii_change': round(random.uniform(-1, 1), 2),
                'dii_change': round(random.uniform(-0.5, 0.5), 2)
            }
        }

    def get_board_meetings(
        self,
        ticker: str,
        upcoming: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get board meeting information

        Args:
            ticker: Company ticker
            upcoming: If True, return upcoming meetings; else past meetings

        Returns:
            List of board meetings
        """
        meetings = []
        current_date = datetime.now()

        for i in range(5):
            if upcoming:
                meeting_date = current_date + timedelta(days=random.randint(5, 60))
            else:
                meeting_date = current_date - timedelta(days=random.randint(5, 90))

            purpose = random.choice([
                'To consider and approve Financial Results',
                'To consider declaration of Dividend',
                'To consider Fund Raising',
                'To consider Merger/Acquisition',
                'General Business',
                'To consider appointment of Directors',
                'To approve Annual Report'
            ])

            meetings.append({
                'ticker': ticker,
                'meeting_date': meeting_date.strftime('%Y-%m-%d'),
                'intimation_date': (meeting_date - timedelta(days=7)).strftime('%Y-%m-%d'),
                'purpose': purpose,
                'outcome': None if upcoming else random.choice(['Approved', 'Discussed', 'Deferred']),
                'exchange': random.choice(['NSE', 'BSE', 'Both'])
            })

        return sorted(meetings, key=lambda x: x['meeting_date'], reverse=not upcoming)

    def get_insider_trading(
        self,
        ticker: str,
        days: int = 180
    ) -> List[Dict[str, Any]]:
        """
        Get insider trading disclosures

        Args:
            ticker: Company ticker
            days: Number of days to look back

        Returns:
            List of insider trading transactions
        """
        transactions = []
        current_date = datetime.now()

        for i in range(random.randint(5, 15)):
            trade_date = current_date - timedelta(days=random.randint(1, days))

            person_category = random.choice([
                'Promoter',
                'Director',
                'Key Managerial Personnel',
                'Immediate Relative of Promoter',
                'Employee'
            ])

            transaction_type = random.choice(['Buy', 'Sell', 'Pledge', 'Revoke Pledge'])

            transactions.append({
                'ticker': ticker,
                'person_name': f"Person {random.randint(1, 100)}",
                'person_category': person_category,
                'transaction_type': transaction_type,
                'transaction_date': trade_date.strftime('%Y-%m-%d'),
                'intimation_date': (trade_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                'quantity': random.randint(1000, 100000),
                'price_per_share': round(random.uniform(100, 2000), 2),
                'total_value': round(random.randint(1000, 100000) * random.uniform(100, 2000), 2),
                'mode': random.choice(['Market', 'Off-Market', 'ESOPs', 'Preferential'])
            })

        return sorted(transactions, key=lambda x: x['transaction_date'], reverse=True)

    def get_compliance_status(self, ticker: str) -> Dict[str, Any]:
        """
        Get compliance status for a company

        Args:
            ticker: Company ticker

        Returns:
            Compliance status information
        """
        return {
            'ticker': ticker,
            'as_of_date': datetime.now().strftime('%Y-%m-%d'),
            'listing_compliance': {
                'status': 'Compliant',
                'last_checked': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            },
            'sebi_regulations': {
                'lodr_compliance': 'Compliant',  # Listing Obligations and Disclosure Requirements
                'takeover_code': 'Compliant',
                'insider_trading': 'Compliant',
                'depositories_act': 'Compliant'
            },
            'corporate_governance': {
                'board_composition': 'Compliant',
                'audit_committee': 'Compliant',
                'nomination_committee': 'Compliant',
                'stakeholders_committee': 'Compliant',
                'independent_directors': 'Compliant'
            },
            'financial_reporting': {
                'quarterly_results': 'Filed on Time',
                'annual_report': 'Filed on Time',
                'cash_flow_statement': 'Filed on Time'
            },
            'penalty_history': {
                'has_penalties': random.random() > 0.9,
                'last_penalty_date': None,
                'total_penalties_3y': 0
            }
        }

    def _generate_filing_subject(self, filing_type: str, ticker: str) -> str:
        """Generate sample filing subject based on type"""
        subjects = {
            'shareholding': f"Shareholding Pattern for Quarter ended",
            'financial_results': f"Financial Results for Quarter/Year ended",
            'board_meeting': f"Intimation of Board Meeting",
            'corporate_action': f"Dividend/Bonus/Split Declaration",
            'compliance': f"Compliance Certificate under SEBI LODR",
            'material_event': f"Material Event Disclosure",
            'insider_trading': f"Disclosure of Insider Trading",
            'annual_report': f"Annual Report FY 2023-24",
            'agm_egm': f"Notice of Annual General Meeting",
            'related_party': f"Related Party Transactions Disclosure",
            'acquisition': f"Acquisition of Shares Disclosure",
            'pledge': f"Pledge of Promoter Shares"
        }

        return subjects.get(filing_type, "Company Filing")

    def _get_filing_category(self, filing_type: str) -> str:
        """Get category for filing type"""
        categories = {
            'shareholding': 'Ownership',
            'financial_results': 'Financial',
            'board_meeting': 'Corporate',
            'corporate_action': 'Corporate',
            'compliance': 'Regulatory',
            'material_event': 'Disclosure',
            'insider_trading': 'Ownership',
            'annual_report': 'Financial',
            'agm_egm': 'Corporate',
            'related_party': 'Disclosure',
            'acquisition': 'Ownership',
            'pledge': 'Ownership'
        }

        return categories.get(filing_type, 'General')
