import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1';

export interface QuoteData {
  symbol: string;
  exchange: string;
  ltp: number;
  last_price: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change: number;
  change_percent: number;
  bid: number;
  ask: number;
  timestamp: string;
}

export interface TickerData {
  type: 'ticker';
  symbol: string;
  exchange: string;
  ltp: number;
  change: number;
  change_percent: number;
  timestamp: string;
}

export interface MarketDepthData {
  type: 'depth';
  symbol: string;
  exchange: string;
  bids: Array<{ price: number; quantity: number; orders: number }>;
  asks: Array<{ price: number; quantity: number; orders: number }>;
  timestamp: string;
}

export interface OHLCData {
  type: 'ohlc';
  symbol: string;
  exchange: string;
  interval: string;
  candle: {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  };
}

// Hook for streaming quotes for multiple symbols
export function useQuotesStream(symbols: string[], exchange: string = 'NSE', enabled: boolean = true) {
  const [quotes, setQuotes] = useState<QuoteData[]>([]);

  const symbolsStr = symbols.join(',');
  const url = enabled ? `${WS_BASE_URL}/ws/quotes?symbols=${symbolsStr}&exchange=${exchange}&interval=1` : '';

  const { isConnected, lastMessage } = useWebSocket({
    url,
    onMessage: (data) => {
      if (data.type === 'quotes' && data.data) {
        setQuotes(data.data);
      }
    },
    reconnect: true,
  });

  return { quotes, isConnected };
}

// Hook for streaming single symbol ticker
export function useTickerStream(symbol: string, exchange: string = 'NSE', enabled: boolean = true) {
  const [ticker, setTicker] = useState<TickerData | null>(null);
  const [priceHistory, setPriceHistory] = useState<number[]>([]);

  const url = enabled ? `${WS_BASE_URL}/ws/ticker/${symbol}?exchange=${exchange}&interval=1` : '';

  const { isConnected, lastMessage } = useWebSocket({
    url,
    onMessage: (data) => {
      if (data.type === 'ticker') {
        setTicker(data);

        // Keep last 100 price points for mini chart
        setPriceHistory((prev) => {
          const newHistory = [...prev, data.ltp];
          return newHistory.slice(-100);
        });
      }
    },
    reconnect: true,
  });

  return { ticker, priceHistory, isConnected };
}

// Hook for streaming market depth
export function useMarketDepthStream(symbol: string, exchange: string = 'NSE', enabled: boolean = true) {
  const [depth, setDepth] = useState<MarketDepthData | null>(null);

  const url = enabled ? `${WS_BASE_URL}/ws/depth/${symbol}?exchange=${exchange}&interval=2` : '';

  const { isConnected, lastMessage } = useWebSocket({
    url,
    onMessage: (data) => {
      if (data.type === 'depth') {
        setDepth(data);
      }
    },
    reconnect: true,
  });

  return { depth, isConnected };
}

// Hook for streaming OHLC candles
export function useOHLCStream(
  symbol: string,
  exchange: string = 'NSE',
  interval: string = '1m',
  enabled: boolean = true
) {
  const [candles, setCandles] = useState<OHLCData['candle'][]>([]);
  const [latestCandle, setLatestCandle] = useState<OHLCData['candle'] | null>(null);

  const url = enabled
    ? `${WS_BASE_URL}/ws/ohlc/${symbol}?exchange=${exchange}&interval=${interval}&update_interval=5`
    : '';

  const { isConnected, lastMessage } = useWebSocket({
    url,
    onMessage: (data) => {
      if (data.type === 'ohlc' && data.candle) {
        setLatestCandle(data.candle);

        // Add to candles array
        setCandles((prev) => {
          // Check if this is an update to the last candle or a new candle
          const lastCandle = prev[prev.length - 1];
          if (lastCandle && lastCandle.timestamp === data.candle.timestamp) {
            // Update last candle
            const updated = [...prev];
            updated[updated.length - 1] = data.candle;
            return updated;
          } else {
            // New candle
            const newCandles = [...prev, data.candle];
            return newCandles.slice(-200); // Keep last 200 candles
          }
        });
      }
    },
    reconnect: true,
  });

  return { candles, latestCandle, isConnected };
}

// Hook for combined market data (quotes + depth)
export function useMarketDataStream(symbol: string, exchange: string = 'NSE', enabled: boolean = true) {
  const ticker = useTickerStream(symbol, exchange, enabled);
  const depth = useMarketDepthStream(symbol, exchange, enabled);

  return {
    ticker: ticker.ticker,
    priceHistory: ticker.priceHistory,
    depth: depth.depth,
    isConnected: ticker.isConnected && depth.isConnected,
  };
}

// Utility hook for WebSocket connection status
export function useWebSocketStatus() {
  const [status, setStatus] = useState<{
    total_connections: number;
    channels: Record<string, any>;
  } | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ws/status`);
        const data = await response.json();
        setStatus(data.connection_info);
      } catch (error) {
        console.error('Failed to fetch WebSocket status:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  return status;
}
