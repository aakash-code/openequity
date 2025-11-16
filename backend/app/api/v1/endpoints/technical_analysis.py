"""
Technical Analysis API Endpoints
Provides technical indicators, pattern recognition, and chart analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User
from app.services.technical_indicators import TechnicalIndicators
from app.services.pattern_recognition import PatternRecognition
from app.services.candlestick_patterns import CandlestickPatterns
from app.services.support_resistance import SupportResistance
from app.services.openalgo_connector import OpenAlgoConnector

router = APIRouter()


# Pydantic models
class IndicatorRequest(BaseModel):
    indicators: List[str]


class OHLCVBar(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: Optional[str] = None
    date: Optional[str] = None


class HistoricalDataRequest(BaseModel):
    symbol: str
    exchange: str = 'NSE'
    interval: str = '1d'
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# ==================== Technical Indicators ====================

@router.post("/indicators")
async def calculate_indicators(
    data: List[OHLCVBar],
    indicators: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate technical indicators

    Available indicators:
    - sma_20, sma_50: Simple Moving Averages
    - ema_12, ema_26: Exponential Moving Averages
    - rsi: Relative Strength Index
    - macd: MACD indicator
    - bollinger_bands: Bollinger Bands
    - stochastic: Stochastic Oscillator
    - williams_r: Williams %R
    - roc: Rate of Change
    - atr: Average True Range
    - adx: Average Directional Index
    - obv: On-Balance Volume
    - vwap: Volume Weighted Average Price
    """
    try:
        ohlcv_data = [bar.dict() for bar in data]

        result = TechnicalIndicators.calculate_all_indicators(
            ohlcv_data,
            indicators
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate indicators: {str(e)}"
        )


@router.get("/indicators/{ticker}")
async def get_indicators_for_ticker(
    ticker: str,
    exchange: str = Query('NSE', description="Exchange code"),
    interval: str = Query('1d', description="Timeframe (1d, 1h, etc.)"),
    indicators: Optional[str] = Query(None, description="Comma-separated indicator names"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
):
    """
    Get technical indicators for a ticker using real-time data
    """
    try:
        # Fetch historical data from OpenAlgo
        connector = OpenAlgoConnector()
        history_data = await connector.get_history(
            ticker,
            exchange,
            interval,
            start_date,
            end_date
        )

        # Convert to OHLCV format
        if 'data' in history_data and isinstance(history_data['data'], list):
            ohlcv_data = history_data['data']
        else:
            raise ValueError("Invalid historical data format")

        # Parse indicator list
        indicator_list = indicators.split(',') if indicators else None

        # Calculate indicators
        result = TechnicalIndicators.calculate_all_indicators(
            ohlcv_data,
            indicator_list
        )

        result['ticker'] = ticker
        result['exchange'] = exchange
        result['interval'] = interval

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch indicators for {ticker}: {str(e)}"
        )


# ==================== Chart Patterns ====================

@router.post("/patterns/chart")
async def detect_chart_patterns(
    data: List[OHLCVBar],
    current_user: User = Depends(get_current_user),
):
    """
    Detect chart patterns (Head & Shoulders, Double Top/Bottom, Triangles, etc.)
    """
    try:
        ohlcv_data = [bar.dict() for bar in data]

        patterns = PatternRecognition.scan_all_patterns(ohlcv_data)

        return patterns

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect chart patterns: {str(e)}"
        )


@router.get("/patterns/chart/{ticker}")
async def get_chart_patterns_for_ticker(
    ticker: str,
    exchange: str = Query('NSE', description="Exchange code"),
    interval: str = Query('1d', description="Timeframe"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
):
    """
    Get chart patterns for a ticker using real-time data
    """
    try:
        connector = OpenAlgoConnector()
        history_data = await connector.get_history(
            ticker,
            exchange,
            interval,
            start_date,
            end_date
        )

        if 'data' in history_data and isinstance(history_data['data'], list):
            ohlcv_data = history_data['data']
        else:
            raise ValueError("Invalid historical data format")

        patterns = PatternRecognition.scan_all_patterns(ohlcv_data)

        patterns['ticker'] = ticker
        patterns['exchange'] = exchange
        patterns['interval'] = interval

        return patterns

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect patterns for {ticker}: {str(e)}"
        )


