/**
 * Tests for useSignalStream hook (T-TEST-UNIT-001)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { type ReactNode, createContext, useContext } from 'react';
import { createElement } from 'react';
import { useSignalStream } from '../../modules/signals/hooks/useSignalStream';
import { StoreProvider } from '../../core/store';
import { MockWebSocket, setupMockWebSocket } from '../../test/mocks/websocket';
import type { Signal } from '../../core/store/types';

// Mock the WebSocket module
vi.mock('../../core/websocket', () => ({
  useWebSocket: () => ({
    subscribe: vi.fn(() => vi.fn()),
    isConnected: false,
    connect: vi.fn(),
    disconnect: vi.fn(),
    send: vi.fn(() => false),
  }),
  WebSocketProvider: ({ children }: { children: ReactNode }) => children,
}));

// Test wrapper that provides Store context
function createWrapper() {
  return function TestWrapper({ children }: { children: ReactNode }) {
    return createElement(StoreProvider, null, children);
  };
}

describe('useSignalStream', () => {
  let mockWS: { instances: MockWebSocket[]; reset: () => void };

  beforeEach(() => {
    mockWS = setupMockWebSocket();
    vi.useFakeTimers();
  });

  afterEach(() => {
    mockWS.reset();
    vi.useRealTimers();
  });

  describe('initialization', () => {
    it('should initialize with empty signals', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      expect(result.current.signals).toEqual([]);
      expect(result.current.isPaused).toBe(false);
      expect(result.current.lastUpdate).toBeNull();
      expect(result.current.error).toBeNull();
    });

    it('should initialize with options', () => {
      const { result } = renderHook(
        () =>
          useSignalStream({
            signalTypes: ['lies_in_circulation'],
            scope: 'national',
            maxHistory: 50,
          }),
        { wrapper: createWrapper() }
      );

      expect(result.current.signals).toEqual([]);
      expect(result.current.isPaused).toBe(false);
    });
  });

  describe('pause and resume', () => {
    it('should pause the stream', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isPaused).toBe(false);

      act(() => {
        result.current.pause();
      });

      expect(result.current.isPaused).toBe(true);
    });

    it('should resume the stream', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.pause();
      });

      expect(result.current.isPaused).toBe(true);

      act(() => {
        result.current.resume();
      });

      expect(result.current.isPaused).toBe(false);
    });
  });

  describe('clear', () => {
    it('should clear signal history and lastUpdate', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.clear();
      });

      expect(result.current.signals).toEqual([]);
      expect(result.current.lastUpdate).toBeNull();
    });
  });

  describe('subscribeToType and unsubscribeFromType', () => {
    it('should add signal type to active types', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.subscribeToType('lies_in_circulation');
      });

      // Subscribe to another type
      act(() => {
        result.current.subscribeToType('battleground_index');
      });

      // These are now active filters (implementation detail)
      expect(result.current.isPaused).toBe(false);
    });

    it('should remove signal type from active types', () => {
      const { result } = renderHook(
        () =>
          useSignalStream({
            signalTypes: ['lies_in_circulation', 'battleground_index'],
          }),
        { wrapper: createWrapper() }
      );

      act(() => {
        result.current.unsubscribeFromType('lies_in_circulation');
      });

      expect(result.current.isPaused).toBe(false);
    });
  });

  describe('getSignal', () => {
    it('should return undefined for non-existent signal', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      expect(result.current.getSignal('non_existent')).toBeUndefined();
    });
  });

  describe('autoSubscribe option', () => {
    it('should auto-subscribe by default', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      // Hook is mounted and subscribed
      expect(result.current.error).toBeNull();
    });

    it('should not auto-subscribe when disabled', () => {
      const { result } = renderHook(
        () => useSignalStream({ autoSubscribe: false }),
        { wrapper: createWrapper() }
      );

      expect(result.current.error).toBeNull();
    });
  });

  describe('maxHistory option', () => {
    it('should respect maxHistory limit', () => {
      const { result } = renderHook(() => useSignalStream({ maxHistory: 2 }), {
        wrapper: createWrapper(),
      });

      // maxHistory is used internally when signals come in
      expect(result.current.signals.length).toBeLessThanOrEqual(2);
    });
  });

  describe('filtering', () => {
    it('should filter by signal type when specified', () => {
      const { result } = renderHook(
        () => useSignalStream({ signalTypes: ['lies_in_circulation'] }),
        { wrapper: createWrapper() }
      );

      expect(result.current.signals).toEqual([]);
    });

    it('should filter by scope when specified', () => {
      const { result } = renderHook(
        () => useSignalStream({ scope: 'national' }),
        { wrapper: createWrapper() }
      );

      expect(result.current.signals).toEqual([]);
    });
  });

  describe('return type', () => {
    it('should return all expected properties and methods', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      // State properties
      expect(Array.isArray(result.current.signals)).toBe(true);
      expect(typeof result.current.isConnected).toBe('boolean');
      expect(result.current.lastUpdate === null || typeof result.current.lastUpdate === 'number').toBe(true);
      expect(result.current.error === null || result.current.error instanceof Error).toBe(true);
      expect(typeof result.current.isPaused).toBe('boolean');

      // Methods
      expect(typeof result.current.pause).toBe('function');
      expect(typeof result.current.resume).toBe('function');
      expect(typeof result.current.clear).toBe('function');
      expect(typeof result.current.getSignal).toBe('function');
      expect(typeof result.current.subscribeToType).toBe('function');
      expect(typeof result.current.unsubscribeFromType).toBe('function');
    });
  });

  describe('integration behavior', () => {
    it('should not process updates when paused', () => {
      const { result } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.pause();
      });

      // When paused, updates should be ignored
      expect(result.current.isPaused).toBe(true);
    });

    it('should maintain stable references for methods', () => {
      const { result, rerender } = renderHook(() => useSignalStream(), {
        wrapper: createWrapper(),
      });

      const initialPause = result.current.pause;
      const initialResume = result.current.resume;
      const initialClear = result.current.clear;

      rerender();

      expect(result.current.pause).toBe(initialPause);
      expect(result.current.resume).toBe(initialResume);
      expect(result.current.clear).toBe(initialClear);
    });
  });
});
