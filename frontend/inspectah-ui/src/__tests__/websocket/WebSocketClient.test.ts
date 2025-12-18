/**
 * Tests for WebSocket client
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WebSocketClient } from '../../core/websocket/WebSocketClient';
import type { WSMessage } from '../../core/websocket/types';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(public url: string) {
    // Simulate async connection
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event('open'));
    }, 10);
  }

  send = vi.fn();

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close', { code: code ?? 1000, reason }));
  }

  // Helper to simulate receiving a message
  simulateMessage(data: unknown) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }));
  }

  // Helper to simulate an error
  simulateError() {
    this.onerror?.(new Event('error'));
  }
}

describe('WebSocketClient', () => {
  let originalWebSocket: typeof WebSocket;

  beforeEach(() => {
    originalWebSocket = globalThis.WebSocket;
    globalThis.WebSocket = MockWebSocket as unknown as typeof WebSocket;
    vi.useFakeTimers();
  });

  afterEach(() => {
    globalThis.WebSocket = originalWebSocket;
    vi.useRealTimers();
  });

  describe('connect', () => {
    it('should connect to WebSocket server', async () => {
      const onConnect = vi.fn();
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
        onConnect,
      });

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      expect(onConnect).toHaveBeenCalled();
      expect(client.isConnected()).toBe(true);
    });

    it('should not reconnect if already connected', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      // Try to connect again
      client.connect();

      // Should still be connected with same socket
      expect(client.isConnected()).toBe(true);
    });
  });

  describe('disconnect', () => {
    it('should disconnect from server', async () => {
      const onDisconnect = vi.fn();
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
        onDisconnect,
      });

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      client.disconnect();

      expect(client.isConnected()).toBe(false);
      expect(onDisconnect).toHaveBeenCalled();
    });
  });

  describe('send', () => {
    it('should send message when connected', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      const result = client.send('heartbeat', { test: true });

      expect(result).toBe(true);
    });

    it('should return false when not connected', () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });

      const result = client.send('heartbeat', { test: true });

      expect(result).toBe(false);
    });
  });

  describe('subscribe', () => {
    it('should call handler when message of type is received', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });
      const handler = vi.fn();

      client.subscribe('signal_update', handler);
      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      // Simulate receiving a message
      const mockWs = (client as unknown as { ws: MockWebSocket }).ws;
      const message: WSMessage = {
        type: 'signal_update',
        payload: { signal_id: 'sig_1', value: 0.5 },
        timestamp: '2025-01-01T00:00:00Z',
      };
      mockWs.simulateMessage(message);

      expect(handler).toHaveBeenCalledWith(message);
    });

    it('should not call handler for different message type', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });
      const handler = vi.fn();

      client.subscribe('signal_update', handler);
      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      // Simulate receiving a different message type
      const mockWs = (client as unknown as { ws: MockWebSocket }).ws;
      mockWs.simulateMessage({
        type: 'notification',
        payload: { title: 'Test' },
        timestamp: '2025-01-01T00:00:00Z',
      });

      expect(handler).not.toHaveBeenCalled();
    });

    it('should allow unsubscribing', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });
      const handler = vi.fn();

      const unsubscribe = client.subscribe('signal_update', handler);
      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      unsubscribe();

      // Simulate receiving a message
      const mockWs = (client as unknown as { ws: MockWebSocket }).ws;
      mockWs.simulateMessage({
        type: 'signal_update',
        payload: { signal_id: 'sig_1' },
        timestamp: '2025-01-01T00:00:00Z',
      });

      expect(handler).not.toHaveBeenCalled();
    });
  });

  describe('subscribeAll', () => {
    it('should call handler for all message types', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });
      const handler = vi.fn();

      client.subscribeAll(handler);
      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      const mockWs = (client as unknown as { ws: MockWebSocket }).ws;

      mockWs.simulateMessage({
        type: 'signal_update',
        payload: {},
        timestamp: '2025-01-01T00:00:00Z',
      });

      mockWs.simulateMessage({
        type: 'notification',
        payload: {},
        timestamp: '2025-01-01T00:00:00Z',
      });

      expect(handler).toHaveBeenCalledTimes(2);
    });
  });

  describe('getState', () => {
    it('should return current state', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });

      const stateBefore = client.getState();
      expect(stateBefore.isConnected).toBe(false);
      expect(stateBefore.reconnectAttempts).toBe(0);

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      const stateAfter = client.getState();
      expect(stateAfter.isConnected).toBe(true);
    });
  });

  describe('reconnection', () => {
    it('should attempt reconnection on unexpected close', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
        reconnectInterval: 1000,
      });

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      // Simulate unexpected close
      const mockWs = (client as unknown as { ws: MockWebSocket }).ws;
      mockWs.onclose?.(new CloseEvent('close', { code: 1006 }));

      // Advance timer past reconnect interval
      await vi.advanceTimersByTimeAsync(1500);

      // Should have attempted reconnection
      const state = client.getState();
      expect(state.reconnectAttempts).toBeGreaterThan(0);
    });

    it('should not reconnect on clean close', async () => {
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
        reconnectInterval: 1000,
      });

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      // Clean disconnect
      client.disconnect();

      // Advance timer
      await vi.advanceTimersByTimeAsync(2000);

      const state = client.getState();
      expect(state.reconnectAttempts).toBe(0);
    });
  });

  describe('error handling', () => {
    it('should call onError callback', async () => {
      const onError = vi.fn();
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
        onError,
      });

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      const mockWs = (client as unknown as { ws: MockWebSocket }).ws;
      mockWs.simulateError();

      expect(onError).toHaveBeenCalled();
    });

    it('should handle malformed JSON messages', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
      const client = new WebSocketClient({
        url: 'ws://localhost:8000/ws',
      });

      client.connect();
      await vi.advanceTimersByTimeAsync(20);

      const mockWs = (client as unknown as { ws: MockWebSocket }).ws;
      mockWs.onmessage?.(new MessageEvent('message', { data: 'invalid json' }));

      expect(consoleError).toHaveBeenCalled();
      consoleError.mockRestore();
    });
  });
});
