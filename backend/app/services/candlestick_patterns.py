"""
Candlestick Pattern Detection Service
Identifies Japanese candlestick patterns for trading signals
"""

from typing import List, Dict, Any, Optional
import numpy as np


class CandlestickPatterns:
    """Service for detecting candlestick patterns"""

    @staticmethod
    def is_doji(open_price: float, close: float, high: float, low: float, threshold: float = 0.1) -> bool:
        """
        Check if candle is a Doji

        Args:
            open_price: Open price
            close: Close price
            high: High price
            low: Low price
            threshold: Body/range ratio threshold (default 0.1 = 10%)

        Returns:
            True if Doji pattern detected
        """
        body = abs(close - open_price)
        total_range = high - low

        if total_range == 0:
            return False

        body_ratio = body / total_range
        return body_ratio <= threshold

    @staticmethod
    def is_hammer(
        open_price: float,
        close: float,
        high: float,
        low: float,
        prev_trend: str = 'down'
    ) -> bool:
        """
        Check if candle is a Hammer (bullish reversal)

        Args:
            open_price: Open price
            close: Close price
            high: High price
            low: Low price
            prev_trend: Previous trend ('up' or 'down')

        Returns:
            True if Hammer pattern detected
        """
        if prev_trend != 'down':
            return False

        body = abs(close - open_price)
        total_range = high - low
        lower_shadow = min(open_price, close) - low
        upper_shadow = high - max(open_price, close)

        if total_range == 0:
            return False

        # Lower shadow should be at least 2x body
        # Upper shadow should be very small
        # Body should be in upper part of range
        return (
            lower_shadow >= body * 2 and
            upper_shadow <= body * 0.3 and
            body / total_range >= 0.1
        )

    @staticmethod
    def is_shooting_star(
        open_price: float,
        close: float,
        high: float,
        low: float,
        prev_trend: str = 'up'
    ) -> bool:
        """
        Check if candle is a Shooting Star (bearish reversal)

        Args:
            open_price: Open price
            close: Close price
            high: High price
            low: Low price
            prev_trend: Previous trend

        Returns:
            True if Shooting Star detected
        """
        if prev_trend != 'up':
            return False

        body = abs(close - open_price)
        total_range = high - low
        lower_shadow = min(open_price, close) - low
        upper_shadow = high - max(open_price, close)

        if total_range == 0:
            return False

        # Upper shadow should be at least 2x body
        # Lower shadow should be very small
        # Body should be in lower part of range
        return (
            upper_shadow >= body * 2 and
            lower_shadow <= body * 0.3 and
            body / total_range >= 0.1
        )

    @staticmethod
    def is_engulfing(
        prev_open: float,
        prev_close: float,
        curr_open: float,
        curr_close: float,
        pattern_type: str = 'bullish'
    ) -> bool:
        """
        Check if pattern is Engulfing

        Args:
            prev_open: Previous candle open
            prev_close: Previous candle close
            curr_open: Current candle open
            curr_close: Current candle close
            pattern_type: 'bullish' or 'bearish'

        Returns:
            True if Engulfing pattern detected
        """
        prev_is_bearish = prev_close < prev_open
        prev_is_bullish = prev_close > prev_open
        curr_is_bearish = curr_close < curr_open
        curr_is_bullish = curr_close > curr_open

        if pattern_type == 'bullish':
            # Previous red, current green and engulfs
            return (
                prev_is_bearish and
                curr_is_bullish and
                curr_close > prev_open and
                curr_open < prev_close
            )
        else:  # bearish
            # Previous green, current red and engulfs
            return (
                prev_is_bullish and
                curr_is_bearish and
                curr_close < prev_open and
                curr_open > prev_close
            )

    @staticmethod
    def is_morning_star(
        candle1_open: float,
        candle1_close: float,
        candle2_open: float,
        candle2_close: float,
        candle2_high: float,
        candle2_low: float,
        candle3_open: float,
        candle3_close: float
    ) -> bool:
        """
        Check if pattern is Morning Star (bullish reversal)

        Three candle pattern:
        1. Large bearish candle
        2. Small-bodied candle (star)
        3. Large bullish candle

        Returns:
            True if Morning Star detected
        """
        # First candle should be bearish
        if candle1_close >= candle1_open:
            return False

        # Third candle should be bullish
        if candle3_close <= candle3_open:
            return False

        # Second candle should be small (doji or small body)
        candle2_body = abs(candle2_close - candle2_open)
        candle2_range = candle2_high - candle2_low

        if candle2_range == 0:
            return False

        is_small_candle = candle2_body / candle2_range < 0.3

        # Star should gap down from first candle
        star_gaps_down = max(candle2_open, candle2_close) < candle1_close

        # Third candle should close well into first candle's body
        closes_into_body = candle3_close > (candle1_open + candle1_close) / 2

        return is_small_candle and star_gaps_down and closes_into_body

    @staticmethod
    def is_evening_star(
        candle1_open: float,
        candle1_close: float,
        candle2_open: float,
        candle2_close: float,
        candle2_high: float,
        candle2_low: float,
        candle3_open: float,
        candle3_close: float
    ) -> bool:
        """
        Check if pattern is Evening Star (bearish reversal)

        Three candle pattern:
        1. Large bullish candle
        2. Small-bodied candle (star)
        3. Large bearish candle

        Returns:
            True if Evening Star detected
        """
        # First candle should be bullish
        if candle1_close <= candle1_open:
            return False

        # Third candle should be bearish
        if candle3_close >= candle3_open:
            return False

        # Second candle should be small
        candle2_body = abs(candle2_close - candle2_open)
        candle2_range = candle2_high - candle2_low

        if candle2_range == 0:
            return False

        is_small_candle = candle2_body / candle2_range < 0.3

        # Star should gap up from first candle
        star_gaps_up = min(candle2_open, candle2_close) > candle1_close

        # Third candle should close well into first candle's body
        closes_into_body = candle3_close < (candle1_open + candle1_close) / 2

        return is_small_candle and star_gaps_up and closes_into_body

    @staticmethod
    def is_three_white_soldiers(
        candles: List[Dict[str, float]],
        min_body_size: float = 0.005
    ) -> bool:
        """
        Check if pattern is Three White Soldiers (strong bullish)

        Three consecutive bullish candles with higher closes

        Args:
            candles: List of 3 candle dicts with 'open', 'close', 'high', 'low'
            min_body_size: Minimum body size as fraction of close price

        Returns:
            True if Three White Soldiers detected
        """
        if len(candles) != 3:
            return False

        for candle in candles:
            # All should be bullish
            if candle['close'] <= candle['open']:
                return False

            # All should have reasonable body size
            body = candle['close'] - candle['open']
            if body / candle['close'] < min_body_size:
                return False

        # Each candle should close higher
        if not (candles[1]['close'] > candles[0]['close'] and
                candles[2]['close'] > candles[1]['close']):
            return False

        # Each candle should open within previous body
        if not (candles[0]['open'] < candles[1]['open'] < candles[0]['close'] and
                candles[1]['open'] < candles[2]['open'] < candles[1]['close']):
            return False

        return True

    @staticmethod
    def is_three_black_crows(
        candles: List[Dict[str, float]],
        min_body_size: float = 0.005
    ) -> bool:
        """
        Check if pattern is Three Black Crows (strong bearish)

        Three consecutive bearish candles with lower closes

        Args:
            candles: List of 3 candle dicts
            min_body_size: Minimum body size

        Returns:
            True if Three Black Crows detected
        """
        if len(candles) != 3:
            return False

        for candle in candles:
            # All should be bearish
            if candle['close'] >= candle['open']:
                return False

            # All should have reasonable body size
            body = candle['open'] - candle['close']
            if body / candle['open'] < min_body_size:
                return False

        # Each candle should close lower
        if not (candles[1]['close'] < candles[0]['close'] and
                candles[2]['close'] < candles[1]['close']):
            return False

        # Each candle should open within previous body
        if not (candles[0]['close'] < candles[1]['open'] < candles[0]['open'] and
                candles[1]['close'] < candles[2]['open'] < candles[1]['open']):
            return False

        return True

    @staticmethod
    def detect_trend_for_pattern(
        closes: List[float],
        index: int,
        lookback: int = 10
    ) -> str:
        """
        Detect trend direction for pattern context

        Args:
            closes: Close prices
            index: Current index
            lookback: Number of bars to look back

        Returns:
            'up', 'down', or 'sideways'
        """
        if index < lookback:
            return 'sideways'

        recent_closes = closes[index - lookback:index]

        # Simple linear regression
        x = np.arange(len(recent_closes))
        slope, _ = np.polyfit(x, recent_closes, 1)

        avg_price = np.mean(recent_closes)
        slope_percent = (slope / avg_price) * 100 if avg_price > 0 else 0

        if slope_percent > 0.3:
            return 'up'
        elif slope_percent < -0.3:
            return 'down'
        else:
            return 'sideways'

    # ==================== Comprehensive Pattern Detection ====================

    @staticmethod
    def scan_candlestick_patterns(
        ohlcv_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Scan for all candlestick patterns

        Args:
            ohlcv_data: List of OHLCV dictionaries

        Returns:
            List of detected patterns with details
        """
        if len(ohlcv_data) < 3:
            return []

        patterns_found = []

        opens = [bar['open'] for bar in ohlcv_data]
        highs = [bar['high'] for bar in ohlcv_data]
        lows = [bar['low'] for bar in ohlcv_data]
        closes = [bar['close'] for bar in ohlcv_data]

        # Scan through data
        for i in range(len(ohlcv_data)):
            current_idx = i
            current = ohlcv_data[i]

            # Single candle patterns
            if CandlestickPatterns.is_doji(current['open'], current['close'],
                                          current['high'], current['low']):
                patterns_found.append({
                    'pattern': 'doji',
                    'type': 'neutral',
                    'index': current_idx,
                    'timestamp': current.get('timestamp', current.get('date', '')),
                    'description': 'Indecision - potential reversal'
                })

            # Hammer (needs previous trend)
            if i >= 10:
                trend = CandlestickPatterns.detect_trend_for_pattern(closes, i)
                if CandlestickPatterns.is_hammer(current['open'], current['close'],
                                                 current['high'], current['low'], trend):
                    patterns_found.append({
                        'pattern': 'hammer',
                        'type': 'bullish',
                        'index': current_idx,
                        'timestamp': current.get('timestamp', current.get('date', '')),
                        'description': 'Bullish reversal signal'
                    })

                if CandlestickPatterns.is_shooting_star(current['open'], current['close'],
                                                        current['high'], current['low'], trend):
                    patterns_found.append({
                        'pattern': 'shooting_star',
                        'type': 'bearish',
                        'index': current_idx,
                        'timestamp': current.get('timestamp', current.get('date', '')),
                        'description': 'Bearish reversal signal'
                    })

            # Two candle patterns
            if i >= 1:
                prev = ohlcv_data[i - 1]

                # Bullish Engulfing
                if CandlestickPatterns.is_engulfing(prev['open'], prev['close'],
                                                    current['open'], current['close'],
                                                    'bullish'):
                    patterns_found.append({
                        'pattern': 'bullish_engulfing',
                        'type': 'bullish',
                        'index': current_idx,
                        'timestamp': current.get('timestamp', current.get('date', '')),
                        'description': 'Strong bullish reversal'
                    })

                # Bearish Engulfing
                if CandlestickPatterns.is_engulfing(prev['open'], prev['close'],
                                                    current['open'], current['close'],
                                                    'bearish'):
                    patterns_found.append({
                        'pattern': 'bearish_engulfing',
                        'type': 'bearish',
                        'index': current_idx,
                        'timestamp': current.get('timestamp', current.get('date', '')),
                        'description': 'Strong bearish reversal'
                    })

            # Three candle patterns
            if i >= 2:
                candle1 = ohlcv_data[i - 2]
                candle2 = ohlcv_data[i - 1]
                candle3 = current

                # Morning Star
                if CandlestickPatterns.is_morning_star(
                    candle1['open'], candle1['close'],
                    candle2['open'], candle2['close'], candle2['high'], candle2['low'],
                    candle3['open'], candle3['close']
                ):
                    patterns_found.append({
                        'pattern': 'morning_star',
                        'type': 'bullish',
                        'index': current_idx,
                        'timestamp': current.get('timestamp', current.get('date', '')),
                        'description': 'Major bullish reversal'
                    })

                # Evening Star
                if CandlestickPatterns.is_evening_star(
                    candle1['open'], candle1['close'],
                    candle2['open'], candle2['close'], candle2['high'], candle2['low'],
                    candle3['open'], candle3['close']
                ):
                    patterns_found.append({
                        'pattern': 'evening_star',
                        'type': 'bearish',
                        'index': current_idx,
                        'timestamp': current.get('timestamp', current.get('date', '')),
                        'description': 'Major bearish reversal'
                    })

                # Three White Soldiers
                three_candles = [candle1, candle2, candle3]
                if CandlestickPatterns.is_three_white_soldiers(three_candles):
                    patterns_found.append({
                        'pattern': 'three_white_soldiers',
                        'type': 'bullish',
                        'index': current_idx,
                        'timestamp': current.get('timestamp', current.get('date', '')),
                        'description': 'Very strong bullish continuation'
                    })

                # Three Black Crows
                if CandlestickPatterns.is_three_black_crows(three_candles):
                    patterns_found.append({
                        'pattern': 'three_black_crows',
                        'type': 'bearish',
                        'index': current_idx,
                        'timestamp': current.get('timestamp', current.get('date', '')),
                        'description': 'Very strong bearish continuation'
                    })

        return patterns_found

    @staticmethod
    def get_recent_patterns(
        ohlcv_data: List[Dict[str, Any]],
        lookback: int = 20
    ) -> Dict[str, Any]:
        """
        Get recent candlestick patterns

        Args:
            ohlcv_data: OHLCV data
            lookback: Number of recent bars to analyze

        Returns:
            Dictionary with recent patterns and summary
        """
        all_patterns = CandlestickPatterns.scan_candlestick_patterns(ohlcv_data)

        # Filter to recent patterns
        recent_patterns = [
            p for p in all_patterns
            if p['index'] >= len(ohlcv_data) - lookback
        ]

        # Count by type
        pattern_counts = {}
        for pattern in recent_patterns:
            name = pattern['pattern']
            pattern_counts[name] = pattern_counts.get(name, 0) + 1

        return {
            'patterns': recent_patterns,
            'summary': {
                'total': len(recent_patterns),
                'bullish': len([p for p in recent_patterns if p['type'] == 'bullish']),
                'bearish': len([p for p in recent_patterns if p['type'] == 'bearish']),
                'neutral': len([p for p in recent_patterns if p['type'] == 'neutral']),
                'by_type': pattern_counts
            }
        }
