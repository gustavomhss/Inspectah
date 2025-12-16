/**
 * S39-FE-WS: WebSocket Client
 *
 * WebSocket client with automatic reconnection and message handling.
 */

import type {
  WSClientConfig,
  WSClientState,
  WSEventHandler,
  WSMessage,
  WSMessageType,
} from './types';

const DEFAULT_RECONNECT_INTERVAL = 3000;
const DEFAULT_MAX_RECONNECT_ATTEMPTS = 10;
const DEFAULT_HEARTBEAT_INTERVAL = 30000;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private config: Required<WSClientConfig>;
  private state: WSClientState = {
    isConnected: false,
    reconnectAttempts: 0,
    lastMessageTime: null,
  };
  private handlers: Map<WSMessageType, Set<WSEventHandler>> = new Map();
  private globalHandlers: Set<WSEventHandler> = new Set();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;

  constructor(config: WSClientConfig) {
    this.config = {
      reconnectInterval: DEFAULT_RECONNECT_INTERVAL,
      maxReconnectAttempts: DEFAULT_MAX_RECONNECT_ATTEMPTS,
      heartbeatInterval: DEFAULT_HEARTBEAT_INTERVAL,
      onConnect: () => {},
      onDisconnect: () => {},
      onError: () => {},
      ...config,
    };
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      this.ws = new WebSocket(this.config.url);
      this.setupEventHandlers();
    } catch (error) {
      console.error('[WS] Connection error:', error);
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    this.clearTimers();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.state.isConnected = false;
    this.state.reconnectAttempts = 0;
  }

  send<T>(type: WSMessageType, payload: T): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WS] Cannot send message: not connected');
      return false;
    }

    const message: WSMessage<T> = {
      type,
      payload,
      timestamp: new Date().toISOString(),
      id: this.generateMessageId(),
    };

    try {
      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('[WS] Send error:', error);
      return false;
    }
  }

  subscribe<T = unknown>(type: WSMessageType, handler: WSEventHandler<T>): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler as WSEventHandler);

    return () => {
      this.handlers.get(type)?.delete(handler as WSEventHandler);
    };
  }

  subscribeAll(handler: WSEventHandler): () => void {
    this.globalHandlers.add(handler);
    return () => {
      this.globalHandlers.delete(handler);
    };
  }

  getState(): Readonly<WSClientState> {
    return { ...this.state };
  }

  isConnected(): boolean {
    return this.state.isConnected;
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('[WS] Connected');
      this.state.isConnected = true;
      this.state.reconnectAttempts = 0;
      this.startHeartbeat();
      this.config.onConnect();
    };

    this.ws.onclose = (event) => {
      console.log('[WS] Disconnected:', event.code, event.reason);
      this.state.isConnected = false;
      this.clearTimers();
      this.config.onDisconnect();

      if (event.code !== 1000) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (event) => {
      console.error('[WS] Error:', event);
      this.config.onError(event);
    };

    this.ws.onmessage = (event) => {
      this.handleMessage(event);
    };
  }

  private handleMessage(event: MessageEvent): void {
    this.state.lastMessageTime = Date.now();

    try {
      const message = JSON.parse(event.data as string) as WSMessage;

      // Notify global handlers
      for (const handler of this.globalHandlers) {
        try {
          handler(message);
        } catch (error) {
          console.error('[WS] Global handler error:', error);
        }
      }

      // Notify type-specific handlers
      const typeHandlers = this.handlers.get(message.type);
      if (typeHandlers) {
        for (const handler of typeHandlers) {
          try {
            handler(message);
          } catch (error) {
            console.error(`[WS] Handler error for ${message.type}:`, error);
          }
        }
      }
    } catch (error) {
      console.error('[WS] Message parse error:', error);
    }
  }

  private scheduleReconnect(): void {
    if (this.state.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      return;
    }

    const delay = this.config.reconnectInterval * Math.pow(1.5, this.state.reconnectAttempts);
    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.state.reconnectAttempts + 1})`);

    this.reconnectTimer = setTimeout(() => {
      this.state.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.send('heartbeat', { client_time: new Date().toISOString() });
    }, this.config.heartbeatInterval);
  }

  private clearTimers(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private generateMessageId(): string {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
  }
}

// Singleton instance for global use
let globalClient: WebSocketClient | null = null;

export function getWebSocketClient(config?: WSClientConfig): WebSocketClient {
  if (!globalClient && config) {
    globalClient = new WebSocketClient(config);
  }
  if (!globalClient) {
    throw new Error('WebSocket client not initialized. Call with config first.');
  }
  return globalClient;
}

export function initWebSocketClient(config: WSClientConfig): WebSocketClient {
  if (globalClient) {
    globalClient.disconnect();
  }
  globalClient = new WebSocketClient(config);
  return globalClient;
}
