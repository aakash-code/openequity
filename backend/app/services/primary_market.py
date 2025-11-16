"""
Primary Market Service
Track rights issues, OFS (Offer for Sale), and other primary market offerings
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random


class PrimaryMarketService:
    """Service for rights issues, OFS, and other primary market activities"""

    def get_rights_issues(
        self,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get list of rights issues

        Args:
            status: Filter by status (upcoming, open, closed)
            limit: Maximum number to return

        Returns:
            List of rights issues
        """
        rights_issues = self._generate_sample_rights_issues()

        if status:
            rights_issues = [ri for ri in rights_issues if ri['status'] == status]

        return rights_issues[:limit]

    def get_rights_issue_details(self, issue_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a rights issue

        Args:
            issue_id: Rights issue identifier

        Returns:
            Detailed rights issue information
        """
        issues = self._generate_sample_rights_issues()
        issue = next((i for i in issues if i['id'] == issue_id), None)

        if not issue:
            return {}

        # Add entitlement calculation
        issue['entitlement'] = {
            'ratio': issue['rights_ratio'],
            'example': f"If you hold {issue['rights_ratio']['for_shares']} shares, "
                      f"you are entitled to {issue['rights_ratio']['get_shares']} rights shares",
            'record_date': (datetime.now() - timedelta(days=random.randint(5, 20))).strftime('%Y-%m-%d')
        }

        # Add premium calculation
        market_price = issue['issue_price'] * random.uniform(1.1, 2.5)
        premium = market_price - issue['issue_price']
        issue['market_data'] = {
            'current_market_price': round(market_price, 2),
            'issue_price': issue['issue_price'],
            'premium_to_issue_price': round(premium, 2),
            'premium_percent': round((premium / issue['issue_price']) * 100, 2),
            'renunciation_allowed': random.choice([True, False])
        }

        return issue

    def get_ofs_list(
        self,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get list of OFS (Offer for Sale)

        Args:
            status: Filter by status (upcoming, open, closed)
            limit: Maximum number to return

        Returns:
            List of OFS offerings
        """
        ofs_list = self._generate_sample_ofs()

        if status:
            ofs_list = [ofs for ofs in ofs_list if ofs['status'] == status]

        return ofs_list[:limit]

    def get_ofs_details(self, ofs_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an OFS

        Args:
            ofs_id: OFS identifier

        Returns:
            Detailed OFS information
        """
        ofs_list = self._generate_sample_ofs()
        ofs = next((o for o in ofs_list if o['id'] == ofs_id), None)

        if not ofs:
            return {}

        # Add subscription details
        ofs['subscription'] = {
            'retail_subscription': round(random.uniform(0.5, 5.0), 2),
            'institutional_subscription': round(random.uniform(1.0, 20.0), 2),
            'total_subscription': round(random.uniform(1.0, 15.0), 2)
        }

        # Add allocation details
        ofs['allocation'] = {
            'retail_investors': {'percentage': 10, 'shares': ofs['shares_offered'] * 0.1},
            'institutional_investors': {'percentage': 90, 'shares': ofs['shares_offered'] * 0.9}
        }

        return ofs

    def get_buyback_list(
        self,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get list of buyback offers

        Args:
            status: Filter by status (upcoming, open, closed)
            limit: Maximum number to return

        Returns:
            List of buyback offers
        """
        buybacks = self._generate_sample_buybacks()

        if status:
            buybacks = [bb for bb in buybacks if bb['status'] == status]

        return buybacks[:limit]

    def get_buyback_details(self, buyback_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a buyback

        Args:
            buyback_id: Buyback identifier

        Returns:
            Detailed buyback information
        """
        buybacks = self._generate_sample_buybacks()
        buyback = next((bb for bb in buybacks if bb['id'] == buyback_id), None)

        if not buyback:
            return {}

        # Add acceptance ratio
        buyback['acceptance'] = {
            'ratio': f"1:{random.randint(2, 50)}",
            'example': "For every share tendered, 1 share may be accepted based on overall response",
            'max_tender': random.randint(100, 10000)
        }

        # Add return calculation
        market_price = buyback['buyback_price'] * random.uniform(0.7, 0.95)
        premium = buyback['buyback_price'] - market_price
        buyback['return_analysis'] = {
            'market_price': round(market_price, 2),
            'buyback_price': buyback['buyback_price'],
            'premium_amount': round(premium, 2),
            'premium_percent': round((premium / market_price) * 100, 2),
            'estimated_days': random.randint(30, 90)
        }

        return buyback

    def _generate_sample_rights_issues(self) -> List[Dict[str, Any]]:
        """Generate sample rights issues data"""
        companies = [
            'Tata Motors Ltd',
            'Reliance Industries',
            'HDFC Bank',
            'Asian Paints',
            'Bharti Airtel'
        ]

        statuses = ['upcoming', 'open', 'closed']
        issues = []

        for i, company in enumerate(companies):
            status = statuses[i % len(statuses)]

            if status == 'upcoming':
                open_date = datetime.now() + timedelta(days=random.randint(10, 30))
            elif status == 'open':
                open_date = datetime.now() - timedelta(days=random.randint(0, 5))
            else:
                open_date = datetime.now() - timedelta(days=random.randint(10, 60))

            close_date = open_date + timedelta(days=random.randint(10, 20))

            get_shares = random.randint(1, 5)
            for_shares = random.randint(5, 20)

            issue = {
                'id': f'RI{i+1:03d}',
                'company_name': company,
                'ticker': company.upper().replace(' ', ''),
                'status': status,
                'issue_size': round(random.uniform(500, 10000), 2),  # In crores
                'issue_price': round(random.uniform(100, 1000), 2),
                'rights_ratio': {
                    'get_shares': get_shares,
                    'for_shares': for_shares,
                    'display': f"{get_shares}:{for_shares}"
                },
                'open_date': open_date.strftime('%Y-%m-%d'),
                'close_date': close_date.strftime('%Y-%m-%d'),
                'purpose': random.choice([
                    'Debt reduction',
                    'Capacity expansion',
                    'Working capital',
                    'Acquisition funding',
                    'General corporate purposes'
                ]),
                'face_value': random.choice([1, 2, 5, 10])
            }

            issues.append(issue)

        return sorted(issues, key=lambda x: x['open_date'], reverse=True)

    def _generate_sample_ofs(self) -> List[Dict[str, Any]]:
        """Generate sample OFS data"""
        companies = [
            {'name': 'Coal India Ltd', 'promoter': 'Government of India'},
            {'name': 'NMDC Ltd', 'promoter': 'Government of India'},
            {'name': 'ONGC Ltd', 'promoter': 'Government of India'},
            {'name': 'Power Grid Corp', 'promoter': 'Government of India'},
            {'name': 'NTPC Ltd', 'promoter': 'Government of India'}
        ]

        statuses = ['upcoming', 'open', 'closed']
        ofs_list = []

        for i, company in enumerate(companies):
            status = statuses[i % len(statuses)]

            if status == 'upcoming':
                date = datetime.now() + timedelta(days=random.randint(5, 20))
            elif status == 'open':
                date = datetime.now()
            else:
                date = datetime.now() - timedelta(days=random.randint(1, 30))

            shares_offered = random.randint(10000000, 500000000)
            floor_price = round(random.uniform(100, 500), 2)

            ofs = {
                'id': f'OFS{i+1:03d}',
                'company_name': company['name'],
                'ticker': company['name'].split()[0].upper(),
                'promoter': company['promoter'],
                'status': status,
                'shares_offered': shares_offered,
                'offer_size': round(shares_offered * floor_price / 10000000, 2),  # In crores
                'floor_price': floor_price,
                'offer_date': date.strftime('%Y-%m-%d'),
                'current_promoter_holding': round(random.uniform(51, 90), 2),
                'post_ofs_promoter_holding': round(random.uniform(51, 75), 2),
                'discount_retail': random.choice([0, 2, 5])  # % discount for retail
            }

            ofs_list.append(ofs)

        return sorted(ofs_list, key=lambda x: x['offer_date'], reverse=True)

    def _generate_sample_buybacks(self) -> List[Dict[str, Any]]:
        """Generate sample buyback data"""
        companies = [
            'Infosys Ltd',
            'TCS Ltd',
            'Wipro Ltd',
            'HCL Technologies',
            'Tech Mahindra'
        ]

        statuses = ['upcoming', 'open', 'closed']
        buybacks = []

        for i, company in enumerate(companies):
            status = statuses[i % len(statuses)]

            if status == 'upcoming':
                open_date = datetime.now() + timedelta(days=random.randint(10, 30))
            elif status == 'open':
                open_date = datetime.now() - timedelta(days=random.randint(0, 10))
            else:
                open_date = datetime.now() - timedelta(days=random.randint(15, 90))

            close_date = open_date + timedelta(days=random.randint(10, 30))
            buyback_price = round(random.uniform(500, 3000), 2)

            buyback = {
                'id': f'BB{i+1:03d}',
                'company_name': company,
                'ticker': company.split()[0].upper(),
                'status': status,
                'buyback_size': round(random.uniform(1000, 50000), 2),  # In crores
                'buyback_price': buyback_price,
                'shares_to_buyback': random.randint(1000000, 100000000),
                'open_date': open_date.strftime('%Y-%m-%d'),
                'close_date': close_date.strftime('%Y-%m-%d'),
                'record_date': (open_date - timedelta(days=random.randint(5, 15))).strftime('%Y-%m-%d'),
                'method': random.choice(['Tender Offer', 'Open Market']),
                'percent_of_equity': round(random.uniform(1, 25), 2)
            }

            buybacks.append(buyback)

        return sorted(buybacks, key=lambda x: x['open_date'], reverse=True)
