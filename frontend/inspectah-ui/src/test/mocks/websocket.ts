/**
 * S39-W4: WebSocket Mock Utility (T-TEST-MOCK-001)
 *
 * Mock WebSocket implementation for testing real-time features.
 */
/* eslint-disable no-undef, @typescript-eslint/no-unused-vars */

import { vi } from 'vitest';
import type { WSMessage, WSMessageType } from '../../core/websocket/types';

// Re-export types for convenience
export type { WSMessage, WSMessageType };

/**
 * Mock WebSocket class for testing
 */
export class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  url: string;
  readyState: number = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  private autoConnect: boolean;
  private connectDelay: number;

  constructor(url: string, options: { autoConnect?: boolean; connectDelay?: number } = {}) {
    this.url = url;
    this.autoConnect = options.autoConnect ?? true;
    this.connectDelay = options.connectDelay ?? 10;

    if (this.autoConnect) {
      setTimeout(() => {
        this.simulateOpen();
      }, this.connectDelay);
    }
  }

  send = vi.fn((data: string) => {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
    return true;
  });

  close(code: number = 1000, reason: string = '') {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(
      new CloseEvent('close', {
        code,
        reason,
        wasClean: code === 1000,
      })
    );
  }

  /**
   * Simulate connection opening
   */
  simulateOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.(new Event('open'));
  }

  /**
   * Simulate receiving a message
   */
  simulateMessage<T = unknown>(message: WSMessage<T>) {
    this.onmessage?.(
      new MessageEvent('message', {
        data: JSON.stringify(message),
      })
    );
  }

  /**
   * Simulate receiving raw data
   */
  simulateRawMessage(data: string) {
    this.onmessage?.(new MessageEvent('message', { data }));
  }

  /**
   * Simulate a connection error
   */
  simulateError(error?: Error) {
    this.onerror?.(new ErrorEvent('error', { error }));
  }

  /**
   * Simulate unexpected disconnect
   */
  simulateDisconnect(code: number = 1006) {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(
      new CloseEvent('close', {
        code,
        wasClean: false,
      })
    );
  }
}

/**
 * Create a signal update message
 */
export function createSignalUpdate(
  signalId: string,
  value: number,
  signalType: string = 'lies_in_circulation',
  scope: string = 'national'
): WSMessage {
  return {
    type: 'signal_update' as WSMessageType,
    payload: {
      signal_id: signalId,
      signal_type: signalType,
      value,
      scope,
    },
    timestamp: new Date().toISOString(),
  };
}

/**
 * Create a notification message
 */
export function createNotification(
  title: string,
  message: string,
  type: 'info' | 'warning' | 'error' | 'success' = 'info',
  source?: string
): WSMessage {
  return {
    type: 'notification' as WSMessageType,
    payload: { title, message, type, source },
    timestamp: new Date().toISOString(),
  };
}

/**
 * Create an ingestion status message
 */
export function createIngestionStatus(
  runId: string,
  sourceId: string,
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED',
  progress: number = 0
): WSMessage {
  return {
    type: 'ingestion_status' as WSMessageType,
    payload: {
      run_id: runId,
      source_id: sourceId,
      status,
      progress,
    },
    timestamp: new Date().toISOString(),
  };
}

/**
 * Create a claim update message
 */
export function createClaimUpdate(
  claimId: string,
  action: 'created' | 'updated' | 'verified' | 'debunked',
  verdict?: string
): WSMessage {
  return {
    type: 'claim_update' as WSMessageType,
    payload: {
      claim_id: claimId,
      action,
      verdict,
    },
    timestamp: new Date().toISOString(),
  };
}

/**
 * Setup mock WebSocket globally
 */
export function setupMockWebSocket(): {
  instances: MockWebSocket[];
  reset: () => void;
} {
  const instances: MockWebSocket[] = [];

  const MockWebSocketConstructor = class extends MockWebSocket {
    constructor(url: string) {
      super(url);
      instances.push(this);
    }
  };

  globalThis.WebSocket = MockWebSocketConstructor as unknown as typeof WebSocket;

  return {
    instances,
    reset: () => {
      instances.length = 0;
    },
  };
}

/**
 * Create a mock WebSocket provider wrapper for testing
 */
export function createMockWSContext() {
  const mockClient = {
    connect: vi.fn(),
    disconnect: vi.fn(),
    send: vi.fn(() => true),
    subscribe: vi.fn(() => vi.fn()),
    subscribeAll: vi.fn(() => vi.fn()),
    isConnected: vi.fn(() => true),
    getState: vi.fn(() => ({
      isConnected: true,
      reconnectAttempts: 0,
      lastMessageAt: Date.now(),
    })),
  };

  return mockClient;
}

/**
 * Simulate a sequence of WebSocket messages
 */
export async function simulateMessageSequence(
  ws: MockWebSocket,
  messages: WSMessage[],
  delayMs: number = 100
): Promise<void> {
  for (const message of messages) {
    ws.simulateMessage(message);
    await new Promise((resolve) => setTimeout(resolve, delayMs));
  }
}

/**
 * Wait for WebSocket to be in a specific state
 */
export async function waitForState(
  ws: MockWebSocket,
  state: number,
  timeoutMs: number = 1000
): Promise<void> {
  const start = Date.now();
  while (ws.readyState !== state) {
    if (Date.now() - start > timeoutMs) {
      throw new Error(`Timeout waiting for WebSocket state ${state}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
}
