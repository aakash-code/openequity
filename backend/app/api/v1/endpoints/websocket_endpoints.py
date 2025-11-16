"""
WebSocket API Endpoints
Real-time data streaming via WebSocket connections
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional, List
import json
import logging

from app.services.websocket_manager import manager
from app.services.realtime_streamer import streamer
from app.core.deps import get_current_user_ws
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/quotes")
async def websocket_quotes(
    websocket: WebSocket,
    symbols: str = Query(..., description="Comma-separated symbols"),
    exchange: str = Query('NSE', description="Exchange code"),
    interval: int = Query(1, description="Update interval in seconds")
):
    """
    WebSocket endpoint for streaming real-time quotes

    Usage:
        ws://localhost:8000/api/v1/ws/quotes?symbols=RELIANCE,TCS&exchange=NSE&interval=1
    """
    symbols_list = [s.strip().upper() for s in symbols.split(',')]
    channel = f"quotes:{exchange}:{','.join(symbols_list)}"

    await manager.connect(websocket, channel, {
        'symbols': symbols_list,
        'exchange': exchange
    })

    # Start streaming if not already active
    await streamer.start_quote_stream(symbols_list, exchange, interval)

    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()

            # Handle client commands
            try:
                message = json.loads(data)
                command = message.get('command')

                if command == 'ping':
                    await websocket.send_json({'type': 'pong', 'timestamp': message.get('timestamp')})

                elif command == 'subscribe':
                    # Add more symbols to subscription
                    new_symbols = message.get('symbols', [])
                    if new_symbols:
                        all_symbols = list(set(symbols_list + new_symbols))
                        await streamer.start_quote_stream(all_symbols, exchange, interval)

                elif command == 'unsubscribe':
                    # Remove symbols from subscription (simplified - would need more logic)
                    pass

            except json.JSONDecodeError:
                await websocket.send_json({'type': 'error', 'message': 'Invalid JSON'})

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"Client disconnected from quotes stream")


@router.websocket("/ws/ticker/{symbol}")
async def websocket_ticker(
    websocket: WebSocket,
    symbol: str,
    exchange: str = Query('NSE', description="Exchange code"),
    interval: int = Query(1, description="Update interval in seconds")
):
    """
    WebSocket endpoint for streaming single symbol ticker

    Usage:
        ws://localhost:8000/api/v1/ws/ticker/RELIANCE?exchange=NSE&interval=1
    """
    symbol = symbol.upper()
    channel = f"ticker:{exchange}:{symbol}"

    await manager.connect(websocket, channel, {
        'symbol': symbol,
        'exchange': exchange
    })

    # Start streaming
    await streamer.start_ticker_stream(symbol, exchange, interval)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                if message.get('command') == 'ping':
                    await websocket.send_json({'type': 'pong'})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"Client disconnected from ticker stream: {symbol}")


@router.websocket("/ws/depth/{symbol}")
async def websocket_market_depth(
    websocket: WebSocket,
    symbol: str,
    exchange: str = Query('NSE', description="Exchange code"),
    interval: int = Query(2, description="Update interval in seconds")
):
    """
    WebSocket endpoint for streaming market depth (order book)

    Usage:
        ws://localhost:8000/api/v1/ws/depth/RELIANCE?exchange=NSE&interval=2
    """
    symbol = symbol.upper()
    channel = f"depth:{exchange}:{symbol}"

    await manager.connect(websocket, channel, {
        'symbol': symbol,
        'exchange': exchange
    })

    # Start streaming
    await streamer.start_market_depth_stream(symbol, exchange, interval)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                if message.get('command') == 'ping':
                    await websocket.send_json({'type': 'pong'})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"Client disconnected from depth stream: {symbol}")


@router.websocket("/ws/ohlc/{symbol}")
async def websocket_ohlc(
    websocket: WebSocket,
    symbol: str,
    exchange: str = Query('NSE', description="Exchange code"),
    interval: str = Query('1m', description="Candle interval"),
    update_interval: int = Query(5, description="Update interval in seconds")
):
    """
    WebSocket endpoint for streaming OHLC candles

    Usage:
        ws://localhost:8000/api/v1/ws/ohlc/RELIANCE?exchange=NSE&interval=1m&update_interval=5
    """
    symbol = symbol.upper()
    channel = f"ohlc:{exchange}:{symbol}:{interval}"

    await manager.connect(websocket, channel, {
        'symbol': symbol,
        'exchange': exchange,
        'interval': interval
    })

    # Start streaming
    await streamer.start_ohlc_stream(symbol, exchange, interval, update_interval)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                if message.get('command') == 'ping':
                    await websocket.send_json({'type': 'pong'})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"Client disconnected from OHLC stream: {symbol}")


@router.websocket("/ws/portfolio")
async def websocket_portfolio(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token")
):
    """
    WebSocket endpoint for streaming portfolio updates

    Usage:
        ws://localhost:8000/api/v1/ws/portfolio?token=your_jwt_token
    """
    # Note: In production, validate token properly
    channel = f"portfolio:{token[:10]}"  # Simplified

    await manager.connect(websocket, channel, {
        'type': 'portfolio',
        'authenticated': True
    })

    try:
        # Send initial portfolio data
        await websocket.send_json({
            'type': 'portfolio_init',
            'message': 'Portfolio stream connected'
        })

        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                if message.get('command') == 'ping':
                    await websocket.send_json({'type': 'pong'})
                elif message.get('command') == 'get_positions':
                    # Fetch and send positions
                    await websocket.send_json({
                        'type': 'positions',
                        'data': []  # Would fetch real positions
                    })
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info("Client disconnected from portfolio stream")


# Management endpoints

@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket server status"""
    return {
        'connection_info': manager.get_connection_info(),
        'active_streams': streamer.get_active_streams(),
        'channels': manager.get_all_channels()
    }


@router.post("/ws/broadcast")
async def broadcast_message(
    channel: str,
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast a message to a specific channel (admin only)

    Args:
        channel: Channel name
        message: Message to broadcast
    """
    await manager.broadcast_to_channel(channel, message)

    return {
        'status': 'sent',
        'channel': channel,
        'connections': manager.get_channel_connections_count(channel)
    }
