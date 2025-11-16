"""
Benchmark Comparison Service
Compares portfolio performance against market benchmarks
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import statistics


class BenchmarkComparisonService:
    """Service for comparing portfolio against benchmarks"""

    # Available benchmarks
    BENCHMARKS = {
        'SPY': {'name': 'S&P 500', 'description': 'US Large Cap Index'},
        'QQQ': {'name': 'NASDAQ-100', 'description': 'US Tech Index'},
        'IWM': {'name': 'Russell 2000', 'description': 'US Small Cap Index'},
        'NIFTY50': {'name': 'NIFTY 50', 'description': 'Indian Large Cap Index'},
        'SENSEX': {'name': 'BSE SENSEX', 'description': 'Bombay Stock Exchange Index'},
    }

    def compare_to_benchmark(
        self,
        portfolio_returns: List[Dict[str, Any]],
        portfolio_values: List[Dict[str, Any]],
        benchmark_symbol: str = 'SPY',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Compare portfolio performance to a benchmark

        Args:
            portfolio_returns: List of portfolio daily returns
            portfolio_values: List of portfolio daily values
            benchmark_symbol: Symbol of benchmark to compare against
            start_date: Start date for comparison
            end_date: End date for comparison

        Returns:
            Dictionary containing comparison metrics and data
        """
        if not portfolio_returns or not portfolio_values:
            return self._empty_comparison()

        # Get benchmark data
        benchmark_data = self._get_benchmark_data(
            benchmark_symbol,
            start_date or datetime.fromisoformat(portfolio_values[0]['date']),
            end_date or datetime.fromisoformat(portfolio_values[-1]['date'])
        )

        if not benchmark_data:
            return self._empty_comparison()

        # Align portfolio and benchmark data by date
        aligned_data = self._align_data(portfolio_returns, benchmark_data)

        if not aligned_data:
            return self._empty_comparison()

        portfolio_aligned = [d['portfolio_return'] for d in aligned_data]
        benchmark_aligned = [d['benchmark_return'] for d in aligned_data]

        # Calculate relative performance
        relative_performance = self._calculate_relative_performance(
            portfolio_aligned, benchmark_aligned
        )

        # Calculate correlation
        correlation = self._calculate_correlation(portfolio_aligned, benchmark_aligned)

        # Calculate tracking error
        tracking_error = self._calculate_tracking_error(portfolio_aligned, benchmark_aligned)

        # Calculate information ratio
        information_ratio = self._calculate_information_ratio(
            portfolio_aligned, benchmark_aligned, tracking_error
        )

        # Calculate cumulative returns for both
        portfolio_cumulative = self._calculate_cumulative_returns(portfolio_aligned)
        benchmark_cumulative = self._calculate_cumulative_returns(benchmark_aligned)

        # Calculate period comparison
        period_comparison = self._calculate_period_comparison(
            portfolio_values, benchmark_data
        )

        # Get benchmark info
        benchmark_info = self.BENCHMARKS.get(benchmark_symbol, {
            'name': benchmark_symbol,
            'description': 'Market Benchmark'
        })

        return {
            'benchmark_symbol': benchmark_symbol,
            'benchmark_name': benchmark_info['name'],
            'benchmark_description': benchmark_info['description'],
            'relative_performance': relative_performance,
            'correlation': round(correlation, 2),
            'tracking_error': round(tracking_error, 2),
            'information_ratio': round(information_ratio, 2),
            'portfolio_cumulative_return': round(portfolio_cumulative[-1] if portfolio_cumulative else 0.0, 2),
            'benchmark_cumulative_return': round(benchmark_cumulative[-1] if benchmark_cumulative else 0.0, 2),
            'excess_return': round(
                (portfolio_cumulative[-1] if portfolio_cumulative else 0.0) -
                (benchmark_cumulative[-1] if benchmark_cumulative else 0.0),
                2
            ),
            'aligned_data': aligned_data,
            'portfolio_cumulative': [
                {'date': aligned_data[i]['date'], 'cumulative_return': round(ret, 2)}
                for i, ret in enumerate(portfolio_cumulative)
            ],
            'benchmark_cumulative': [
                {'date': aligned_data[i]['date'], 'cumulative_return': round(ret, 2)}
                for i, ret in enumerate(benchmark_cumulative)
            ],
            'period_comparison': period_comparison
        }

    def _empty_comparison(self) -> Dict[str, Any]:
        """Return empty comparison structure"""
        return {
            'benchmark_symbol': '',
            'benchmark_name': '',
            'benchmark_description': '',
            'relative_performance': 0.0,
            'correlation': 0.0,
            'tracking_error': 0.0,
            'information_ratio': 0.0,
            'portfolio_cumulative_return': 0.0,
            'benchmark_cumulative_return': 0.0,
            'excess_return': 0.0,
            'aligned_data': [],
            'portfolio_cumulative': [],
            'benchmark_cumulative': [],
            'period_comparison': {}
        }

    def _get_benchmark_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get benchmark return data

        NOTE: In production, this would fetch real market data from an API.
        For demo purposes, we generate synthetic benchmark returns.
        """
        benchmark_data = []
        current_date = start_date.date()
        end_date_only = end_date.date()

        # Benchmark characteristics (annualized)
        benchmarks_params = {
            'SPY': {'mean_return': 0.10, 'volatility': 0.15},      # S&P 500: 10% return, 15% vol
            'QQQ': {'mean_return': 0.15, 'volatility': 0.20},      # NASDAQ: 15% return, 20% vol
            'IWM': {'mean_return': 0.08, 'volatility': 0.22},      # Russell 2000: 8% return, 22% vol
            'NIFTY50': {'mean_return': 0.12, 'volatility': 0.18},  # NIFTY 50: 12% return, 18% vol
            'SENSEX': {'mean_return': 0.11, 'volatility': 0.17},   # SENSEX: 11% return, 17% vol
        }

        params = benchmarks_params.get(symbol, {'mean_return': 0.08, 'volatility': 0.15})

        # Convert to daily parameters
        daily_mean = params['mean_return'] / 252
        daily_std = params['volatility'] / (252 ** 0.5)

        # Generate synthetic returns
        random.seed(42)  # For reproducibility
        while current_date <= end_date_only:
            # Generate random return from normal distribution
            daily_return = random.gauss(daily_mean, daily_std) * 100  # Convert to percentage

            benchmark_data.append({
                'date': current_date.isoformat(),
                'return': round(daily_return, 4)
            })

            current_date += timedelta(days=1)

        return benchmark_data

    def _align_data(
        self,
        portfolio_returns: List[Dict[str, Any]],
        benchmark_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Align portfolio and benchmark data by date"""
        # Create dictionaries for quick lookup
        portfolio_dict = {r['date']: r['return'] for r in portfolio_returns}
        benchmark_dict = {b['date']: b['return'] for b in benchmark_data}

        # Find common dates
        common_dates = sorted(set(portfolio_dict.keys()) & set(benchmark_dict.keys()))

        aligned = []
        for date in common_dates:
            aligned.append({
                'date': date,
                'portfolio_return': portfolio_dict[date],
                'benchmark_return': benchmark_dict[date]
            })

        return aligned

    def _calculate_relative_performance(
        self,
        portfolio_returns: List[float],
        benchmark_returns: List[float]
    ) -> float:
        """Calculate average relative performance (outperformance)"""
        if not portfolio_returns or not benchmark_returns:
            return 0.0

        relative_returns = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
        return statistics.mean(relative_returns)

    def _calculate_correlation(
        self,
        portfolio_returns: List[float],
        benchmark_returns: List[float]
    ) -> float:
        """Calculate correlation between portfolio and benchmark"""
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return 0.0

        mean_portfolio = statistics.mean(portfolio_returns)
        mean_benchmark = statistics.mean(benchmark_returns)

        # Calculate covariance
        covariance = sum(
            (p - mean_portfolio) * (b - mean_benchmark)
            for p, b in zip(portfolio_returns, benchmark_returns)
        ) / (len(portfolio_returns) - 1)

        # Calculate standard deviations
        std_portfolio = statistics.stdev(portfolio_returns)
        std_benchmark = statistics.stdev(benchmark_returns)

        if std_portfolio == 0 or std_benchmark == 0:
            return 0.0

        correlation = covariance / (std_portfolio * std_benchmark)

        return correlation

    def _calculate_tracking_error(
        self,
        portfolio_returns: List[float],
        benchmark_returns: List[float]
    ) -> float:
        """Calculate tracking error (volatility of excess returns)"""
        if not portfolio_returns or not benchmark_returns:
            return 0.0

        excess_returns = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]

        if len(excess_returns) < 2:
            return 0.0

        # Annualize tracking error
        tracking_error = statistics.stdev(excess_returns) * (252 ** 0.5)

        return tracking_error

    def _calculate_information_ratio(
        self,
        portfolio_returns: List[float],
        benchmark_returns: List[float],
        tracking_error: float
    ) -> float:
        """Calculate information ratio (excess return / tracking error)"""
        if tracking_error == 0:
            return 0.0

        excess_returns = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
        mean_excess = statistics.mean(excess_returns)

        # Annualize
        annualized_excess = mean_excess * 252

        information_ratio = annualized_excess / tracking_error

        return information_ratio

    def _calculate_cumulative_returns(self, returns: List[float]) -> List[float]:
        """Calculate cumulative returns from daily returns"""
        cumulative = []
        cum_return = 0.0

        for ret in returns:
            cum_return = ((1 + cum_return / 100) * (1 + ret / 100) - 1) * 100
            cumulative.append(cum_return)

        return cumulative

    def _calculate_period_comparison(
        self,
        portfolio_values: List[Dict[str, Any]],
        benchmark_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate performance comparison for different periods"""
        if not portfolio_values or not benchmark_data:
            return {}

        latest_date = datetime.fromisoformat(portfolio_values[-1]['date'])

        periods = {
            '1_week': timedelta(days=7),
            '1_month': timedelta(days=30),
            '3_months': timedelta(days=90),
            '6_months': timedelta(days=180),
            '1_year': timedelta(days=365),
        }

        period_comparison = {}

        for period_name, delta in periods.items():
            start_date = latest_date - delta

            # Get portfolio return for period
            portfolio_return = self._get_period_return(
                portfolio_values, start_date, latest_date
            )

            # Get benchmark return for period
            benchmark_return = self._get_benchmark_period_return(
                benchmark_data, start_date, latest_date
            )

            period_comparison[period_name] = {
                'portfolio_return': round(portfolio_return, 2),
                'benchmark_return': round(benchmark_return, 2),
                'excess_return': round(portfolio_return - benchmark_return, 2)
            }

        return period_comparison

    def _get_period_return(
        self,
        values: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Calculate return for a specific period"""
        start_value = None
        end_value = None

        for v in values:
            v_date = datetime.fromisoformat(v['date'])
            if v_date >= start_date and start_value is None:
                start_value = v['value']
            if v_date <= end_date:
                end_value = v['value']

        if start_value is None or end_value is None or start_value == 0:
            return 0.0

        return ((end_value - start_value) / start_value) * 100

    def _get_benchmark_period_return(
        self,
        benchmark_data: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Calculate benchmark return for a specific period"""
        period_returns = []

        for b in benchmark_data:
            b_date = datetime.fromisoformat(b['date'])
            if start_date <= b_date <= end_date:
                period_returns.append(b['return'])

        if not period_returns:
            return 0.0

        # Calculate cumulative return
        cumulative = 0.0
        for ret in period_returns:
            cumulative = ((1 + cumulative / 100) * (1 + ret / 100) - 1) * 100

        return cumulative
