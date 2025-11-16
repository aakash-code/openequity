"""
Risk Metrics Service
Calculates portfolio risk metrics including Sharpe, Sortino, Beta, VaR, etc.
"""

from typing import List, Dict, Any, Optional
import statistics
import math


class RiskMetricsService:
    """Service for calculating portfolio risk metrics"""

    def calculate_risk_metrics(
        self,
        daily_returns: List[Dict[str, Any]],
        daily_values: List[Dict[str, Any]],
        benchmark_returns: Optional[List[float]] = None,
        risk_free_rate: float = 0.04  # 4% annual risk-free rate
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk metrics

        Args:
            daily_returns: List of daily return dictionaries
            daily_values: List of daily portfolio value dictionaries
            benchmark_returns: List of benchmark daily returns (for Beta/Alpha)
            risk_free_rate: Annual risk-free rate (default 4%)

        Returns:
            Dictionary containing all risk metrics
        """
        if not daily_returns or len(daily_returns) < 2:
            return self._empty_risk_metrics()

        # Extract return values
        returns = [r['return'] for r in daily_returns]

        # Calculate basic statistics
        mean_return = statistics.mean(returns)
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0.0

        # Annualize metrics
        trading_days = 252
        annualized_return = mean_return * trading_days
        annualized_volatility = std_dev * math.sqrt(trading_days)

        # Calculate Sharpe Ratio
        sharpe_ratio = self._calculate_sharpe_ratio(
            mean_return, std_dev, risk_free_rate, trading_days
        )

        # Calculate Sortino Ratio
        sortino_ratio = self._calculate_sortino_ratio(
            returns, mean_return, risk_free_rate, trading_days
        )

        # Calculate Maximum Drawdown
        max_drawdown = self._calculate_max_drawdown(daily_values)

        # Calculate Value at Risk (VaR)
        var_95 = self._calculate_var(returns, 0.95)
        var_99 = self._calculate_var(returns, 0.99)

        # Calculate Conditional VaR (CVaR / Expected Shortfall)
        cvar_95 = self._calculate_cvar(returns, 0.95)
        cvar_99 = self._calculate_cvar(returns, 0.99)

        # Calculate Calmar Ratio
        calmar_ratio = self._calculate_calmar_ratio(annualized_return, max_drawdown['max_drawdown_percent'])

        # Calculate Beta and Alpha (if benchmark provided)
        beta = 0.0
        alpha = 0.0
        correlation = 0.0
        if benchmark_returns and len(benchmark_returns) == len(returns):
            beta = self._calculate_beta(returns, benchmark_returns)
            alpha = self._calculate_alpha(
                mean_return, beta, statistics.mean(benchmark_returns), risk_free_rate, trading_days
            )
            correlation = self._calculate_correlation(returns, benchmark_returns)

        # Calculate up/down capture ratios (if benchmark provided)
        up_capture = 0.0
        down_capture = 0.0
        if benchmark_returns and len(benchmark_returns) == len(returns):
            up_capture, down_capture = self._calculate_capture_ratios(returns, benchmark_returns)

        # Calculate win rate
        win_rate = self._calculate_win_rate(returns)

        return {
            'annualized_return': round(annualized_return, 2),
            'annualized_volatility': round(annualized_volatility, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'max_drawdown': max_drawdown,
            'calmar_ratio': round(calmar_ratio, 2),
            'var_95': round(var_95, 2),
            'var_99': round(var_99, 2),
            'cvar_95': round(cvar_95, 2),
            'cvar_99': round(cvar_99, 2),
            'beta': round(beta, 2),
            'alpha': round(alpha, 2),
            'correlation': round(correlation, 2),
            'up_capture': round(up_capture, 2),
            'down_capture': round(down_capture, 2),
            'win_rate': round(win_rate, 2),
            'mean_daily_return': round(mean_return, 4),
            'daily_volatility': round(std_dev, 4)
        }

    def _empty_risk_metrics(self) -> Dict[str, Any]:
        """Return empty risk metrics structure"""
        return {
            'annualized_return': 0.0,
            'annualized_volatility': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'max_drawdown': {
                'max_drawdown_percent': 0.0,
                'max_drawdown_value': 0.0,
                'peak_date': None,
                'trough_date': None,
                'recovery_date': None,
                'drawdown_series': []
            },
            'calmar_ratio': 0.0,
            'var_95': 0.0,
            'var_99': 0.0,
            'cvar_95': 0.0,
            'cvar_99': 0.0,
            'beta': 0.0,
            'alpha': 0.0,
            'correlation': 0.0,
            'up_capture': 0.0,
            'down_capture': 0.0,
            'win_rate': 0.0,
            'mean_daily_return': 0.0,
            'daily_volatility': 0.0
        }

    def _calculate_sharpe_ratio(
        self,
        mean_return: float,
        std_dev: float,
        risk_free_rate: float,
        trading_days: int
    ) -> float:
        """Calculate Sharpe Ratio"""
        if std_dev == 0:
            return 0.0

        # Convert annual risk-free rate to daily
        daily_rf = risk_free_rate / trading_days

        # Calculate excess return
        excess_return = mean_return - daily_rf

        # Annualize Sharpe ratio
        sharpe = (excess_return / std_dev) * math.sqrt(trading_days)

        return sharpe

    def _calculate_sortino_ratio(
        self,
        returns: List[float],
        mean_return: float,
        risk_free_rate: float,
        trading_days: int
    ) -> float:
        """Calculate Sortino Ratio (uses downside deviation)"""
        # Calculate downside deviation (only negative returns)
        negative_returns = [r for r in returns if r < 0]

        if not negative_returns:
            return 0.0

        downside_dev = statistics.stdev(negative_returns) if len(negative_returns) > 1 else 0.0

        if downside_dev == 0:
            return 0.0

        # Convert annual risk-free rate to daily
        daily_rf = risk_free_rate / trading_days

        # Calculate excess return
        excess_return = mean_return - daily_rf

        # Annualize Sortino ratio
        sortino = (excess_return / downside_dev) * math.sqrt(trading_days)

        return sortino

    def _calculate_max_drawdown(
        self,
        daily_values: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate maximum drawdown"""
        if not daily_values:
            return {
                'max_drawdown_percent': 0.0,
                'max_drawdown_value': 0.0,
                'peak_date': None,
                'trough_date': None,
                'recovery_date': None,
                'drawdown_series': []
            }

        peak = daily_values[0]['value']
        peak_date = daily_values[0]['date']
        max_dd = 0.0
        max_dd_value = 0.0
        trough_date = None
        recovery_date = None
        drawdown_series = []

        for i, dv in enumerate(daily_values):
            value = dv['value']
            date = dv['date']

            # Update peak
            if value > peak:
                peak = value
                peak_date = date

            # Calculate drawdown
            if peak > 0:
                dd = ((value - peak) / peak) * 100
            else:
                dd = 0.0

            drawdown_series.append({
                'date': date,
                'drawdown_percent': round(dd, 2)
            })

            # Update max drawdown
            if dd < max_dd:
                max_dd = dd
                max_dd_value = value - peak
                trough_date = date
                recovery_date = None
            elif dd == 0.0 and trough_date is not None and recovery_date is None:
                recovery_date = date

        return {
            'max_drawdown_percent': round(abs(max_dd), 2),
            'max_drawdown_value': round(abs(max_dd_value), 2),
            'peak_date': peak_date,
            'trough_date': trough_date,
            'recovery_date': recovery_date,
            'drawdown_series': drawdown_series
        }

    def _calculate_var(self, returns: List[float], confidence: float) -> float:
        """Calculate Value at Risk at given confidence level"""
        if not returns:
            return 0.0

        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        index = max(0, min(index, len(sorted_returns) - 1))

        return sorted_returns[index]

    def _calculate_cvar(self, returns: List[float], confidence: float) -> float:
        """Calculate Conditional VaR (Expected Shortfall)"""
        if not returns:
            return 0.0

        var = self._calculate_var(returns, confidence)

        # Average of returns worse than VaR
        tail_returns = [r for r in returns if r <= var]

        if not tail_returns:
            return var

        return statistics.mean(tail_returns)

    def _calculate_calmar_ratio(self, annualized_return: float, max_drawdown: float) -> float:
        """Calculate Calmar Ratio (return / max drawdown)"""
        if max_drawdown == 0:
            return 0.0

        return annualized_return / max_drawdown

    def _calculate_beta(self, returns: List[float], benchmark_returns: List[float]) -> float:
        """Calculate Beta (portfolio sensitivity to benchmark)"""
        if len(returns) != len(benchmark_returns) or len(returns) < 2:
            return 0.0

        # Calculate covariance
        mean_portfolio = statistics.mean(returns)
        mean_benchmark = statistics.mean(benchmark_returns)

        covariance = sum(
            (r - mean_portfolio) * (b - mean_benchmark)
            for r, b in zip(returns, benchmark_returns)
        ) / (len(returns) - 1)

        # Calculate benchmark variance
        benchmark_variance = statistics.variance(benchmark_returns)

        if benchmark_variance == 0:
            return 0.0

        beta = covariance / benchmark_variance

        return beta

    def _calculate_alpha(
        self,
        mean_return: float,
        beta: float,
        benchmark_mean: float,
        risk_free_rate: float,
        trading_days: int
    ) -> float:
        """Calculate Alpha (excess return over CAPM expected return)"""
        # Convert to daily risk-free rate
        daily_rf = risk_free_rate / trading_days

        # CAPM expected return
        expected_return = daily_rf + beta * (benchmark_mean - daily_rf)

        # Alpha is actual return minus expected return, annualized
        alpha = (mean_return - expected_return) * trading_days

        return alpha

    def _calculate_correlation(self, returns: List[float], benchmark_returns: List[float]) -> float:
        """Calculate correlation with benchmark"""
        if len(returns) != len(benchmark_returns) or len(returns) < 2:
            return 0.0

        mean_portfolio = statistics.mean(returns)
        mean_benchmark = statistics.mean(benchmark_returns)

        # Calculate covariance
        covariance = sum(
            (r - mean_portfolio) * (b - mean_benchmark)
            for r, b in zip(returns, benchmark_returns)
        ) / (len(returns) - 1)

        # Calculate standard deviations
        std_portfolio = statistics.stdev(returns)
        std_benchmark = statistics.stdev(benchmark_returns)

        if std_portfolio == 0 or std_benchmark == 0:
            return 0.0

        correlation = covariance / (std_portfolio * std_benchmark)

        return correlation

    def _calculate_capture_ratios(
        self,
        returns: List[float],
        benchmark_returns: List[float]
    ) -> tuple[float, float]:
        """Calculate up capture and down capture ratios"""
        if len(returns) != len(benchmark_returns):
            return 0.0, 0.0

        up_portfolio = []
        up_benchmark = []
        down_portfolio = []
        down_benchmark = []

        for r, b in zip(returns, benchmark_returns):
            if b > 0:
                up_portfolio.append(r)
                up_benchmark.append(b)
            elif b < 0:
                down_portfolio.append(r)
                down_benchmark.append(b)

        # Up capture ratio
        up_capture = 0.0
        if up_benchmark:
            avg_up_portfolio = statistics.mean(up_portfolio)
            avg_up_benchmark = statistics.mean(up_benchmark)
            if avg_up_benchmark != 0:
                up_capture = (avg_up_portfolio / avg_up_benchmark) * 100

        # Down capture ratio
        down_capture = 0.0
        if down_benchmark:
            avg_down_portfolio = statistics.mean(down_portfolio)
            avg_down_benchmark = statistics.mean(down_benchmark)
            if avg_down_benchmark != 0:
                down_capture = (avg_down_portfolio / avg_down_benchmark) * 100

        return up_capture, down_capture

    def _calculate_win_rate(self, returns: List[float]) -> float:
        """Calculate percentage of positive return days"""
        if not returns:
            return 0.0

        positive_days = sum(1 for r in returns if r > 0)
        win_rate = (positive_days / len(returns)) * 100

        return win_rate
