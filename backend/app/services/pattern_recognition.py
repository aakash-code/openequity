"""
Chart Pattern Recognition Service
Identifies common chart patterns and trading signals
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from scipy.signal import find_peaks, argrelextrema
from datetime import datetime


class PatternRecognition:
    """Service for detecting chart patterns"""

    # ==================== Peak and Trough Detection ====================

    @staticmethod
    def find_swing_points(
        prices: List[float],
        order: int = 5
    ) -> Tuple[List[int], List[int]]:
        """
        Find swing highs and lows

        Args:
            prices: Price data
            order: Number of points on each side to use for comparison

        Returns:
            Tuple of (peak indices, trough indices)
        """
        prices_array = np.array(prices)

        # Find peaks (swing highs)
        peaks, _ = find_peaks(prices_array, distance=order)

        # Find troughs (swing lows) - peaks of inverted prices
        troughs, _ = find_peaks(-prices_array, distance=order)

        return peaks.tolist(), troughs.tolist()

    # ==================== Trend Detection ====================

    @staticmethod
    def detect_trend(
        prices: List[float],
        period: int = 20
    ) -> Dict[str, Any]:
        """
        Detect current trend direction

        Args:
            prices: Price data
            period: Lookback period

        Returns:
            Dictionary with trend information
        """
        if len(prices) < period:
            return {'trend': 'insufficient_data', 'strength': 0}

        recent_prices = prices[-period:]

        # Linear regression to find trend
        x = np.arange(len(recent_prices))
        y = np.array(recent_prices)

        # Calculate slope
        slope, intercept = np.polyfit(x, y, 1)

        # Calculate R-squared to measure trend strength
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Determine trend
        avg_price = np.mean(recent_prices)
        slope_percent = (slope / avg_price) * 100 if avg_price > 0 else 0

        if abs(slope_percent) < 0.1:
            trend = 'sideways'
        elif slope_percent > 0:
            trend = 'uptrend'
        else:
            trend = 'downtrend'

        return {
            'trend': trend,
            'strength': abs(r_squared),
            'slope': slope,
            'slope_percent': slope_percent,
            'r_squared': r_squared
        }

    # ==================== Chart Patterns ====================

    @staticmethod
    def detect_head_and_shoulders(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        tolerance: float = 0.03
    ) -> List[Dict[str, Any]]:
        """
        Detect Head and Shoulders pattern

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            tolerance: Tolerance for shoulder equality (3% default)

        Returns:
            List of detected patterns with details
        """
        patterns = []

        if len(highs) < 50:
            return patterns

        # Find swing points
        peaks, troughs = PatternRecognition.find_swing_points(highs)

        if len(peaks) < 3 or len(troughs) < 2:
            return patterns

        # Look for H&S pattern: left shoulder, head, right shoulder
        for i in range(len(peaks) - 2):
            left_shoulder_idx = peaks[i]
            head_idx = peaks[i + 1]
            right_shoulder_idx = peaks[i + 2]

            left_shoulder = highs[left_shoulder_idx]
            head = highs[head_idx]
            right_shoulder = highs[right_shoulder_idx]

            # Head should be higher than shoulders
            if head > left_shoulder and head > right_shoulder:
                # Shoulders should be roughly equal
                shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder

                if shoulder_diff <= tolerance:
                    # Find neckline (troughs between shoulders)
                    relevant_troughs = [t for t in troughs if left_shoulder_idx < t < right_shoulder_idx]

                    if len(relevant_troughs) >= 1:
                        neckline = np.mean([lows[t] for t in relevant_troughs])

                        patterns.append({
                            'pattern': 'head_and_shoulders',
                            'type': 'bearish',
                            'left_shoulder_idx': left_shoulder_idx,
                            'head_idx': head_idx,
                            'right_shoulder_idx': right_shoulder_idx,
                            'neckline': neckline,
                            'target': neckline - (head - neckline),
                            'confidence': 1 - shoulder_diff
                        })

        return patterns

    @staticmethod
    def detect_double_top_bottom(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        tolerance: float = 0.02
    ) -> List[Dict[str, Any]]:
        """
        Detect Double Top and Double Bottom patterns

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            tolerance: Tolerance for peak/trough equality (2% default)

        Returns:
            List of detected patterns
        """
        patterns = []

        if len(highs) < 30:
            return patterns

        # Find swing points
        peaks, troughs = PatternRecognition.find_swing_points(highs)

        # Double Top
        for i in range(len(peaks) - 1):
            first_peak_idx = peaks[i]
            second_peak_idx = peaks[i + 1]

            first_peak = highs[first_peak_idx]
            second_peak = highs[second_peak_idx]

            # Peaks should be roughly equal
            peak_diff = abs(first_peak - second_peak) / first_peak

            if peak_diff <= tolerance:
                # Find trough between peaks
                relevant_troughs = [t for t in troughs if first_peak_idx < t < second_peak_idx]

                if relevant_troughs:
                    valley = min([lows[t] for t in relevant_troughs])
                    valley_idx = lows.index(valley)

                    patterns.append({
                        'pattern': 'double_top',
                        'type': 'bearish',
                        'first_peak_idx': first_peak_idx,
                        'second_peak_idx': second_peak_idx,
                        'valley_idx': valley_idx,
                        'resistance': (first_peak + second_peak) / 2,
                        'support': valley,
                        'target': valley - abs(first_peak - valley),
                        'confidence': 1 - peak_diff
                    })

        # Double Bottom
        for i in range(len(troughs) - 1):
            first_trough_idx = troughs[i]
            second_trough_idx = troughs[i + 1]

            first_trough = lows[first_trough_idx]
            second_trough = lows[second_trough_idx]

            # Troughs should be roughly equal
            trough_diff = abs(first_trough - second_trough) / first_trough

            if trough_diff <= tolerance:
                # Find peak between troughs
                relevant_peaks = [p for p in peaks if first_trough_idx < p < second_trough_idx]

                if relevant_peaks:
                    peak_high = max([highs[p] for p in relevant_peaks])
                    peak_idx = highs.index(peak_high)

                    patterns.append({
                        'pattern': 'double_bottom',
                        'type': 'bullish',
                        'first_trough_idx': first_trough_idx,
                        'second_trough_idx': second_trough_idx,
                        'peak_idx': peak_idx,
                        'support': (first_trough + second_trough) / 2,
                        'resistance': peak_high,
                        'target': peak_high + abs(peak_high - first_trough),
                        'confidence': 1 - trough_diff
                    })

        return patterns

    @staticmethod
    def detect_triangle(
        highs: List[float],
        lows: List[float],
        min_touches: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Detect Triangle patterns (ascending, descending, symmetrical)

        Args:
            highs: High prices
            lows: Low prices
            min_touches: Minimum number of touches for trendline

        Returns:
            List of detected triangle patterns
        """
        patterns = []

        if len(highs) < 50:
            return patterns

        # Look at recent data (last 50 bars)
        recent_highs = highs[-50:]
        recent_lows = lows[-50:]

        # Find peaks and troughs
        peaks, troughs = PatternRecognition.find_swing_points(recent_highs)

        if len(peaks) < 2 or len(troughs) < 2:
            return patterns

        # Calculate upper trendline (resistance)
        peak_prices = [recent_highs[p] for p in peaks]
        upper_slope, upper_intercept = np.polyfit(peaks, peak_prices, 1)

        # Calculate lower trendline (support)
        trough_prices = [recent_lows[t] for t in troughs]
        lower_slope, lower_intercept = np.polyfit(troughs, trough_prices, 1)

        # Determine triangle type
        if abs(upper_slope) < 0.01 and lower_slope > 0.01:
            triangle_type = 'ascending'
            bias = 'bullish'
        elif abs(lower_slope) < 0.01 and upper_slope < -0.01:
            triangle_type = 'descending'
            bias = 'bearish'
        elif upper_slope < -0.01 and lower_slope > 0.01:
            triangle_type = 'symmetrical'
            bias = 'neutral'
        else:
            return patterns

        # Calculate apex (where lines converge)
        if abs(upper_slope - lower_slope) > 0.001:
            apex_x = (lower_intercept - upper_intercept) / (upper_slope - lower_slope)
            apex_price = upper_slope * apex_x + upper_intercept

            patterns.append({
                'pattern': f'{triangle_type}_triangle',
                'type': bias,
                'upper_trendline': {'slope': upper_slope, 'intercept': upper_intercept},
                'lower_trendline': {'slope': lower_slope, 'intercept': lower_intercept},
                'apex_index': int(apex_x) if apex_x > 0 else len(recent_highs),
                'apex_price': apex_price,
                'start_index': len(highs) - 50,
                'current_index': len(highs) - 1
            })

        return patterns

    @staticmethod
    def detect_flags_and_pennants(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        volumes: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Detect Flag and Pennant continuation patterns

        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            volumes: Volume data

        Returns:
            List of detected patterns
        """
        patterns = []

        if len(closes) < 30:
            return patterns

        # Look for strong move followed by consolidation
        for i in range(20, len(closes) - 10):
            # Check for strong move (pole)
            pole_start = i - 20
            pole_end = i

            pole_move = (closes[pole_end] - closes[pole_start]) / closes[pole_start]

            # Need at least 5% move for pole
            if abs(pole_move) < 0.05:
                continue

            # Check for consolidation (flag/pennant)
            consolidation = closes[pole_end:pole_end + 10]

            if len(consolidation) < 5:
                continue

            consolidation_range = (max(consolidation) - min(consolidation)) / min(consolidation)

            # Consolidation should be tight (< 3%)
            if consolidation_range > 0.03:
                continue

            # Check volume decrease during consolidation
            pole_volume = np.mean(volumes[pole_start:pole_end])
            consolidation_volume = np.mean(volumes[pole_end:pole_end + 10])

            volume_decrease = consolidation_volume < pole_volume * 0.7

            if volume_decrease:
                pattern_type = 'bull_flag' if pole_move > 0 else 'bear_flag'

                patterns.append({
                    'pattern': pattern_type,
                    'type': 'bullish' if pole_move > 0 else 'bearish',
                    'pole_start_idx': pole_start,
                    'pole_end_idx': pole_end,
                    'consolidation_end_idx': pole_end + 10,
                    'pole_move_percent': pole_move * 100,
                    'target': closes[pole_end] + (closes[pole_end] - closes[pole_start])
                })

        return patterns

    # ==================== Comprehensive Pattern Scan ====================

    @staticmethod
    def scan_all_patterns(
        ohlcv_data: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan for all chart patterns

        Args:
            ohlcv_data: List of OHLCV dictionaries

        Returns:
            Dictionary with all detected patterns by type
        """
        if len(ohlcv_data) < 30:
            return {'patterns': [], 'summary': {'total': 0}}

        opens = [bar['open'] for bar in ohlcv_data]
        highs = [bar['high'] for bar in ohlcv_data]
        lows = [bar['low'] for bar in ohlcv_data]
        closes = [bar['close'] for bar in ohlcv_data]
        volumes = [bar['volume'] for bar in ohlcv_data]

        all_patterns = []

        # Detect all pattern types
        all_patterns.extend(PatternRecognition.detect_head_and_shoulders(highs, lows, closes))
        all_patterns.extend(PatternRecognition.detect_double_top_bottom(highs, lows, closes))
        all_patterns.extend(PatternRecognition.detect_triangle(highs, lows))
        all_patterns.extend(PatternRecognition.detect_flags_and_pennants(highs, lows, closes, volumes))

        # Get current trend
        trend_info = PatternRecognition.detect_trend(closes)

        # Count patterns by type
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_name = pattern['pattern']
            pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1

        return {
            'patterns': all_patterns,
            'trend': trend_info,
            'summary': {
                'total': len(all_patterns),
                'by_type': pattern_counts,
                'bullish': len([p for p in all_patterns if p.get('type') == 'bullish']),
                'bearish': len([p for p in all_patterns if p.get('type') == 'bearish']),
                'neutral': len([p for p in all_patterns if p.get('type') == 'neutral'])
            }
        }
