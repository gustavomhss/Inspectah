/**
 * S39-FE-WS: WebSocket Provider
 *
 * React context provider for WebSocket connection management.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { useStore } from '../store';
import { WebSocketClient } from './WebSocketClient';
import type {
  IngestionStatusPayload,
  NotificationPayload,
  SignalUpdatePayload,
  WSEventHandler,
  WSMessage,
  WSMessageType,
} from './types';

interface WebSocketContextValue {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  send: <T>(type: WSMessageType, payload: T) => boolean;
  subscribe: <T>(type: WSMessageType, handler: WSEventHandler<T>) => () => void;
}

const WebSocketContext = createContext<WebSocketContextValue | undefined>(undefined);

interface WebSocketProviderProps {
  children: ReactNode;
  url?: string;
  autoConnect?: boolean;
}

export function WebSocketProvider({
  children,
  url,
  autoConnect = true,
}: WebSocketProviderProps) {
  const { dispatch, addNotification } = useStore();
  const [isConnected, setIsConnected] = useState(false);
  const clientRef = useRef<WebSocketClient | null>(null);

  // Get WebSocket URL from env or prop
  const wsUrl = url ?? import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/ws';

  // Initialize client
  useEffect(() => {
    const client = new WebSocketClient({
      url: wsUrl,
      onConnect: () => {
        setIsConnected(true);
        dispatch({ type: 'SET_WS_CONNECTED', payload: true });
        dispatch({ type: 'SET_LAST_SYNC', payload: Date.now() });
      },
      onDisconnect: () => {
        setIsConnected(false);
        dispatch({ type: 'SET_WS_CONNECTED', payload: false });
      },
      onError: () => {
        addNotification({
          type: 'error',
          title: 'Connection Error',
          message: 'WebSocket connection failed. Retrying...',
          source: 'websocket',
        });
      },
    });

    clientRef.current = client;

    // Setup message handlers
    const unsubscribers: Array<() => void> = [];

    // Handle signal updates
    unsubscribers.push(
      client.subscribe<SignalUpdatePayload>('signal_update', (msg) => {
        dispatch({
          type: 'SET_SIGNAL',
          payload: {
            id: msg.payload.signal_id,
            signal_type: msg.payload.signal_type,
            value: msg.payload.value,
            scope: msg.payload.scope,
            updated_at: msg.timestamp,
          },
        });
      })
    );

    // Handle notifications
    unsubscribers.push(
      client.subscribe<NotificationPayload>('notification', (msg) => {
        addNotification({
          type: msg.payload.type,
          title: msg.payload.title,
          message: msg.payload.message,
          source: msg.payload.source,
        });
      })
    );

    // Handle ingestion status
    unsubscribers.push(
      client.subscribe<IngestionStatusPayload>('ingestion_status', (msg) => {
        // Invalidate ingestion cache when status changes
        dispatch({
          type: 'INVALIDATE_CACHE',
          payload: ['ingestion_runs', `ingestion_run_${msg.payload.run_id}`],
        });
      })
    );

    // Handle heartbeat for sync tracking
    unsubscribers.push(
      client.subscribe('heartbeat', () => {
        dispatch({ type: 'SET_LAST_SYNC', payload: Date.now() });
      })
    );

    if (autoConnect) {
      client.connect();
    }

    return () => {
      unsubscribers.forEach((unsub) => unsub());
      client.disconnect();
    };
  }, [wsUrl, autoConnect, dispatch, addNotification]);

  const connect = useCallback(() => {
    clientRef.current?.connect();
  }, []);

  const disconnect = useCallback(() => {
    clientRef.current?.disconnect();
  }, []);

  const send = useCallback(<T,>(type: WSMessageType, payload: T): boolean => {
    return clientRef.current?.send(type, payload) ?? false;
  }, []);

  const subscribe = useCallback(
    <T,>(type: WSMessageType, handler: WSEventHandler<T>): (() => void) => {
      return clientRef.current?.subscribe(type, handler) ?? (() => {});
    },
    []
  );

  const value = useMemo<WebSocketContextValue>(
    () => ({
      isConnected,
      connect,
      disconnect,
      send,
      subscribe,
    }),
    [isConnected, connect, disconnect, send, subscribe]
  );

  return (
    <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>
  );
}

export function useWebSocket(): WebSocketContextValue {
  const ctx = useContext(WebSocketContext);
  if (!ctx) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return ctx;
}

// Hook for subscribing to specific message types
export function useWSSubscription<T>(
  type: WSMessageType,
  handler: (payload: T, message: WSMessage<T>) => void
): void {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe<T>(type, (message) => {
      handler(message.payload, message);
    });
    return unsubscribe;
  }, [type, handler, subscribe]);
}
