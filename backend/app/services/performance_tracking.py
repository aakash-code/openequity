"""
Performance Tracking Service
Calculates portfolio performance metrics over time
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class PerformanceTrackingService:
    """Service for calculating portfolio performance over time"""

    def calculate_time_series_returns(
        self,
        transactions: List[Dict[str, Any]],
        current_prices: Dict[str, float],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate time-series returns for portfolio

        Args:
            transactions: List of transaction dictionaries
            current_prices: Dictionary mapping ticker to current price
            start_date: Start date for performance calculation
            end_date: End date for performance calculation

        Returns:
            Dictionary containing time-series performance data
        """
        if not transactions:
            return {
                'daily_returns': [],
                'cumulative_returns': [],
                'period_returns': {},
                'annualized_return': 0.0,
                'total_return': 0.0,
                'inception_date': None,
                'latest_date': None
            }

        # Sort transactions by date
        sorted_txns = sorted(transactions, key=lambda x: x['transaction_date'])

        # Determine date range
        inception = sorted_txns[0]['transaction_date']
        if isinstance(inception, str):
            inception = datetime.fromisoformat(inception.replace('Z', '+00:00'))

        if start_date is None:
            start_date = inception
        if end_date is None:
            end_date = datetime.now()

        # Calculate portfolio value for each day
        daily_values = self._calculate_daily_portfolio_values(
            sorted_txns, current_prices, start_date, end_date
        )

        if not daily_values:
            return {
                'daily_returns': [],
                'cumulative_returns': [],
                'period_returns': {},
                'annualized_return': 0.0,
                'total_return': 0.0,
                'inception_date': inception.isoformat(),
                'latest_date': end_date.isoformat()
            }

        # Calculate daily returns
        daily_returns = self._calculate_daily_returns(daily_values)

        # Calculate cumulative returns
        cumulative_returns = self._calculate_cumulative_returns(daily_returns)

        # Calculate period returns
        period_returns = self._calculate_period_returns(daily_values)

        # Calculate annualized return
        annualized_return = self._calculate_annualized_return(
            daily_values, inception, end_date
        )

        # Calculate total return
        total_return = 0.0
        if daily_values:
            first_value = daily_values[0]['value']
            last_value = daily_values[-1]['value']
            if first_value > 0:
                total_return = ((last_value - first_value) / first_value) * 100

        return {
            'daily_returns': daily_returns,
            'cumulative_returns': cumulative_returns,
            'period_returns': period_returns,
            'annualized_return': round(annualized_return, 2),
            'total_return': round(total_return, 2),
            'inception_date': inception.isoformat(),
            'latest_date': end_date.isoformat(),
            'daily_values': daily_values
        }

    def _calculate_daily_portfolio_values(
        self,
        transactions: List[Dict[str, Any]],
        current_prices: Dict[str, float],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Calculate portfolio value for each day"""
        daily_values = []

        # Build position history
        positions = defaultdict(lambda: {'quantity': 0.0, 'cost_basis': 0.0})
        cash_flows = defaultdict(float)

        # Group transactions by date
        txns_by_date = defaultdict(list)
        for txn in transactions:
            txn_date = txn['transaction_date']
            if isinstance(txn_date, str):
                txn_date = datetime.fromisoformat(txn_date.replace('Z', '+00:00'))

            date_key = txn_date.date()
            txns_by_date[date_key].append(txn)

        # Iterate through each day
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            # Process transactions for this date
            if current_date in txns_by_date:
                for txn in txns_by_date[current_date]:
                    ticker = txn['ticker']
                    quantity = txn['quantity']
                    price = txn['price']
                    commission = txn.get('commission', 0.0)
                    txn_type = txn['transaction_type']

                    if txn_type == 'buy':
                        positions[ticker]['quantity'] += quantity
                        positions[ticker]['cost_basis'] += (quantity * price) + commission
                        cash_flows[current_date] -= (quantity * price) + commission
                    elif txn_type == 'sell':
                        if positions[ticker]['quantity'] > 0:
                            # Reduce position using FIFO
                            cost_reduction = (quantity / positions[ticker]['quantity']) * positions[ticker]['cost_basis']
                            positions[ticker]['quantity'] -= quantity
                            positions[ticker]['cost_basis'] -= cost_reduction
                            cash_flows[current_date] += (quantity * price) - commission
                    elif txn_type == 'dividend':
                        cash_flows[current_date] += (quantity * price)

            # Calculate portfolio value for this date
            portfolio_value = 0.0
            for ticker, position in positions.items():
                if position['quantity'] > 0:
                    # Use current price as proxy (in real implementation, would use historical prices)
                    price = current_prices.get(ticker, 0.0)
                    portfolio_value += position['quantity'] * price

            # Add cumulative cash flows
            total_cash_flow = sum(cash_flows.values())

            if portfolio_value > 0 or total_cash_flow != 0:
                daily_values.append({
                    'date': current_date.isoformat(),
                    'value': round(portfolio_value, 2),
                    'cash_flow': round(total_cash_flow, 2),
                    'invested': round(abs(total_cash_flow), 2)
                })

            current_date += timedelta(days=1)

        return daily_values

    def _calculate_daily_returns(
        self,
        daily_values: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate daily returns"""
        if len(daily_values) < 2:
            return []

        daily_returns = []
        for i in range(1, len(daily_values)):
            prev_value = daily_values[i-1]['value']
            curr_value = daily_values[i]['value']

            if prev_value > 0:
                daily_return = ((curr_value - prev_value) / prev_value) * 100
            else:
                daily_return = 0.0

            daily_returns.append({
                'date': daily_values[i]['date'],
                'return': round(daily_return, 4)
            })

        return daily_returns

    def _calculate_cumulative_returns(
        self,
        daily_returns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate cumulative returns"""
        cumulative_returns = []
        cumulative = 0.0

        for daily_return in daily_returns:
            cumulative = ((1 + cumulative / 100) * (1 + daily_return['return'] / 100) - 1) * 100

            cumulative_returns.append({
                'date': daily_return['date'],
                'cumulative_return': round(cumulative, 2)
            })

        return cumulative_returns

    def _calculate_period_returns(
        self,
        daily_values: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate returns for different time periods"""
        if not daily_values or len(daily_values) < 2:
            return {
                '1_day': 0.0,
                '1_week': 0.0,
                '1_month': 0.0,
                '3_months': 0.0,
                '6_months': 0.0,
                '1_year': 0.0,
                'ytd': 0.0
            }

        latest = daily_values[-1]
        latest_value = latest['value']
        latest_date = datetime.fromisoformat(latest['date'])

        period_returns = {}

        # Helper function to find value at specific date
        def find_value_at_date(target_date: datetime) -> Optional[float]:
            for dv in reversed(daily_values):
                dv_date = datetime.fromisoformat(dv['date'])
                if dv_date <= target_date:
                    return dv['value']
            return None

        # 1 day
        if len(daily_values) >= 2:
            prev_value = daily_values[-2]['value']
            period_returns['1_day'] = self._calculate_return(prev_value, latest_value)
        else:
            period_returns['1_day'] = 0.0

        # 1 week
        week_ago = latest_date - timedelta(days=7)
        week_ago_value = find_value_at_date(week_ago)
        period_returns['1_week'] = self._calculate_return(week_ago_value, latest_value) if week_ago_value else 0.0

        # 1 month
        month_ago = latest_date - timedelta(days=30)
        month_ago_value = find_value_at_date(month_ago)
        period_returns['1_month'] = self._calculate_return(month_ago_value, latest_value) if month_ago_value else 0.0

        # 3 months
        three_months_ago = latest_date - timedelta(days=90)
        three_months_value = find_value_at_date(three_months_ago)
        period_returns['3_months'] = self._calculate_return(three_months_value, latest_value) if three_months_value else 0.0

        # 6 months
        six_months_ago = latest_date - timedelta(days=180)
        six_months_value = find_value_at_date(six_months_ago)
        period_returns['6_months'] = self._calculate_return(six_months_value, latest_value) if six_months_value else 0.0

        # 1 year
        year_ago = latest_date - timedelta(days=365)
        year_ago_value = find_value_at_date(year_ago)
        period_returns['1_year'] = self._calculate_return(year_ago_value, latest_value) if year_ago_value else 0.0

        # YTD
        ytd_start = datetime(latest_date.year, 1, 1)
        ytd_value = find_value_at_date(ytd_start)
        period_returns['ytd'] = self._calculate_return(ytd_value, latest_value) if ytd_value else 0.0

        return period_returns

    def _calculate_return(self, old_value: Optional[float], new_value: float) -> float:
        """Calculate percentage return"""
        if old_value is None or old_value == 0:
            return 0.0
        return round(((new_value - old_value) / old_value) * 100, 2)

    def _calculate_annualized_return(
        self,
        daily_values: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Calculate annualized return"""
        if not daily_values or len(daily_values) < 2:
            return 0.0

        first_value = daily_values[0]['value']
        last_value = daily_values[-1]['value']

        if first_value <= 0:
            return 0.0

        # Calculate total return
        total_return = (last_value - first_value) / first_value

        # Calculate number of years
        days = (end_date - start_date).days
        if days <= 0:
            return 0.0

        years = days / 365.25

        # Annualize
        if years > 0:
            annualized = (((1 + total_return) ** (1 / years)) - 1) * 100
            return annualized

        return 0.0
