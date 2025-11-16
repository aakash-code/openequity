"""
OpenAlgo Connector Service
Integrates with OpenAlgo API for real-time Indian market data
"""

import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os


class OpenAlgoConnector:
    """Service to connect to OpenAlgo for real-time broker data"""

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None
    ):
        """
        Initialize OpenAlgo connector

        Args:
            base_url: OpenAlgo server URL (e.g., http://localhost:5000)
            api_key: OpenAlgo API key from settings
        """
        self.base_url = base_url or os.getenv('OPENALGO_URL', 'http://localhost:5000')
        self.api_key = api_key or os.getenv('OPENALGO_API_KEY')
        self.api_version = 'v1'

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    async def ping(self) -> Dict[str, Any]:
        """
        Test API connectivity

        Returns:
            Connection status
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/{self.api_version}/ping",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_quotes(
        self,
        symbols: List[str],
        exchange: str = 'NSE'
    ) -> Dict[str, Any]:
        """
        Get real-time quotes for symbols

        Args:
            symbols: List of symbols (e.g., ['RELIANCE', 'TCS', 'INFY'])
            exchange: Exchange code (NSE, BSE, NFO, etc.)

        Returns:
            Real-time quote data
        """
        async with httpx.AsyncClient() as client:
            # OpenAlgo expects symbol in format "EXCHANGE:SYMBOL"
            formatted_symbols = [f"{exchange}:{symbol}" for symbol in symbols]

            response = await client.post(
                f"{self.base_url}/api/{self.api_version}/quotes",
                headers=self._get_headers(),
                json={'symbols': formatted_symbols}
            )
            response.raise_for_status()
            return response.json()

    async def get_history(
        self,
        symbol: str,
        exchange: str = 'NSE',
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical OHLC data

        Args:
            symbol: Symbol name
            exchange: Exchange code
            interval: Time interval (1m, 5m, 15m, 1h, 1d, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Historical OHLC data
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if not start_date:
            # Default to 1 year of data
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/{self.api_version}/history",
                headers=self._get_headers(),
                json={
                    'symbol': f"{exchange}:{symbol}",
                    'interval': interval,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_depth(
        self,
        symbol: str,
        exchange: str = 'NSE'
    ) -> Dict[str, Any]:
        """
        Get market depth (order book)

        Args:
            symbol: Symbol name
            exchange: Exchange code

        Returns:
            Market depth with bid/ask levels
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/{self.api_version}/depth",
                headers=self._get_headers(),
                json={'symbol': f"{exchange}:{symbol}"}
            )
            response.raise_for_status()
            return response.json()

    async def search_symbols(
        self,
        query: str,
        exchange: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for symbols

        Args:
            query: Search query
            exchange: Optional exchange filter

        Returns:
            List of matching symbols
        """
        async with httpx.AsyncClient() as client:
            payload = {'query': query}
            if exchange:
                payload['exchange'] = exchange

            response = await client.post(
                f"{self.base_url}/api/{self.api_version}/search",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def get_positions(self) -> Dict[str, Any]:
        """
        Get current positions from broker

        Returns:
            Position book
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/{self.api_version}/positionbook",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_holdings(self) -> Dict[str, Any]:
        """
        Get demat holdings

        Returns:
            Holdings data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/{self.api_version}/holdings",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_funds(self) -> Dict[str, Any]:
        """
        Get account funds and margins

        Returns:
            Funds and margin data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/{self.api_version}/funds",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_orderbook(self) -> Dict[str, Any]:
        """
        Get order book

        Returns:
            List of orders
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/{self.api_version}/orderbook",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def place_order(
        self,
        symbol: str,
        exchange: str,
        action: str,  # BUY or SELL
        quantity: int,
        price: Optional[float] = None,
        order_type: str = 'MARKET',  # MARKET or LIMIT
        product: str = 'MIS',  # MIS (intraday) or CNC (delivery)
        **kwargs
    ) -> Dict[str, Any]:
        """
        Place an order through broker

        Args:
            symbol: Symbol name
            exchange: Exchange code
            action: BUY or SELL
            quantity: Order quantity
            price: Limit price (required for LIMIT orders)
            order_type: MARKET or LIMIT
            product: MIS (intraday) or CNC (delivery)
            **kwargs: Additional broker-specific parameters

        Returns:
            Order placement response
        """
        async with httpx.AsyncClient() as client:
            order_data = {
                'symbol': f"{exchange}:{symbol}",
                'action': action.upper(),
                'quantity': quantity,
                'order_type': order_type.upper(),
                'product': product.upper(),
                **kwargs
            }

            if price and order_type.upper() == 'LIMIT':
                order_data['price'] = price

            response = await client.post(
                f"{self.base_url}/api/{self.api_version}/placeorder",
                headers=self._get_headers(),
                json=order_data
            )
            response.raise_for_status()
            return response.json()

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order

        Args:
            order_id: Order ID to cancel

        Returns:
            Cancellation response
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/{self.api_version}/cancelorder",
                headers=self._get_headers(),
                json={'order_id': order_id}
            )
            response.raise_for_status()
            return response.json()
