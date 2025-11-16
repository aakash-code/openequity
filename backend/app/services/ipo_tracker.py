"""
IPO Tracking Service
Track IPOs, subscription data, pricing, and listing gains
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random


class IPOTrackerService:
    """Service for tracking IPO and primary market offerings"""

    # IPO status types
    IPO_STATUS = {
        'upcoming': 'Upcoming',
        'open': 'Open for Subscription',
        'closed': 'Subscription Closed',
        'listed': 'Listed',
        'withdrawn': 'Withdrawn'
    }

    # Investor categories
    INVESTOR_CATEGORIES = ['retail', 'hni', 'qib', 'employee', 'shareholder']

    def get_ipo_list(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get list of IPOs filtered by status

        Args:
            status: Filter by status (upcoming, open, closed, listed, withdrawn)
            limit: Maximum number of IPOs to return

        Returns:
            List of IPO details
        """
        # In production, fetch from database
        # For now, generate sample data
        ipos = self._generate_sample_ipos()

        if status:
            ipos = [ipo for ipo in ipos if ipo['status'] == status]

        return ipos[:limit]

    def get_ipo_details(self, ipo_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific IPO

        Args:
            ipo_id: IPO identifier

        Returns:
            Detailed IPO information
        """
        # In production, fetch from database
        return self._generate_ipo_details(ipo_id)

    def get_subscription_data(self, ipo_id: str) -> Dict[str, Any]:
        """
        Get real-time subscription data for an IPO

        Args:
            ipo_id: IPO identifier

        Returns:
            Subscription data by category
        """
        return {
            'ipo_id': ipo_id,
            'last_updated': datetime.now().isoformat(),
            'overall_subscription': round(random.uniform(0.5, 150.0), 2),
            'categories': {
                'retail': {
                    'subscription_times': round(random.uniform(0.3, 5.0), 2),
                    'applications': random.randint(50000, 500000),
                    'shares_bid': random.randint(10000000, 100000000),
                    'shares_offered': random.randint(5000000, 50000000)
                },
                'hni': {
                    'subscription_times': round(random.uniform(5.0, 200.0), 2),
                    'applications': random.randint(5000, 50000),
                    'shares_bid': random.randint(50000000, 500000000),
                    'shares_offered': random.randint(2000000, 20000000)
                },
                'qib': {
                    'subscription_times': round(random.uniform(10.0, 100.0), 2),
                    'applications': random.randint(100, 1000),
                    'shares_bid': random.randint(100000000, 1000000000),
                    'shares_offered': random.randint(50000000, 500000000)
                }
            },
            'total_applications': random.randint(100000, 1000000),
            'total_amount_bid': round(random.uniform(1000, 50000), 2)  # In crores
        }

    def get_listing_gains(self, ipo_id: str) -> Dict[str, Any]:
        """
        Calculate listing gains for an IPO

        Args:
            ipo_id: IPO identifier

        Returns:
            Listing price, gains, and performance metrics
        """
        issue_price = round(random.uniform(100, 2000), 2)
        listing_price = round(issue_price * random.uniform(0.85, 1.85), 2)
        current_price = round(listing_price * random.uniform(0.90, 1.30), 2)

        listing_gain_percent = ((listing_price - issue_price) / issue_price) * 100
        current_return_percent = ((current_price - issue_price) / issue_price) * 100

        return {
            'ipo_id': ipo_id,
            'issue_price': issue_price,
            'listing_price': listing_price,
            'listing_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'listing_gain_percent': round(listing_gain_percent, 2),
            'listing_gain_amount': round(listing_price - issue_price, 2),
            'current_price': current_price,
            'current_return_percent': round(current_return_percent, 2),
            'current_return_amount': round(current_price - issue_price, 2),
            'high_price': round(current_price * random.uniform(1.0, 1.5), 2),
            'low_price': round(current_price * random.uniform(0.5, 1.0), 2),
            'volume': random.randint(100000, 10000000),
            'market_cap': round(current_price * random.randint(10000000, 1000000000), 2)
        }

    def get_grey_market_premium(self, ipo_id: str) -> Dict[str, Any]:
        """
        Get grey market premium for an IPO

        Args:
            ipo_id: IPO identifier

        Returns:
            Grey market premium data
        """
        issue_price = round(random.uniform(100, 2000), 2)
        gmp = round(random.uniform(-50, 500), 2)
        gmp_percent = (gmp / issue_price) * 100
        expected_listing_price = issue_price + gmp

        return {
            'ipo_id': ipo_id,
            'issue_price': issue_price,
            'grey_market_premium': gmp,
            'gmp_percent': round(gmp_percent, 2),
            'expected_listing_price': expected_listing_price,
            'last_updated': datetime.now().isoformat(),
            'sentiment': 'Positive' if gmp > 0 else 'Negative' if gmp < 0 else 'Neutral',
            'subject_to_market_risk': True
        }

    def get_allotment_status(self, ipo_id: str, application_number: str) -> Dict[str, Any]:
        """
        Check IPO allotment status

        Args:
            ipo_id: IPO identifier
            application_number: Application number

        Returns:
            Allotment status
        """
        # Randomly determine allotment
        is_allotted = random.choice([True, False])
        shares_applied = random.randint(1, 10) * 15  # In lots of 15
        shares_allotted = shares_applied if is_allotted else 0

        return {
            'ipo_id': ipo_id,
            'application_number': application_number,
            'is_allotted': is_allotted,
            'shares_applied': shares_applied,
            'shares_allotted': shares_allotted,
            'allotment_date': (datetime.now() + timedelta(days=random.randint(-5, 2))).strftime('%Y-%m-%d'),
            'refund_date': (datetime.now() + timedelta(days=random.randint(-3, 4))).strftime('%Y-%m-%d'),
            'listing_date': (datetime.now() + timedelta(days=random.randint(-1, 6))).strftime('%Y-%m-%d'),
            'status': 'Allotted' if is_allotted else 'Not Allotted'
        }

    def _generate_sample_ipos(self) -> List[Dict[str, Any]]:
        """Generate sample IPO data"""
        companies = [
            {'name': 'TechVision Solutions Ltd', 'sector': 'Technology', 'exchange': 'NSE'},
            {'name': 'GreenEnergy Power Corp', 'sector': 'Renewable Energy', 'exchange': 'BSE'},
            {'name': 'HealthPlus Pharma Ltd', 'sector': 'Pharmaceuticals', 'exchange': 'NSE'},
            {'name': 'FinServe Technologies', 'sector': 'Financial Services', 'exchange': 'NSE'},
            {'name': 'Urban Infrastructure Ltd', 'sector': 'Infrastructure', 'exchange': 'BSE'},
            {'name': 'CloudNet Systems', 'sector': 'IT Services', 'exchange': 'NSE'},
            {'name': 'EcoPackaging Industries', 'sector': 'Manufacturing', 'exchange': 'BSE'},
            {'name': 'SmartLogistics Corp', 'sector': 'Logistics', 'exchange': 'NSE'},
            {'name': 'FoodChain Retail Ltd', 'sector': 'Retail', 'exchange': 'NSE'},
            {'name': 'AutoParts Manufacturing', 'sector': 'Automobile', 'exchange': 'BSE'}
        ]

        statuses = ['upcoming', 'open', 'closed', 'listed', 'listed', 'listed']
        ipos = []

        for i, company in enumerate(companies):
            status = statuses[i % len(statuses)]
            issue_price_range = [random.randint(100, 500), random.randint(500, 1500)]
            issue_price_range.sort()

            # Dates based on status
            if status == 'upcoming':
                open_date = datetime.now() + timedelta(days=random.randint(5, 30))
                close_date = open_date + timedelta(days=3)
                listing_date = close_date + timedelta(days=random.randint(5, 10))
            elif status == 'open':
                open_date = datetime.now() - timedelta(days=random.randint(0, 2))
                close_date = open_date + timedelta(days=3)
                listing_date = close_date + timedelta(days=random.randint(5, 10))
            elif status == 'closed':
                open_date = datetime.now() - timedelta(days=random.randint(3, 7))
                close_date = open_date + timedelta(days=3)
                listing_date = close_date + timedelta(days=random.randint(5, 10))
            else:  # listed
                open_date = datetime.now() - timedelta(days=random.randint(30, 365))
                close_date = open_date + timedelta(days=3)
                listing_date = close_date + timedelta(days=random.randint(5, 10))

            ipo = {
                'id': f'IPO{i+1:03d}',
                'company_name': company['name'],
                'sector': company['sector'],
                'exchange': company['exchange'],
                'status': status,
                'issue_type': random.choice(['Fresh Issue', 'Offer for Sale', 'Fresh Issue + OFS']),
                'issue_size': round(random.uniform(100, 5000), 2),  # In crores
                'price_range': issue_price_range,
                'lot_size': random.choice([10, 15, 20, 25, 50]),
                'open_date': open_date.strftime('%Y-%m-%d'),
                'close_date': close_date.strftime('%Y-%m-%d'),
                'allotment_date': (close_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                'listing_date': listing_date.strftime('%Y-%m-%d'),
                'lead_managers': random.sample(['ICICI Securities', 'Kotak Mahindra Capital', 'Axis Capital',
                                               'JM Financial', 'IIFL Securities'], k=random.randint(1, 3)),
                'registrar': random.choice(['Link Intime', 'KFin Technologies', 'Karvy Computershare']),
                'minimum_investment': issue_price_range[0] * random.choice([10, 15, 20, 25, 50]),
                'face_value': random.choice([1, 2, 5, 10])
            }

            # Add subscription data for open/closed IPOs
            if status in ['open', 'closed', 'listed']:
                ipo['subscription_times'] = round(random.uniform(0.5, 150.0), 2)

            # Add listing price for listed IPOs
            if status == 'listed':
                final_price = random.randint(issue_price_range[0], issue_price_range[1])
                listing_price = round(final_price * random.uniform(0.85, 1.85), 2)
                current_price = round(listing_price * random.uniform(0.90, 1.30), 2)
                ipo['issue_price'] = final_price
                ipo['listing_price'] = listing_price
                ipo['current_price'] = current_price
                ipo['listing_gain_percent'] = round(((listing_price - final_price) / final_price) * 100, 2)

            ipos.append(ipo)

        return sorted(ipos, key=lambda x: x['open_date'], reverse=True)

    def _generate_ipo_details(self, ipo_id: str) -> Dict[str, Any]:
        """Generate detailed IPO information"""
        ipos = self._generate_sample_ipos()
        ipo = next((i for i in ipos if i['id'] == ipo_id), None)

        if not ipo:
            return {}

        # Add detailed information
        ipo['company_details'] = {
            'industry': ipo['sector'],
            'founded': random.randint(1980, 2020),
            'headquarters': random.choice(['Mumbai', 'Bengaluru', 'Delhi', 'Pune', 'Hyderabad']),
            'employees': random.randint(500, 50000),
            'website': f"www.{ipo['company_name'].lower().replace(' ', '')}.com"
        }

        ipo['financials'] = {
            'revenue_fy23': round(random.uniform(100, 10000), 2),
            'revenue_fy22': round(random.uniform(80, 8000), 2),
            'revenue_fy21': round(random.uniform(60, 6000), 2),
            'net_profit_fy23': round(random.uniform(10, 1000), 2),
            'net_profit_fy22': round(random.uniform(8, 800), 2),
            'net_profit_fy21': round(random.uniform(6, 600), 2),
            'eps_fy23': round(random.uniform(5, 100), 2),
            'roe': round(random.uniform(10, 35), 2),
            'debt_to_equity': round(random.uniform(0.1, 2.0), 2)
        }

        ipo['valuation'] = {
            'pre_issue_equity': round(random.uniform(100, 5000), 2),
            'post_issue_equity': round(random.uniform(150, 6000), 2),
            'market_cap_at_lower_price': round(ipo['price_range'][0] * random.randint(10000000, 100000000), 2),
            'market_cap_at_upper_price': round(ipo['price_range'][1] * random.randint(10000000, 100000000), 2),
            'pe_ratio_at_upper_price': round(random.uniform(15, 80), 2),
            'book_value': round(random.uniform(50, 500), 2)
        }

        ipo['reservation'] = {
            'qib': {'percentage': 50, 'shares': round(ipo['issue_size'] * 0.5 / ipo['price_range'][1])},
            'retail': {'percentage': 35, 'shares': round(ipo['issue_size'] * 0.35 / ipo['price_range'][1])},
            'hni': {'percentage': 15, 'shares': round(ipo['issue_size'] * 0.15 / ipo['price_range'][1])}
        }

        ipo['objectives'] = random.sample([
            'Expansion of manufacturing facilities',
            'Working capital requirements',
            'Debt repayment',
            'Research and development',
            'Brand building and marketing',
            'Acquisitions and strategic investments',
            'General corporate purposes'
        ], k=random.randint(3, 5))

        ipo['strengths'] = random.sample([
            'Strong market position in growing sector',
            'Experienced management team',
            'Diversified product portfolio',
            'Established customer base',
            'Strong financial performance',
            'Technology and innovation focus',
            'Asset-light business model'
        ], k=random.randint(3, 5))

        ipo['risks'] = random.sample([
            'Intense competition in the industry',
            'Regulatory changes',
            'Customer concentration risk',
            'Dependence on key personnel',
            'Foreign exchange fluctuation risk',
            'Economic downturn impact',
            'Commodity price volatility'
        ], k=random.randint(3, 5))

        return ipo
