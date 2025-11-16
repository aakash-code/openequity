"""
Indian Market Data Service
Handles NSE/BSE specific data, SEBI filings, and Indian market indices
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random


class IndianMarketService:
    """Service for Indian stock market data (NSE/BSE)"""

    # Major Indian market indices
    INDIAN_INDICES = {
        'NIFTY50': {
            'name': 'NIFTY 50',
            'description': 'Top 50 companies on NSE',
            'exchange': 'NSE'
        },
        'NIFTY100': {
            'name': 'NIFTY 100',
            'description': 'Top 100 companies on NSE',
            'exchange': 'NSE'
        },
        'NIFTYBANK': {
            'name': 'NIFTY Bank',
            'description': 'Banking sector index',
            'exchange': 'NSE'
        },
        'NIFTYIT': {
            'name': 'NIFTY IT',
            'description': 'IT sector index',
            'exchange': 'NSE'
        },
        'SENSEX': {
            'name': 'BSE SENSEX',
            'description': 'Top 30 companies on BSE',
            'exchange': 'BSE'
        },
        'BSE100': {
            'name': 'BSE 100',
            'description': 'Top 100 companies on BSE',
            'exchange': 'BSE'
        }
    }

    # NSE sectors
    NSE_SECTORS = [
        'Automobiles',
        'Banking',
        'Financial Services',
        'FMCG',
        'IT',
        'Media',
        'Metal',
        'Pharma',
        'PSU Bank',
        'Private Bank',
        'Realty',
        'Energy',
        'Infrastructure'
    ]

    def get_indian_indices(self) -> Dict[str, Dict[str, Any]]:
        """Get all Indian market indices"""
        return self.INDIAN_INDICES

    def get_index_info(self, index_symbol: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific Indian index"""
        return self.INDIAN_INDICES.get(index_symbol)

    def get_nse_sectors(self) -> List[str]:
        """Get list of NSE sectors"""
        return self.NSE_SECTORS

    def enrich_company_with_indian_data(
        self,
        ticker: str,
        exchange: str
    ) -> Dict[str, Any]:
        """
        Enrich company data with Indian market specific information

        Args:
            ticker: Company ticker symbol
            exchange: Exchange (NSE or BSE)

        Returns:
            Dictionary with Indian market data
        """
        # In production, this would fetch real data from NSE/BSE APIs
        # For now, return structured placeholder data

        indian_data = {
            'nse_symbol': None,
            'bse_code': None,
            'isin': None,
            'industry': None,
            'listing_date': None,
            'face_value': None,
            'market_lot': 1,
            'indices_membership': [],
            'sebi_registered': True
        }

        if exchange == 'NSE':
            indian_data['nse_symbol'] = ticker
            indian_data['isin'] = f'INE{random.randint(100000, 999999)}01'
            indian_data['face_value'] = random.choice([1, 2, 5, 10])
            indian_data['market_lot'] = 1
            # Randomly assign to indices
            if random.random() > 0.7:
                indian_data['indices_membership'].append('NIFTY50')
            if random.random() > 0.5:
                indian_data['indices_membership'].append('NIFTY100')

        elif exchange == 'BSE':
            indian_data['bse_code'] = str(random.randint(500000, 599999))
            indian_data['isin'] = f'INE{random.randint(100000, 999999)}01'
            indian_data['face_value'] = random.choice([1, 2, 5, 10])
            indian_data['market_lot'] = 1
            if random.random() > 0.8:
                indian_data['indices_membership'].append('SENSEX')

        return indian_data

    def get_market_status(self, exchange: str = 'NSE') -> Dict[str, Any]:
        """
        Get current market status for NSE/BSE

        Args:
            exchange: Exchange name (NSE or BSE)

        Returns:
            Market status information
        """
        # In production, fetch real market hours and status
        now = datetime.now()

        # IST market hours: 9:15 AM - 3:30 PM
        market_open_time = now.replace(hour=9, minute=15, second=0)
        market_close_time = now.replace(hour=15, minute=30, second=0)

        is_open = market_open_time <= now <= market_close_time and now.weekday() < 5

        return {
            'exchange': exchange,
            'status': 'OPEN' if is_open else 'CLOSED',
            'market_open_time': '09:15 IST',
            'market_close_time': '15:30 IST',
            'current_time': now.strftime('%H:%M:%S IST'),
            'is_trading_day': now.weekday() < 5
        }

    def get_corporate_actions(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get corporate actions for an Indian company

        Args:
            ticker: Company ticker
            start_date: Start date for actions
            end_date: End date for actions

        Returns:
            List of corporate actions
        """
        # In production, fetch from NSE/BSE APIs
        # Return sample corporate actions

        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=365)

        actions = []

        # Sample dividend
        actions.append({
            'action_type': 'Dividend',
            'ex_date': (end_date - timedelta(days=90)).strftime('%Y-%m-%d'),
            'record_date': (end_date - timedelta(days=88)).strftime('%Y-%m-%d'),
            'payment_date': (end_date - timedelta(days=60)).strftime('%Y-%m-%d'),
            'amount': round(random.uniform(5, 50), 2),
            'currency': 'INR',
            'purpose': 'Final Dividend'
        })

        # Sample bonus
        if random.random() > 0.7:
            actions.append({
                'action_type': 'Bonus',
                'ex_date': (end_date - timedelta(days=180)).strftime('%Y-%m-%d'),
                'record_date': (end_date - timedelta(days=178)).strftime('%Y-%m-%d'),
                'ratio': '1:1',
                'purpose': 'Bonus Issue'
            })

        # Sample split
        if random.random() > 0.8:
            actions.append({
                'action_type': 'Split',
                'ex_date': (end_date - timedelta(days=200)).strftime('%Y-%m-%d'),
                'record_date': (end_date - timedelta(days=198)).strftime('%Y-%m-%d'),
                'old_fv': 10,
                'new_fv': 1,
                'ratio': '1:10',
                'purpose': 'Stock Split'
            })

        return sorted(actions, key=lambda x: x.get('ex_date', ''), reverse=True)

    def get_price_band(self, ticker: str, exchange: str = 'NSE') -> Dict[str, Any]:
        """
        Get price band (circuit limits) for Indian stock

        Args:
            ticker: Company ticker
            exchange: Exchange (NSE or BSE)

        Returns:
            Price band information
        """
        # In production, fetch real circuit limits
        # Indian markets typically have ±20% circuit limits for most stocks

        # Sample current price
        current_price = round(random.uniform(100, 5000), 2)

        # Standard circuit limits
        upper_circuit = round(current_price * 1.20, 2)
        lower_circuit = round(current_price * 0.80, 2)

        return {
            'ticker': ticker,
            'exchange': exchange,
            'current_price': current_price,
            'upper_circuit': upper_circuit,
            'lower_circuit': lower_circuit,
            'circuit_percentage': 20.0,
            'price_band_type': 'Regular'
        }

    def get_delivery_percentage(
        self,
        ticker: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get delivery percentage data for Indian stock

        Args:
            ticker: Company ticker
            days: Number of days of data

        Returns:
            Delivery percentage statistics
        """
        # Delivery percentage indicates actual delivery vs speculative trading
        # Higher delivery % indicates investor confidence

        delivery_data = []
        current_date = datetime.now()

        for i in range(days):
            date = current_date - timedelta(days=i)
            delivery_pct = round(random.uniform(30, 80), 2)

            delivery_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'delivery_percentage': delivery_pct,
                'traded_quantity': random.randint(100000, 10000000),
                'delivery_quantity': int(random.randint(100000, 10000000) * (delivery_pct / 100))
            })

        avg_delivery = sum(d['delivery_percentage'] for d in delivery_data) / len(delivery_data)

        return {
            'ticker': ticker,
            'average_delivery_percentage': round(avg_delivery, 2),
            'latest_delivery_percentage': delivery_data[0]['delivery_percentage'],
            'delivery_trend': 'High' if avg_delivery > 60 else 'Medium' if avg_delivery > 40 else 'Low',
            'data': sorted(delivery_data, key=lambda x: x['date'], reverse=True)
        }

    def get_fii_dii_data(
        self,
        ticker: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get FII/DII (Foreign/Domestic Institutional Investor) activity

        Args:
            ticker: Company ticker
            days: Number of days of data

        Returns:
            FII/DII activity data
        """
        fii_dii_data = []
        current_date = datetime.now()

        for i in range(days):
            date = current_date - timedelta(days=i)

            fii_dii_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'fii_net': round(random.uniform(-1000, 1000), 2),  # Crores
                'dii_net': round(random.uniform(-500, 500), 2),     # Crores
                'total_institutional': round(random.uniform(-1500, 1500), 2)
            })

        # Calculate totals
        total_fii = sum(d['fii_net'] for d in fii_dii_data)
        total_dii = sum(d['dii_net'] for d in fii_dii_data)

        return {
            'ticker': ticker,
            'period_days': days,
            'total_fii_net': round(total_fii, 2),
            'total_dii_net': round(total_dii, 2),
            'total_institutional_net': round(total_fii + total_dii, 2),
            'fii_trend': 'Buying' if total_fii > 0 else 'Selling',
            'dii_trend': 'Buying' if total_dii > 0 else 'Selling',
            'data': sorted(fii_dii_data, key=lambda x: x['date'], reverse=True)
        }

    def format_indian_number(self, number: float) -> str:
        """
        Format number in Indian numbering system (Lakhs/Crores)

        Args:
            number: Number to format

        Returns:
            Formatted string
        """
        if number >= 10000000:  # 1 Crore
            return f"₹{number / 10000000:.2f} Cr"
        elif number >= 100000:  # 1 Lakh
            return f"₹{number / 100000:.2f} L"
        else:
            return f"₹{number:,.2f}"