# ==================== Candlestick Patterns ====================

@router.post("/patterns/candlestick")
async def detect_candlestick_patterns(
    data: List[OHLCVBar],
    lookback: int = Query(20, description="Number of recent bars to analyze"),
    current_user: User = Depends(get_current_user),
):
    """
    Detect candlestick patterns (Doji, Hammer, Engulfing, Morning/Evening Star, etc.)
    """
    try:
        ohlcv_data = [bar.dict() for bar in data]

        patterns = CandlestickPatterns.get_recent_patterns(ohlcv_data, lookback)

        return patterns

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect candlestick patterns: {str(e)}"
        )


@router.get("/patterns/candlestick/{ticker}")
async def get_candlestick_patterns_for_ticker(
    ticker: str,
    exchange: str = Query('NSE', description="Exchange code"),
    interval: str = Query('1d', description="Timeframe"),
    lookback: int = Query(20, description="Number of bars to analyze"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
):
    """
    Get candlestick patterns for a ticker using real-time data
    """
    try:
        connector = OpenAlgoConnector()
        history_data = await connector.get_history(
            ticker,
            exchange,
            interval,
            start_date,
            end_date
        )

        if 'data' in history_data and isinstance(history_data['data'], list):
            ohlcv_data = history_data['data']
        else:
            raise ValueError("Invalid historical data format")

        patterns = CandlestickPatterns.get_recent_patterns(ohlcv_data, lookback)

        patterns['ticker'] = ticker
        patterns['exchange'] = exchange
        patterns['interval'] = interval

        return patterns

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect candlestick patterns for {ticker}: {str(e)}"
        )


# ==================== Support & Resistance ====================

@router.post("/support-resistance")
async def find_support_resistance(
    data: List[OHLCVBar],
    include_round_numbers: bool = Query(True, description="Include psychological levels"),
    include_fibonacci: bool = Query(True, description="Include Fibonacci levels"),
    include_pivots: bool = Query(True, description="Include pivot points"),
    current_user: User = Depends(get_current_user),
):
    """
    Find support and resistance levels
    """
    try:
        ohlcv_data = [bar.dict() for bar in data]

        levels = SupportResistance.analyze_all_levels(
            ohlcv_data,
            include_round_numbers,
            include_fibonacci,
            include_pivots
        )

        return levels

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find support/resistance: {str(e)}"
        )


@router.get("/support-resistance/{ticker}")
async def get_support_resistance_for_ticker(
    ticker: str,
    exchange: str = Query('NSE', description="Exchange code"),
    interval: str = Query('1d', description="Timeframe"),
    include_round_numbers: bool = Query(True),
    include_fibonacci: bool = Query(True),
    include_pivots: bool = Query(True),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
):
    """
    Get support/resistance levels for a ticker using real-time data
    """
    try:
        connector = OpenAlgoConnector()
        history_data = await connector.get_history(
            ticker,
            exchange,
            interval,
            start_date,
            end_date
        )

        if 'data' in history_data and isinstance(history_data['data'], list):
            ohlcv_data = history_data['data']
        else:
            raise ValueError("Invalid historical data format")

        levels = SupportResistance.analyze_all_levels(
            ohlcv_data,
            include_round_numbers,
            include_fibonacci,
            include_pivots
        )

        levels['ticker'] = ticker
        levels['exchange'] = exchange
        levels['interval'] = interval

        return levels

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find support/resistance for {ticker}: {str(e)}"
        )


# ==================== Comprehensive Analysis ====================

