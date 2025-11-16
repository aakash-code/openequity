"""
Technical Indicators Service
Calculates 20+ technical indicators for price analysis
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime


class TechnicalIndicators:
    """Service for calculating technical indicators"""

    @staticmethod
    def validate_data(data: List[float], min_length: int = 1) -> None:
        """Validate input data"""
        if not data or len(data) < min_length:
            raise ValueError(f"Insufficient data: need at least {min_length} periods")

    # ==================== Moving Averages ====================

    @staticmethod
    def sma(data: List[float], period: int = 20) -> List[Optional[float]]:
        """
        Simple Moving Average

        Args:
            data: Price data (typically close prices)
            period: Number of periods

        Returns:
            List of SMA values (None for insufficient data points)
        """
        TechnicalIndicators.validate_data(data, period)

        result = [None] * (period - 1)
        for i in range(period - 1, len(data)):
            result.append(sum(data[i - period + 1:i + 1]) / period)

        return result

    @staticmethod
    def ema(data: List[float], period: int = 20) -> List[Optional[float]]:
        """
        Exponential Moving Average

        Args:
            data: Price data
            period: Number of periods

        Returns:
            List of EMA values
        """
        TechnicalIndicators.validate_data(data, period)

        multiplier = 2 / (period + 1)
        result = [None] * (period - 1)

        # First EMA is SMA
        result.append(sum(data[:period]) / period)

        # Calculate subsequent EMAs
        for i in range(period, len(data)):
            ema_value = (data[i] - result[-1]) * multiplier + result[-1]
            result.append(ema_value)

        return result

    @staticmethod
    def wma(data: List[float], period: int = 20) -> List[Optional[float]]:
        """
        Weighted Moving Average

        Args:
            data: Price data
            period: Number of periods

        Returns:
            List of WMA values
        """
        TechnicalIndicators.validate_data(data, period)

        weights = np.arange(1, period + 1)
        result = [None] * (period - 1)

        for i in range(period - 1, len(data)):
            window = data[i - period + 1:i + 1]
            wma_value = np.dot(window, weights) / weights.sum()
            result.append(float(wma_value))

        return result

    # ==================== Momentum Indicators ====================

    @staticmethod
    def rsi(data: List[float], period: int = 14) -> List[Optional[float]]:
        """
        Relative Strength Index

        Args:
            data: Price data
            period: Number of periods

        Returns:
            List of RSI values (0-100)
        """
        TechnicalIndicators.validate_data(data, period + 1)

        # Calculate price changes
        deltas = [data[i] - data[i - 1] for i in range(1, len(data))]

        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        result = [None] * period

        # Initial average gain/loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100 - (100 / (1 + rs)))

        # Calculate subsequent RSI values
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

            if avg_loss == 0:
                result.append(100.0)
            else:
                rs = avg_gain / avg_loss
                result.append(100 - (100 / (1 + rs)))

        return result

    @staticmethod
    def stochastic(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[List[Optional[float]], List[Optional[float]]]:
        """
        Stochastic Oscillator (%K and %D)

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            k_period: %K period
            d_period: %D period (SMA of %K)

        Returns:
            Tuple of (%K values, %D values)
        """
        TechnicalIndicators.validate_data(closes, k_period)

        k_values = [None] * (k_period - 1)

        for i in range(k_period - 1, len(closes)):
            window_high = max(highs[i - k_period + 1:i + 1])
            window_low = min(lows[i - k_period + 1:i + 1])

            if window_high == window_low:
                k_values.append(50.0)
            else:
                k = ((closes[i] - window_low) / (window_high - window_low)) * 100
                k_values.append(k)

        # %D is SMA of %K
        d_values = TechnicalIndicators.sma([k for k in k_values if k is not None], d_period)
        d_values = [None] * (len(k_values) - len(d_values)) + d_values

        return k_values, d_values

    @staticmethod
    def williams_r(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> List[Optional[float]]:
        """
        Williams %R

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            period: Number of periods

        Returns:
            List of Williams %R values (-100 to 0)
        """
        TechnicalIndicators.validate_data(closes, period)

        result = [None] * (period - 1)

        for i in range(period - 1, len(closes)):
            window_high = max(highs[i - period + 1:i + 1])
            window_low = min(lows[i - period + 1:i + 1])

            if window_high == window_low:
                result.append(-50.0)
            else:
                wr = ((window_high - closes[i]) / (window_high - window_low)) * -100
                result.append(wr)

        return result

    @staticmethod
    def roc(data: List[float], period: int = 12) -> List[Optional[float]]:
        """
        Rate of Change

        Args:
            data: Price data
            period: Number of periods

        Returns:
            List of ROC values (percentage)
        """
        TechnicalIndicators.validate_data(data, period + 1)

        result = [None] * period

        for i in range(period, len(data)):
            if data[i - period] == 0:
                result.append(0.0)
            else:
                roc_value = ((data[i] - data[i - period]) / data[i - period]) * 100
                result.append(roc_value)

        return result

    # ==================== Volatility Indicators ====================

    @staticmethod
    def bollinger_bands(
        data: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """
        Bollinger Bands

        Args:
            data: Price data
            period: Number of periods
            std_dev: Number of standard deviations

        Returns:
            Tuple of (upper band, middle band, lower band)
        """
        TechnicalIndicators.validate_data(data, period)

        middle_band = TechnicalIndicators.sma(data, period)

        upper_band = [None] * (period - 1)
        lower_band = [None] * (period - 1)

        for i in range(period - 1, len(data)):
            window = data[i - period + 1:i + 1]
            std = np.std(window)

            upper_band.append(middle_band[i] + (std_dev * std))
            lower_band.append(middle_band[i] - (std_dev * std))

        return upper_band, middle_band, lower_band

    @staticmethod
    def atr(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> List[Optional[float]]:
        """
        Average True Range

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            period: Number of periods

        Returns:
            List of ATR values
        """
        TechnicalIndicators.validate_data(closes, period + 1)

        # Calculate True Range
        tr_values = [None]

        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i - 1])
            low_close = abs(lows[i] - closes[i - 1])

            tr = max(high_low, high_close, low_close)
            tr_values.append(tr)

        # Calculate ATR (smoothed average of TR)
        result = [None] * period

        # First ATR is simple average
        first_atr = sum([tr for tr in tr_values[1:period + 1]]) / period
        result.append(first_atr)

        # Subsequent ATRs are smoothed
        for i in range(period + 1, len(tr_values)):
            atr_value = (result[-1] * (period - 1) + tr_values[i]) / period
            result.append(atr_value)

        return result

    # ==================== Trend Indicators ====================

    @staticmethod
    def macd(
        data: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """
        MACD (Moving Average Convergence Divergence)

        Args:
            data: Price data
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period

        Returns:
            Tuple of (MACD line, signal line, histogram)
        """
        TechnicalIndicators.validate_data(data, slow_period)

        # Calculate fast and slow EMAs
        fast_ema = TechnicalIndicators.ema(data, fast_period)
        slow_ema = TechnicalIndicators.ema(data, slow_period)

        # Calculate MACD line
        macd_line = []
        for i in range(len(data)):
            if fast_ema[i] is not None and slow_ema[i] is not None:
                macd_line.append(fast_ema[i] - slow_ema[i])
            else:
                macd_line.append(None)

        # Calculate signal line (EMA of MACD)
        macd_values_only = [m for m in macd_line if m is not None]
        signal_line_values = TechnicalIndicators.ema(macd_values_only, signal_period)

        # Pad signal line with None values
        none_count = len(macd_line) - len(signal_line_values)
        signal_line = [None] * none_count + signal_line_values

        # Calculate histogram
        histogram = []
        for i in range(len(macd_line)):
            if macd_line[i] is not None and signal_line[i] is not None:
                histogram.append(macd_line[i] - signal_line[i])
            else:
                histogram.append(None)

        return macd_line, signal_line, histogram

    @staticmethod
    def adx(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> List[Optional[float]]:
        """
        Average Directional Index

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            period: Number of periods

        Returns:
            List of ADX values (0-100)
        """
        TechnicalIndicators.validate_data(closes, period * 2)

        # Calculate +DM and -DM
        plus_dm = [0]
        minus_dm = [0]

        for i in range(1, len(highs)):
            high_diff = highs[i] - highs[i - 1]
            low_diff = lows[i - 1] - lows[i]

            plus_dm.append(high_diff if high_diff > low_diff and high_diff > 0 else 0)
            minus_dm.append(low_diff if low_diff > high_diff and low_diff > 0 else 0)

        # Calculate ATR
        atr = TechnicalIndicators.atr(highs, lows, closes, period)

        # Calculate smoothed +DM and -DM
        smoothed_plus_dm = [None] * period
        smoothed_minus_dm = [None] * period

        smoothed_plus_dm.append(sum(plus_dm[1:period + 1]))
        smoothed_minus_dm.append(sum(minus_dm[1:period + 1]))

        for i in range(period + 1, len(plus_dm)):
            smoothed_plus_dm.append(smoothed_plus_dm[-1] - (smoothed_plus_dm[-1] / period) + plus_dm[i])
            smoothed_minus_dm.append(smoothed_minus_dm[-1] - (smoothed_minus_dm[-1] / period) + minus_dm[i])

        # Calculate +DI and -DI
        plus_di = []
        minus_di = []

        for i in range(len(atr)):
            if atr[i] is not None and atr[i] > 0 and smoothed_plus_dm[i] is not None:
                plus_di.append((smoothed_plus_dm[i] / atr[i]) * 100)
                minus_di.append((smoothed_minus_dm[i] / atr[i]) * 100)
            else:
                plus_di.append(None)
                minus_di.append(None)

        # Calculate DX
        dx = []
        for i in range(len(plus_di)):
            if plus_di[i] is not None and minus_di[i] is not None:
                di_sum = plus_di[i] + minus_di[i]
                if di_sum > 0:
                    dx.append(abs(plus_di[i] - minus_di[i]) / di_sum * 100)
                else:
                    dx.append(0)
            else:
                dx.append(None)

        # Calculate ADX (smoothed DX)
        dx_values_only = [d for d in dx if d is not None]
        if len(dx_values_only) < period:
            return [None] * len(closes)

        adx_result = [None] * (len(dx) - len(dx_values_only))
        adx_result += [None] * (period - 1)

        # First ADX
        adx_result.append(sum(dx_values_only[:period]) / period)

        # Smoothed ADX
        dx_index = period
        for i in range(len(dx_values_only) - period):
            adx_value = (adx_result[-1] * (period - 1) + dx_values_only[dx_index]) / period
            adx_result.append(adx_value)
            dx_index += 1

        return adx_result

    # ==================== Volume Indicators ====================

    @staticmethod
    def obv(closes: List[float], volumes: List[float]) -> List[float]:
        """
        On-Balance Volume

        Args:
            closes: Close prices
            volumes: Volume data

        Returns:
            List of OBV values
        """
        TechnicalIndicators.validate_data(closes, 2)

        result = [volumes[0]]

        for i in range(1, len(closes)):
            if closes[i] > closes[i - 1]:
                result.append(result[-1] + volumes[i])
            elif closes[i] < closes[i - 1]:
                result.append(result[-1] - volumes[i])
            else:
                result.append(result[-1])

        return result

    @staticmethod
    def vwap(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        volumes: List[float]
    ) -> List[float]:
        """
        Volume Weighted Average Price

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            volumes: Volume data

        Returns:
            List of VWAP values
        """
        TechnicalIndicators.validate_data(closes, 1)

        cumulative_tpv = 0  # Typical Price × Volume
        cumulative_volume = 0
        result = []

        for i in range(len(closes)):
            typical_price = (highs[i] + lows[i] + closes[i]) / 3
            tpv = typical_price * volumes[i]

            cumulative_tpv += tpv
            cumulative_volume += volumes[i]

            if cumulative_volume > 0:
                result.append(cumulative_tpv / cumulative_volume)
            else:
                result.append(closes[i])

        return result

    # ==================== Helper Methods ====================

    @staticmethod
    def calculate_all_indicators(
        ohlcv_data: List[Dict[str, Any]],
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate multiple indicators at once

        Args:
            ohlcv_data: List of OHLCV dictionaries with keys:
                       'open', 'high', 'low', 'close', 'volume', 'timestamp'
            indicators: List of indicator names to calculate (default: all)

        Returns:
            Dictionary with calculated indicators
        """
        if not ohlcv_data:
            return {}

        # Extract price arrays
        opens = [bar['open'] for bar in ohlcv_data]
        highs = [bar['high'] for bar in ohlcv_data]
        lows = [bar['low'] for bar in ohlcv_data]
        closes = [bar['close'] for bar in ohlcv_data]
        volumes = [bar['volume'] for bar in ohlcv_data]
        timestamps = [bar.get('timestamp', bar.get('date', '')) for bar in ohlcv_data]

        result = {
            'timestamps': timestamps,
            'ohlcv': ohlcv_data,
            'indicators': {}
        }

        # Calculate requested indicators (or all if not specified)
        all_indicators = indicators is None

        # Moving Averages
        if all_indicators or 'sma_20' in indicators:
            result['indicators']['sma_20'] = TechnicalIndicators.sma(closes, 20)
        if all_indicators or 'sma_50' in indicators:
            result['indicators']['sma_50'] = TechnicalIndicators.sma(closes, 50)
        if all_indicators or 'ema_12' in indicators:
            result['indicators']['ema_12'] = TechnicalIndicators.ema(closes, 12)
        if all_indicators or 'ema_26' in indicators:
            result['indicators']['ema_26'] = TechnicalIndicators.ema(closes, 26)

        # Momentum
        if all_indicators or 'rsi' in indicators:
            result['indicators']['rsi'] = TechnicalIndicators.rsi(closes, 14)
        if all_indicators or 'stochastic' in indicators:
            k, d = TechnicalIndicators.stochastic(highs, lows, closes)
            result['indicators']['stochastic_k'] = k
            result['indicators']['stochastic_d'] = d
        if all_indicators or 'williams_r' in indicators:
            result['indicators']['williams_r'] = TechnicalIndicators.williams_r(highs, lows, closes)
        if all_indicators or 'roc' in indicators:
            result['indicators']['roc'] = TechnicalIndicators.roc(closes, 12)

        # Volatility
        if all_indicators or 'bollinger_bands' in indicators:
            upper, middle, lower = TechnicalIndicators.bollinger_bands(closes)
            result['indicators']['bb_upper'] = upper
            result['indicators']['bb_middle'] = middle
            result['indicators']['bb_lower'] = lower
        if all_indicators or 'atr' in indicators:
            result['indicators']['atr'] = TechnicalIndicators.atr(highs, lows, closes)

        # Trend
        if all_indicators or 'macd' in indicators:
            macd_line, signal, histogram = TechnicalIndicators.macd(closes)
            result['indicators']['macd_line'] = macd_line
            result['indicators']['macd_signal'] = signal
            result['indicators']['macd_histogram'] = histogram
        if all_indicators or 'adx' in indicators:
            result['indicators']['adx'] = TechnicalIndicators.adx(highs, lows, closes)

        # Volume
        if all_indicators or 'obv' in indicators:
            result['indicators']['obv'] = TechnicalIndicators.obv(closes, volumes)
        if all_indicators or 'vwap' in indicators:
            result['indicators']['vwap'] = TechnicalIndicators.vwap(highs, lows, closes, volumes)

        return result
