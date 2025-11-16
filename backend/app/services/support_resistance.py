"""
Support and Resistance Level Identification Service
Identifies key price levels for trading decisions
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from scipy.signal import find_peaks
from collections import Counter


class SupportResistance:
    """Service for identifying support and resistance levels"""

    @staticmethod
    def find_pivot_points(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        method: str = 'standard'
    ) -> Dict[str, float]:
        """
        Calculate pivot points

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            method: 'standard', 'fibonacci', 'woodie', 'camarilla'

        Returns:
            Dictionary with pivot levels
        """
        if not highs or not lows or not closes:
            return {}

        high = highs[-1]
        low = lows[-1]
        close = closes[-1]

        if method == 'standard':
            pivot = (high + low + close) / 3

            r1 = 2 * pivot - low
            r2 = pivot + (high - low)
            r3 = high + 2 * (pivot - low)

            s1 = 2 * pivot - high
            s2 = pivot - (high - low)
            s3 = low - 2 * (high - pivot)

        elif method == 'fibonacci':
            pivot = (high + low + close) / 3

            r1 = pivot + 0.382 * (high - low)
            r2 = pivot + 0.618 * (high - low)
            r3 = pivot + 1.000 * (high - low)

            s1 = pivot - 0.382 * (high - low)
            s2 = pivot - 0.618 * (high - low)
            s3 = pivot - 1.000 * (high - low)

        elif method == 'woodie':
            pivot = (high + low + 2 * close) / 4

            r1 = 2 * pivot - low
            r2 = pivot + (high - low)
            r3 = high + 2 * (pivot - low)

            s1 = 2 * pivot - high
            s2 = pivot - (high - low)
            s3 = low - 2 * (high - pivot)

        elif method == 'camarilla':
            pivot = (high + low + close) / 3

            r1 = close + 1.1 * (high - low) / 12
            r2 = close + 1.1 * (high - low) / 6
            r3 = close + 1.1 * (high - low) / 4
            r4 = close + 1.1 * (high - low) / 2

            s1 = close - 1.1 * (high - low) / 12
            s2 = close - 1.1 * (high - low) / 6
            s3 = close - 1.1 * (high - low) / 4
            s4 = close - 1.1 * (high - low) / 2

            return {
                'pivot': pivot,
                'r1': r1, 'r2': r2, 'r3': r3, 'r4': r4,
                's1': s1, 's2': s2, 's3': s3, 's4': s4
            }

        else:
            raise ValueError(f"Unknown pivot method: {method}")

        return {
            'pivot': pivot,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3
        }

    @staticmethod
    def find_support_resistance_levels(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        num_levels: int = 5,
        tolerance: float = 0.02
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find support and resistance levels using peak/trough clustering

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            num_levels: Number of levels to return
            tolerance: Tolerance for clustering levels (2% default)

        Returns:
            Dictionary with support and resistance levels
        """
        if len(highs) < 20:
            return {'support': [], 'resistance': []}

        # Find swing highs (resistance candidates)
        peaks, _ = find_peaks(highs, distance=5)
        resistance_prices = [highs[p] for p in peaks]

        # Find swing lows (support candidates)
        troughs, _ = find_peaks([-l for l in lows], distance=5)
        support_prices = [lows[t] for t in troughs]

        # Cluster resistance levels
        resistance_levels = SupportResistance._cluster_levels(
            resistance_prices,
            tolerance,
            num_levels
        )

        # Cluster support levels
        support_levels = SupportResistance._cluster_levels(
            support_prices,
            tolerance,
            num_levels
        )

        # Calculate strength (how many times price touched the level)
        current_price = closes[-1]

        return {
            'support': [
                {
                    'price': level['price'],
                    'strength': level['count'],
                    'distance_percent': ((current_price - level['price']) / current_price) * 100
                }
                for level in support_levels
                if level['price'] < current_price
            ],
            'resistance': [
                {
                    'price': level['price'],
                    'strength': level['count'],
                    'distance_percent': ((level['price'] - current_price) / current_price) * 100
                }
                for level in resistance_levels
                if level['price'] > current_price
            ],
            'current_price': current_price
        }

    @staticmethod
    def _cluster_levels(
        prices: List[float],
        tolerance: float,
        max_levels: int
    ) -> List[Dict[str, Any]]:
        """
        Cluster price levels that are close together

        Args:
            prices: List of price levels
            tolerance: Clustering tolerance
            max_levels: Maximum number of levels to return

        Returns:
            List of clustered levels with counts
        """
        if not prices:
            return []

        # Sort prices
        sorted_prices = sorted(prices)

        clusters = []
        current_cluster = [sorted_prices[0]]

        for price in sorted_prices[1:]:
            # Check if price is within tolerance of current cluster
            cluster_avg = np.mean(current_cluster)

            if abs(price - cluster_avg) / cluster_avg <= tolerance:
                current_cluster.append(price)
            else:
                # Save current cluster and start new one
                clusters.append({
                    'price': np.mean(current_cluster),
                    'count': len(current_cluster)
                })
                current_cluster = [price]

        # Add last cluster
        if current_cluster:
            clusters.append({
                'price': np.mean(current_cluster),
                'count': len(current_cluster)
            })

        # Sort by strength (count) and return top levels
        clusters.sort(key=lambda x: x['count'], reverse=True)

        return clusters[:max_levels]

    @staticmethod
    def find_round_number_levels(
        current_price: float,
        num_levels: int = 5,
        intervals: List[int] = None
    ) -> Dict[str, List[float]]:
        """
        Find psychological round number levels

        Args:
            current_price: Current price
            num_levels: Number of levels above and below
            intervals: Round number intervals (e.g., [50, 100, 500])

        Returns:
            Dictionary with support and resistance round numbers
        """
        if intervals is None:
            # Auto-determine intervals based on price
            if current_price < 10:
                intervals = [1, 5]
            elif current_price < 100:
                intervals = [5, 10, 25]
            elif current_price < 1000:
                intervals = [10, 50, 100]
            elif current_price < 5000:
                intervals = [50, 100, 250, 500]
            else:
                intervals = [100, 500, 1000]

        all_levels = set()

        for interval in intervals:
            # Find round numbers below
            for i in range(1, num_levels + 1):
                level = (int(current_price / interval) - i) * interval
                if level > 0:
                    all_levels.add(float(level))

            # Find round numbers above
            for i in range(1, num_levels + 1):
                level = (int(current_price / interval) + i) * interval
                all_levels.add(float(level))

        # Split into support and resistance
        support = sorted([l for l in all_levels if l < current_price], reverse=True)
        resistance = sorted([l for l in all_levels if l > current_price])

        return {
            'support': support[:num_levels],
            'resistance': resistance[:num_levels],
            'current_price': current_price
        }

    @staticmethod
    def find_fibonacci_retracement(
        swing_high: float,
        swing_low: float,
        direction: str = 'uptrend'
    ) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels

        Args:
            swing_high: Swing high price
            swing_low: Swing low price
            direction: 'uptrend' or 'downtrend'

        Returns:
            Dictionary with Fibonacci levels
        """
        diff = swing_high - swing_low

        if direction == 'uptrend':
            # Retracement from high
            return {
                '0%': swing_high,
                '23.6%': swing_high - 0.236 * diff,
                '38.2%': swing_high - 0.382 * diff,
                '50%': swing_high - 0.5 * diff,
                '61.8%': swing_high - 0.618 * diff,
                '78.6%': swing_high - 0.786 * diff,
                '100%': swing_low,
                'direction': 'uptrend'
            }
        else:
            # Extension from low
            return {
                '0%': swing_low,
                '23.6%': swing_low + 0.236 * diff,
                '38.2%': swing_low + 0.382 * diff,
                '50%': swing_low + 0.5 * diff,
                '61.8%': swing_low + 0.618 * diff,
                '78.6%': swing_low + 0.786 * diff,
                '100%': swing_high,
                'direction': 'downtrend'
            }

    @staticmethod
    def auto_detect_fibonacci_levels(
        highs: List[float],
        lows: List[float],
        lookback: int = 50
    ) -> Dict[str, Any]:
        """
        Auto-detect swing high/low and calculate Fibonacci levels

        Args:
            highs: High prices
            lows: Low prices
            lookback: Period to look for swing points

        Returns:
            Fibonacci levels with auto-detected swings
        """
        if len(highs) < lookback:
            lookback = len(highs)

        recent_highs = highs[-lookback:]
        recent_lows = lows[-lookback:]

        swing_high = max(recent_highs)
        swing_low = min(recent_lows)

        swing_high_idx = len(highs) - lookback + recent_highs.index(swing_high)
        swing_low_idx = len(lows) - lookback + recent_lows.index(swing_low)

        # Determine trend direction
        if swing_high_idx > swing_low_idx:
            direction = 'uptrend'
        else:
            direction = 'downtrend'

        fib_levels = SupportResistance.find_fibonacci_retracement(
            swing_high,
            swing_low,
            direction
        )

        fib_levels['swing_high_idx'] = swing_high_idx
        fib_levels['swing_low_idx'] = swing_low_idx

        return fib_levels

    # ==================== Comprehensive Level Analysis ====================

    @staticmethod
    def analyze_all_levels(
        ohlcv_data: List[Dict[str, Any]],
        include_round_numbers: bool = True,
        include_fibonacci: bool = True,
        include_pivots: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive support/resistance analysis

        Args:
            ohlcv_data: OHLCV data
            include_round_numbers: Include psychological levels
            include_fibonacci: Include Fibonacci levels
            include_pivots: Include pivot points

        Returns:
            Complete level analysis
        """
        if len(ohlcv_data) < 20:
            return {}

        highs = [bar['high'] for bar in ohlcv_data]
        lows = [bar['low'] for bar in ohlcv_data]
        closes = [bar['close'] for bar in ohlcv_data]
        current_price = closes[-1]

        result = {
            'current_price': current_price,
            'timestamp': ohlcv_data[-1].get('timestamp', ohlcv_data[-1].get('date', ''))
        }

        # Technical support/resistance
        sr_levels = SupportResistance.find_support_resistance_levels(
            highs, lows, closes
        )
        result['technical_levels'] = sr_levels

        # Round numbers
        if include_round_numbers:
            round_levels = SupportResistance.find_round_number_levels(current_price)
            result['round_number_levels'] = round_levels

        # Fibonacci
        if include_fibonacci:
            fib_levels = SupportResistance.auto_detect_fibonacci_levels(highs, lows)
            result['fibonacci_levels'] = fib_levels

        # Pivot points
        if include_pivots:
            pivot_standard = SupportResistance.find_pivot_points(
                highs, lows, closes, 'standard'
            )
            pivot_fibonacci = SupportResistance.find_pivot_points(
                highs, lows, closes, 'fibonacci'
            )
            result['pivot_points'] = {
                'standard': pivot_standard,
                'fibonacci': pivot_fibonacci
            }

        # Combine all levels for easy access
        all_support = []
        all_resistance = []

        # Technical levels
        all_support.extend([
            {'price': l['price'], 'type': 'technical', 'strength': l['strength']}
            for l in sr_levels.get('support', [])
        ])
        all_resistance.extend([
            {'price': l['price'], 'type': 'technical', 'strength': l['strength']}
            for l in sr_levels.get('resistance', [])
        ])

        # Add round numbers
        if include_round_numbers:
            all_support.extend([
                {'price': p, 'type': 'round_number', 'strength': 1}
                for p in round_levels.get('support', [])[:3]
            ])
            all_resistance.extend([
                {'price': p, 'type': 'round_number', 'strength': 1}
                for p in round_levels.get('resistance', [])[:3]
            ])

        # Sort by proximity to current price
        all_support.sort(key=lambda x: current_price - x['price'])
        all_resistance.sort(key=lambda x: x['price'] - current_price)

        result['nearest_support'] = all_support[:3] if all_support else []
        result['nearest_resistance'] = all_resistance[:3] if all_resistance else []

        return result