@router.get("/analyze/{ticker}")
async def comprehensive_technical_analysis(
    ticker: str,
    exchange: str = Query('NSE', description="Exchange code"),
    interval: str = Query('1d', description="Timeframe"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
):
    """
    Comprehensive technical analysis - all indicators, patterns, and levels
    """
    try:
        # Fetch historical data
        connector = OpenAlgoConnector()
        history_data = await connector.get_history(
            ticker,
            exchange,
            interval,
            start_date,
            end_date
        )

        if 'data' in history_data and isinstance(history_data['data'], list):
            ohlcv_data = history_data['data']
        else:
            raise ValueError("Invalid historical data format")

        # Calculate all indicators
        indicators = TechnicalIndicators.calculate_all_indicators(ohlcv_data)

        # Detect all patterns
        chart_patterns = PatternRecognition.scan_all_patterns(ohlcv_data)
        candlestick_patterns = CandlestickPatterns.get_recent_patterns(ohlcv_data)

        # Find support/resistance
        sr_levels = SupportResistance.analyze_all_levels(ohlcv_data)

        return {
            'ticker': ticker,
            'exchange': exchange,
            'interval': interval,
            'indicators': indicators,
            'chart_patterns': chart_patterns,
            'candlestick_patterns': candlestick_patterns,
            'support_resistance': sr_levels,
            'ohlcv_data': ohlcv_data[-100:],  # Last 100 bars
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform comprehensive analysis for {ticker}: {str(e)}"
        )


# ==================== Specific Indicator Calculations ====================

@router.get("/indicator/sma/{ticker}")
async def calculate_sma(
    ticker: str,
    period: int = Query(20, description="SMA period"),
    exchange: str = Query('NSE'),
    interval: str = Query('1d'),
    current_user: User = Depends(get_current_user),
):
    """Calculate Simple Moving Average"""
    try:
        connector = OpenAlgoConnector()
        history_data = await connector.get_history(ticker, exchange, interval)

        if 'data' in history_data:
            closes = [bar['close'] for bar in history_data['data']]
            sma_values = TechnicalIndicators.sma(closes, period)

            return {
                'ticker': ticker,
                'indicator': 'SMA',
                'period': period,
                'values': sma_values,
                'current_value': sma_values[-1] if sma_values else None
            }
        else:
            raise ValueError("No data available")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicator/rsi/{ticker}")
async def calculate_rsi(
    ticker: str,
    period: int = Query(14, description="RSI period"),
    exchange: str = Query('NSE'),
    interval: str = Query('1d'),
    current_user: User = Depends(get_current_user),
):
    """Calculate Relative Strength Index"""
    try:
        connector = OpenAlgoConnector()
        history_data = await connector.get_history(ticker, exchange, interval)

        if 'data' in history_data:
            closes = [bar['close'] for bar in history_data['data']]
            rsi_values = TechnicalIndicators.rsi(closes, period)

            current_rsi = rsi_values[-1] if rsi_values and rsi_values[-1] is not None else None

            # Interpretation
            interpretation = 'neutral'
            if current_rsi:
                if current_rsi > 70:
                    interpretation = 'overbought'
                elif current_rsi < 30:
                    interpretation = 'oversold'

            return {
                'ticker': ticker,
                'indicator': 'RSI',
                'period': period,
                'values': rsi_values,
                'current_value': current_rsi,
                'interpretation': interpretation
            }
        else:
            raise ValueError("No data available")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicator/macd/{ticker}")
async def calculate_macd(
    ticker: str,
    fast_period: int = Query(12),
    slow_period: int = Query(26),
    signal_period: int = Query(9),
    exchange: str = Query('NSE'),
    interval: str = Query('1d'),
    current_user: User = Depends(get_current_user),
):
    """Calculate MACD"""
    try:
        connector = OpenAlgoConnector()
        history_data = await connector.get_history(ticker, exchange, interval)

        if 'data' in history_data:
            closes = [bar['close'] for bar in history_data['data']]
            macd_line, signal_line, histogram = TechnicalIndicators.macd(
                closes, fast_period, slow_period, signal_period
            )

            return {
                'ticker': ticker,
                'indicator': 'MACD',
                'macd_line': macd_line,
                'signal_line': signal_line,
                'histogram': histogram,
                'current_macd': macd_line[-1] if macd_line and macd_line[-1] is not None else None,
                'current_signal': signal_line[-1] if signal_line and signal_line[-1] is not None else None,
                'current_histogram': histogram[-1] if histogram and histogram[-1] is not None else None
            }
        else:
            raise ValueError("No data available")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
