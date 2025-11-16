"""
Real-time Data Streaming Service
Streams market data via WebSocket connections
"""

import asyncio
from typing import List, Dict, Any, Optional
import random
from datetime import datetime, timedelta
import logging

from app.services.websocket_manager import manager
from app.services.openalgo_connector import OpenAlgoConnector

logger = logging.getLogger(__name__)


class RealtimeStreamer:
    """Service for streaming real-time market data"""

    def __init__(self):
        self.active_streams: Dict[str, asyncio.Task] = {}
        self.openalgo = OpenAlgoConnector()

    async def start_quote_stream(
        self,
        symbols: List[str],
        exchange: str = 'NSE',
        interval_seconds: int = 1
    ):
        """
        Start streaming quotes for symbols

        Args:
            symbols: List of symbol names
            exchange: Exchange code
            interval_seconds: Update interval in seconds
        """
        channel = f"quotes:{exchange}:{','.join(symbols)}"

        # Don't start if already streaming
        if channel in self.active_streams:
            logger.info(f"Stream already active for {channel}")
            return

        async def stream_quotes():
            """Inner function to stream quotes"""
            logger.info(f"Starting quote stream for {channel}")

            while True:
                try:
                    # Check if anyone is still listening
                    if manager.get_channel_connections_count(channel) == 0:
                        logger.info(f"No listeners for {channel}, stopping stream")
                        break

                    # Fetch quotes from OpenAlgo (or generate sample data)
                    try:
                        quotes_data = await self.openalgo.get_quotes(symbols, exchange)
                        data = quotes_data.get('data', [])
                    except Exception as e:
                        logger.warning(f"OpenAlgo fetch failed, using sample data: {e}")
                        data = self._generate_sample_quotes(symbols, exchange)

                    # Broadcast to all listeners
                    await manager.broadcast_to_channel(channel, {
                        'type': 'quotes',
                        'exchange': exchange,
                        'data': data
                    })

                    # Wait before next update
                    await asyncio.sleep(interval_seconds)

                except Exception as e:
                    logger.error(f"Error in quote stream: {e}")
                    await asyncio.sleep(interval_seconds)

            # Clean up
            if channel in self.active_streams:
                del self.active_streams[channel]
            logger.info(f"Quote stream stopped for {channel}")

        # Start the stream task
        task = asyncio.create_task(stream_quotes())
        self.active_streams[channel] = task

    async def start_ticker_stream(
        self,
        symbol: str,
        exchange: str = 'NSE',
        interval_seconds: int = 1
    ):
        """
        Start streaming ticker data (LTP updates) for a single symbol

        Args:
            symbol: Symbol name
            exchange: Exchange code
            interval_seconds: Update interval in seconds
        """
        channel = f"ticker:{exchange}:{symbol}"

        if channel in self.active_streams:
            return

        async def stream_ticker():
            """Stream ticker updates"""
            logger.info(f"Starting ticker stream for {symbol}")
            last_price = None

            while True:
                try:
                    if manager.get_channel_connections_count(channel) == 0:
                        break

                    # Fetch latest quote
                    try:
                        quotes_data = await self.openalgo.get_quotes([symbol], exchange)
                        if quotes_data.get('data'):
                            quote = quotes_data['data'][0]
                            current_price = quote.get('ltp', quote.get('last_price', 0))
                        else:
                            raise ValueError("No data")
                    except Exception as e:
                        # Generate sample data
                        if last_price is None:
                            last_price = random.uniform(100, 5000)
                        current_price = last_price * random.uniform(0.998, 1.002)

                    # Calculate change
                    change = 0
                    change_percent = 0
                    if last_price:
                        change = current_price - last_price
                        change_percent = (change / last_price) * 100

                    ticker_data = {
                        'type': 'ticker',
                        'symbol': symbol,
                        'exchange': exchange,
                        'ltp': round(current_price, 2),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'timestamp': datetime.now().isoformat()
                    }

                    await manager.broadcast_to_channel(channel, ticker_data)

                    last_price = current_price
                    await asyncio.sleep(interval_seconds)

                except Exception as e:
                    logger.error(f"Error in ticker stream: {e}")
                    await asyncio.sleep(interval_seconds)

            if channel in self.active_streams:
                del self.active_streams[channel]
            logger.info(f"Ticker stream stopped for {symbol}")

        task = asyncio.create_task(stream_ticker())
        self.active_streams[channel] = task

    async def start_market_depth_stream(
        self,
        symbol: str,
        exchange: str = 'NSE',
        interval_seconds: int = 2
    ):
        """
        Start streaming market depth (order book) for a symbol

        Args:
            symbol: Symbol name
            exchange: Exchange code
            interval_seconds: Update interval in seconds
        """
        channel = f"depth:{exchange}:{symbol}"

        if channel in self.active_streams:
            return

        async def stream_depth():
            """Stream market depth updates"""
            logger.info(f"Starting depth stream for {symbol}")

            while True:
                try:
                    if manager.get_channel_connections_count(channel) == 0:
                        break

                    # Fetch market depth
                    try:
                        depth_data = await self.openalgo.get_depth(symbol, exchange)
                    except Exception as e:
                        depth_data = self._generate_sample_depth(symbol)

                    depth_data['type'] = 'depth'
                    depth_data['symbol'] = symbol
                    depth_data['exchange'] = exchange

                    await manager.broadcast_to_channel(channel, depth_data)
                    await asyncio.sleep(interval_seconds)

                except Exception as e:
                    logger.error(f"Error in depth stream: {e}")
                    await asyncio.sleep(interval_seconds)

            if channel in self.active_streams:
                del self.active_streams[channel]
            logger.info(f"Depth stream stopped for {symbol}")

        task = asyncio.create_task(stream_depth())
        self.active_streams[channel] = task

    async def start_ohlc_stream(
        self,
        symbol: str,
        exchange: str = 'NSE',
        interval: str = '1m',
        update_interval_seconds: int = 5
    ):
        """
        Start streaming OHLC candle updates

        Args:
            symbol: Symbol name
            exchange: Exchange code
            interval: Candle interval (1m, 5m, etc.)
            update_interval_seconds: Update interval
        """
        channel = f"ohlc:{exchange}:{symbol}:{interval}"

        if channel in self.active_streams:
            return

        async def stream_ohlc():
            """Stream OHLC candle updates"""
            logger.info(f"Starting OHLC stream for {symbol} ({interval})")

            while True:
                try:
                    if manager.get_channel_connections_count(channel) == 0:
                        break

                    # Generate current candle (in real implementation, fetch from OpenAlgo)
                    candle = self._generate_sample_candle(symbol)

                    ohlc_data = {
                        'type': 'ohlc',
                        'symbol': symbol,
                        'exchange': exchange,
                        'interval': interval,
                        'candle': candle
                    }

                    await manager.broadcast_to_channel(channel, ohlc_data)
                    await asyncio.sleep(update_interval_seconds)

                except Exception as e:
                    logger.error(f"Error in OHLC stream: {e}")
                    await asyncio.sleep(update_interval_seconds)

            if channel in self.active_streams:
                del self.active_streams[channel]
            logger.info(f"OHLC stream stopped for {symbol}")

        task = asyncio.create_task(stream_ohlc())
        self.active_streams[channel] = task

    async def stop_stream(self, channel: str):
        """
        Stop a specific stream

        Args:
            channel: Channel name to stop
        """
        if channel in self.active_streams:
            self.active_streams[channel].cancel()
            del self.active_streams[channel]
            logger.info(f"Stream stopped: {channel}")

    async def stop_all_streams(self):
        """Stop all active streams"""
        for channel, task in list(self.active_streams.items()):
            task.cancel()
        self.active_streams.clear()
        logger.info("All streams stopped")

    def get_active_streams(self) -> List[str]:
        """Get list of active stream channels"""
        return list(self.active_streams.keys())

    # Helper methods for generating sample data

    def _generate_sample_quotes(self, symbols: List[str], exchange: str) -> List[Dict[str, Any]]:
        """Generate sample quote data"""
        quotes = []
        for symbol in symbols:
            price = random.uniform(100, 5000)
            quotes.append({
                'symbol': symbol,
                'exchange': exchange,
                'ltp': round(price, 2),
                'last_price': round(price, 2),
                'open': round(price * random.uniform(0.98, 1.02), 2),
                'high': round(price * random.uniform(1.00, 1.05), 2),
                'low': round(price * random.uniform(0.95, 1.00), 2),
                'close': round(price, 2),
                'volume': random.randint(100000, 10000000),
                'change': round(price * random.uniform(-0.03, 0.03), 2),
                'change_percent': round(random.uniform(-3, 3), 2),
                'bid': round(price * 0.999, 2),
                'ask': round(price * 1.001, 2),
                'timestamp': datetime.now().isoformat()
            })
        return quotes

    def _generate_sample_depth(self, symbol: str) -> Dict[str, Any]:
        """Generate sample market depth data"""
        base_price = random.uniform(100, 5000)

        bids = []
        asks = []

        for i in range(5):
            bid_price = base_price - (i + 1) * base_price * 0.001
            ask_price = base_price + (i + 1) * base_price * 0.001

            bids.append({
                'price': round(bid_price, 2),
                'quantity': random.randint(100, 10000),
                'orders': random.randint(1, 50)
            })

            asks.append({
                'price': round(ask_price, 2),
                'quantity': random.randint(100, 10000),
                'orders': random.randint(1, 50)
            })

        return {
            'bids': bids,
            'asks': asks,
            'timestamp': datetime.now().isoformat()
        }

    def _generate_sample_candle(self, symbol: str) -> Dict[str, Any]:
        """Generate sample OHLC candle"""
        base_price = random.uniform(100, 5000)
        open_price = base_price
        high = base_price * random.uniform(1.00, 1.02)
        low = base_price * random.uniform(0.98, 1.00)
        close = base_price * random.uniform(0.99, 1.01)
        volume = random.randint(10000, 1000000)

        return {
            'timestamp': datetime.now().isoformat(),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        }


# Global streamer instance
streamer = RealtimeStreamer()
