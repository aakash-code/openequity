"""
WebSocket Connection Manager
Handles WebSocket connections and message broadcasting
"""

from typing import Dict, Set, List, Any
from fastapi import WebSocket
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        # Active connections by channel
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str, metadata: Dict[str, Any] = None):
        """
        Connect a WebSocket to a channel

        Args:
            websocket: WebSocket connection
            channel: Channel name (e.g., 'quotes:RELIANCE', 'market:NSE')
            metadata: Optional metadata about the connection
        """
        await websocket.accept()

        async with self._lock:
            if channel not in self.active_connections:
                self.active_connections[channel] = set()

            self.active_connections[channel].add(websocket)
            self.connection_metadata[websocket] = {
                'channel': channel,
                'connected_at': datetime.now().isoformat(),
                **(metadata or {})
            }

        logger.info(f"Client connected to channel: {channel}. Total connections: {len(self.active_connections[channel])}")

    async def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket from all channels

        Args:
            websocket: WebSocket connection to disconnect
        """
        async with self._lock:
            # Find and remove from all channels
            for channel, connections in self.active_connections.items():
                if websocket in connections:
                    connections.remove(websocket)
                    logger.info(f"Client disconnected from channel: {channel}. Remaining: {len(connections)}")

            # Remove metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send message to a specific WebSocket

        Args:
            message: Message to send (JSON string)
            websocket: Target WebSocket
        """
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """
        Broadcast message to all connections in a channel

        Args:
            channel: Channel name
            message: Message to broadcast (will be JSON encoded)
        """
        if channel not in self.active_connections:
            return

        # Add timestamp to message
        message['timestamp'] = datetime.now().isoformat()

        message_str = json.dumps(message)
        disconnected = []

        # Send to all connections in channel
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        Broadcast message to all connections across all channels

        Args:
            message: Message to broadcast
        """
        for channel in self.active_connections.keys():
            await self.broadcast_to_channel(channel, message)

    def get_channel_connections_count(self, channel: str) -> int:
        """Get number of connections for a channel"""
        return len(self.active_connections.get(channel, set()))

    def get_all_channels(self) -> List[str]:
        """Get list of all active channels"""
        return list(self.active_connections.keys())

    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about all connections"""
        return {
            'total_connections': sum(len(conns) for conns in self.active_connections.values()),
            'channels': {
                channel: {
                    'connections': len(conns),
                    'channel_name': channel
                }
                for channel, conns in self.active_connections.items()
            }
        }


# Global connection manager instance
manager = ConnectionManager()
