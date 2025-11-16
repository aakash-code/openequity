"""
Portfolio Analytics Service
Calculates portfolio performance, risk metrics, and allocations
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import math


class PortfolioAnalytics:
    """
    Comprehensive portfolio analytics including:
    - Returns calculation (total, annualized, per position)
    - Risk metrics (volatility, Sharpe ratio, max drawdown)
    - Asset allocation (by ticker, sector, etc.)
    - Performance attribution
    """

    def calculate_position_summary(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate current positions from transaction history

        Args:
            transactions: List of transactions (sorted by date)

        Returns:
            Dictionary of positions by ticker with quantity, cost basis, etc.
        """
        positions = defaultdict(lambda: {
            'quantity': 0.0,
            'total_cost': 0.0,
            'cost_basis': 0.0,
            'transactions': []
        })

        for txn in transactions:
            ticker = txn['ticker']
            quantity = txn['quantity']
            price = txn['price']
            commission = txn.get('commission', 0.0)
            txn_type = txn['transaction_type']

            if txn_type == 'buy':
                # Add to position
                positions[ticker]['quantity'] += quantity
                positions[ticker]['total_cost'] += (quantity * price) + commission
                positions[ticker]['transactions'].append(txn)

            elif txn_type == 'sell':
                # Reduce position
                positions[ticker]['quantity'] -= quantity
                # Reduce cost proportionally (FIFO method)
                if positions[ticker]['quantity'] > 0:
                    cost_per_share = positions[ticker]['total_cost'] / (positions[ticker]['quantity'] + quantity)
                    positions[ticker]['total_cost'] -= (quantity * cost_per_share)
                else:
                    positions[ticker]['total_cost'] = 0.0
                positions[ticker]['transactions'].append(txn)

        # Calculate cost basis for each position
        result = {}
        for ticker, pos in positions.items():
            if pos['quantity'] > 0:  # Only include active positions
                result[ticker] = {
                    'ticker': ticker,
                    'quantity': round(pos['quantity'], 4),
                    'total_cost': round(pos['total_cost'], 2),
                    'cost_basis': round(pos['total_cost'] / pos['quantity'], 2) if pos['quantity'] > 0 else 0,
                    'transaction_count': len(pos['transactions'])
                }

        return result

    def calculate_portfolio_value(
        self,
        positions: Dict[str, Dict[str, Any]],
        current_prices: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate current portfolio value

        Args:
            positions: Current positions by ticker
            current_prices: Current market prices by ticker

        Returns:
            Portfolio valuation metrics
        """
        total_value = 0.0
        total_cost = 0.0
        position_values = {}

        for ticker, position in positions.items():
            current_price = current_prices.get(ticker, 0.0)
            quantity = position['quantity']
            cost = position['total_cost']

            market_value = quantity * current_price
            unrealized_gain = market_value - cost
            unrealized_gain_pct = (unrealized_gain / cost * 100) if cost > 0 else 0

            position_values[ticker] = {
                'ticker': ticker,
                'quantity': quantity,
                'cost_basis': position['cost_basis'],
                'current_price': current_price,
                'market_value': round(market_value, 2),
                'total_cost': round(cost, 2),
                'unrealized_gain': round(unrealized_gain, 2),
                'unrealized_gain_percent': round(unrealized_gain_pct, 2),
                'weight': 0.0  # Will be calculated after total
            }

            total_value += market_value
            total_cost += cost

        # Calculate weights
        for ticker in position_values:
            if total_value > 0:
                position_values[ticker]['weight'] = round(
                    (position_values[ticker]['market_value'] / total_value) * 100, 2
                )

        total_gain = total_value - total_cost
        total_return_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0

        return {
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'total_gain': round(total_gain, 2),
            'total_return_percent': round(total_return_pct, 2),
            'position_count': len(position_values),
            'positions': position_values
        }

    def calculate_returns_over_time(
        self,
        transactions: List[Dict[str, Any]],
        price_history: Dict[str, List[Dict[str, Any]]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate time-weighted returns

        Args:
            transactions: Transaction history
            price_history: Historical prices by ticker
            start_date: Analysis start date
            end_date: Analysis end date (default: today)

        Returns:
            Time series of portfolio value and returns
        """
        # This is a simplified implementation
        # A complete implementation would calculate daily portfolio values
        # using transaction history and price data

        # For now, return basic structure
        return {
            'time_series': [],
            'total_return': 0.0,
            'annualized_return': 0.0
        }

    def calculate_sharpe_ratio(
        self,
        returns: List[float],
        risk_free_rate: float = 0.03
    ) -> Optional[float]:
        """
        Calculate Sharpe Ratio

        Sharpe = (Rp - Rf) / σp
        where Rp = portfolio return, Rf = risk-free rate, σp = std deviation

        Args:
            returns: List of periodic returns
            risk_free_rate: Annual risk-free rate (default: 3%)

        Returns:
            Sharpe ratio or None if insufficient data
        """
        if len(returns) < 2:
            return None

        mean_return = sum(returns) / len(returns)

        # Calculate standard deviation
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return None

        # Annualized Sharpe ratio (assuming daily returns)
        excess_return = mean_return - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe = (excess_return / std_dev) * math.sqrt(252)  # Annualized

        return round(sharpe, 2)

    def calculate_max_drawdown(
        self,
        portfolio_values: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate maximum drawdown

        Args:
            portfolio_values: Time series of portfolio values

        Returns:
            Maximum drawdown metrics
        """
        if len(portfolio_values) < 2:
            return {
                'max_drawdown': 0.0,
                'max_drawdown_percent': 0.0
            }

        peak = portfolio_values[0]
        max_dd = 0.0
        max_dd_pct = 0.0

        for value in portfolio_values:
            if value > peak:
                peak = value

            dd = peak - value
            dd_pct = (dd / peak * 100) if peak > 0 else 0

            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct

        return {
            'max_drawdown': round(max_dd, 2),
            'max_drawdown_percent': round(max_dd_pct, 2)
        }

    def calculate_asset_allocation(
        self,
        positions: Dict[str, Dict[str, Any]],
        company_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate asset allocation by various dimensions

        Args:
            positions: Current positions with market values
            company_data: Company metadata (sector, industry, etc.)

        Returns:
            Allocation breakdowns
        """
        total_value = sum(pos['market_value'] for pos in positions.values())

        # Allocation by sector
        sector_allocation = defaultdict(float)
        industry_allocation = defaultdict(float)
        exchange_allocation = defaultdict(float)

        for ticker, position in positions.items():
            market_value = position['market_value']
            weight = (market_value / total_value * 100) if total_value > 0 else 0

            company = company_data.get(ticker, {})
            sector = company.get('sector', 'Unknown')
            industry = company.get('industry', 'Unknown')
            exchange = company.get('exchange', 'Unknown')

            sector_allocation[sector] += weight
            industry_allocation[industry] += weight
            exchange_allocation[exchange] += weight

        return {
            'by_sector': [
                {'name': sector, 'weight': round(weight, 2)}
                for sector, weight in sorted(sector_allocation.items(), key=lambda x: -x[1])
            ],
            'by_industry': [
                {'name': industry, 'weight': round(weight, 2)}
                for industry, weight in sorted(industry_allocation.items(), key=lambda x: -x[1])
            ],
            'by_exchange': [
                {'name': exchange, 'weight': round(weight, 2)}
                for exchange, weight in sorted(exchange_allocation.items(), key=lambda x: -x[1])
            ]
        }

    def calculate_concentration_metrics(
        self,
        positions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate concentration metrics (diversification)

        Args:
            positions: Current positions with weights

        Returns:
            Concentration metrics
        """
        if not positions:
            return {
                'top_5_concentration': 0.0,
                'top_10_concentration': 0.0,
                'herfindahl_index': 0.0
            }

        # Sort by weight
        sorted_positions = sorted(
            positions.values(),
            key=lambda x: x['weight'],
            reverse=True
        )

        # Top N concentration
        top_5 = sum(p['weight'] for p in sorted_positions[:5])
        top_10 = sum(p['weight'] for p in sorted_positions[:10])

        # Herfindahl-Hirschman Index (sum of squared weights)
        hhi = sum((p['weight'] / 100) ** 2 for p in positions.values()) * 10000

        return {
            'top_5_concentration': round(top_5, 2),
            'top_10_concentration': round(top_10, 2),
            'herfindahl_index': round(hhi, 0),
            'position_count': len(positions)
        }

    def get_top_performers(
        self,
        positions: Dict[str, Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top performing positions

        Args:
            positions: Current positions
            limit: Number of top performers to return

        Returns:
            List of top performers
        """
        sorted_positions = sorted(
            positions.values(),
            key=lambda x: x.get('unrealized_gain_percent', 0),
            reverse=True
        )

        return sorted_positions[:limit]

    def get_worst_performers(
        self,
        positions: Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get worst performing positions

        Args:
            positions: Current positions
            limit: Number of worst performers to return

        Returns:
            List of worst performers
        """
        sorted_positions = sorted(
            positions.values(),
            key=lambda x: x.get('unrealized_gain_percent', 0)
        )

        return sorted_positions[:limit]
