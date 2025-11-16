import { useState, useEffect, useRef, useCallback } from 'react';

export interface WebSocketOptions {
  url: string;
  onOpen?: (event: Event) => void;
  onMessage?: (data: any) => void;
  onError?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
  reconnectAttempts?: number;
}

export interface WebSocketHook {
  isConnected: boolean;
  isConnecting: boolean;
  lastMessage: any;
  sendMessage: (message: any) => void;
  sendJsonMessage: (message: object) => void;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(options: WebSocketOptions): WebSocketHook {
  const {
    url,
    onOpen,
    onMessage,
    onError,
    onClose,
    reconnect = true,
    reconnectInterval = 3000,
    reconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectCountRef = useRef(0);
  const shouldReconnectRef = useRef(reconnect);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || isConnecting) {
      return;
    }

    setIsConnecting(true);

    try {
      const ws = new WebSocket(url);

      ws.onopen = (event) => {
        console.log('WebSocket connected:', url);
        setIsConnected(true);
        setIsConnecting(false);
        reconnectCountRef.current = 0;
        onOpen?.(event);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setIsConnecting(false);
        onError?.(event);
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        setIsConnecting(false);
        wsRef.current = null;
        onClose?.(event);

        // Attempt reconnection
        if (
          shouldReconnectRef.current &&
          reconnectCountRef.current < reconnectAttempts
        ) {
          reconnectCountRef.current += 1;
          console.log(
            `Reconnecting... Attempt ${reconnectCountRef.current}/${reconnectAttempts}`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else if (reconnectCountRef.current >= reconnectAttempts) {
          console.error('Max reconnect attempts reached');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setIsConnecting(false);
    }
  }, [url, onOpen, onMessage, onError, onClose, reconnectInterval, reconnectAttempts, isConnecting]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message);
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const sendJsonMessage = useCallback((message: object) => {
    sendMessage(JSON.stringify(message));
  }, [sendMessage]);

  // Auto-connect on mount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  // Ping/heartbeat to keep connection alive
  useEffect(() => {
    if (!isConnected) return;

    const pingInterval = setInterval(() => {
      sendJsonMessage({ command: 'ping', timestamp: Date.now() });
    }, 30000); // Ping every 30 seconds

    return () => clearInterval(pingInterval);
  }, [isConnected, sendJsonMessage]);

  return {
    isConnected,
    isConnecting,
    lastMessage,
    sendMessage,
    sendJsonMessage,
    connect,
    disconnect,
  };
}
