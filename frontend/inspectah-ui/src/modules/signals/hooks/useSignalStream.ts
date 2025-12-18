/**
 * S39-W4: useSignalStream Hook (T-TEST-UNIT-001)
 *
 * Hook for subscribing to real-time signal updates via WebSocket.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { useWebSocket } from '../../../core/websocket';
import { useStore, useSignals } from '../../../core/store';
import type { Signal } from '../../../core/store/types';
import type { SignalUpdatePayload, WSMessage } from '../../../core/websocket/types';

/**
 * Signal stream options
 */
export interface UseSignalStreamOptions {
  /** Filter signals by type */
  signalTypes?: string[];
  /** Filter signals by scope */
  scope?: string;
  /** Maximum number of signals to keep in history */
  maxHistory?: number;
  /** Auto-subscribe on mount */
  autoSubscribe?: boolean;
}

/**
 * Signal stream state
 */
export interface SignalStreamState {
  /** Current signals */
  signals: Signal[];
  /** Whether currently connected */
  isConnected: boolean;
  /** Last update timestamp */
  lastUpdate: number | null;
  /** Error if any */
  error: Error | null;
  /** Whether stream is paused */
  isPaused: boolean;
}

/**
 * Signal stream return type
 */
export interface UseSignalStreamReturn extends SignalStreamState {
  /** Pause the stream */
  pause: () => void;
  /** Resume the stream */
  resume: () => void;
  /** Clear signal history */
  clear: () => void;
  /** Get a specific signal by ID */
  getSignal: (id: string) => Signal | undefined;
  /** Subscribe to a specific signal type */
  subscribeToType: (type: string) => void;
  /** Unsubscribe from a specific signal type */
  unsubscribeFromType: (type: string) => void;
}

/**
 * Hook for real-time signal streaming
 */
export function useSignalStream(options: UseSignalStreamOptions = {}): UseSignalStreamReturn {
  const {
    signalTypes: initialTypes = [],
    scope,
    maxHistory = 100,
    autoSubscribe = true,
  } = options;

  const { subscribe, isConnected } = useWebSocket();
  const { state, dispatch } = useStore();
  const storeSignals = useSignals();
  const [signalHistory, setSignalHistory] = useState<Signal[]>([]);
  const [lastUpdate, setLastUpdate] = useState<number | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [activeTypes, setActiveTypes] = useState<Set<string>>(new Set(initialTypes));

  const unsubscribeRef = useRef<(() => void) | null>(null);
  const isPausedRef = useRef(isPaused);
  isPausedRef.current = isPaused;

  // Handle incoming signal updates
  const handleSignalUpdate = useCallback(
    (message: WSMessage<SignalUpdatePayload>) => {
      if (isPausedRef.current) return;

      const payload = message.payload;
      const signal: Signal = {
        id: payload.signal_id,
        signal_type: payload.signal_type,
        value: payload.value,
        scope: payload.scope,
        updated_at: message.timestamp,
      };

      // Filter by type if specified
      if (activeTypes.size > 0 && !activeTypes.has(signal.signal_type)) {
        return;
      }

      // Filter by scope if specified
      if (scope && signal.scope !== scope) {
        return;
      }

      // Update global store
      dispatch({ type: 'SET_SIGNAL', payload: signal });

      // Update local history
      setSignalHistory((prev) => {
        const updated = [signal, ...prev.filter((s) => s.id !== signal.id)];
        return updated.slice(0, maxHistory);
      });

      setLastUpdate(Date.now());
      setError(null);
    },
    [activeTypes, scope, maxHistory, dispatch]
  );

  // Subscribe to WebSocket signal updates
  useEffect(() => {
    if (!autoSubscribe) return;

    try {
      unsubscribeRef.current = subscribe<SignalUpdatePayload>('signal_update', handleSignalUpdate);
    } catch (err) {
      setError(err as Error);
    }

    return () => {
      unsubscribeRef.current?.();
    };
  }, [subscribe, handleSignalUpdate, autoSubscribe]);

  // Get signals from store filtered by active types
  const getFilteredSignals = useCallback((): Signal[] => {
    const allSignals = Object.values(state.signals);

    if (activeTypes.size === 0 && !scope) {
      return allSignals;
    }

    return allSignals.filter((signal) => {
      const matchesType = activeTypes.size === 0 || activeTypes.has(signal.signal_type);
      const matchesScope = !scope || signal.scope === scope;
      return matchesType && matchesScope;
    });
  }, [state.signals, activeTypes, scope]);

  // Pause the stream
  const pause = useCallback(() => {
    setIsPaused(true);
  }, []);

  // Resume the stream
  const resume = useCallback(() => {
    setIsPaused(false);
  }, []);

  // Clear signal history
  const clear = useCallback(() => {
    setSignalHistory([]);
    setLastUpdate(null);
  }, []);

  // Get a specific signal by ID
  const getSignal = useCallback(
    (id: string): Signal | undefined => {
      return state.signals[id];
    },
    [state.signals]
  );

  // Subscribe to a specific signal type
  const subscribeToType = useCallback((type: string) => {
    setActiveTypes((prev) => new Set([...prev, type]));
  }, []);

  // Unsubscribe from a specific signal type
  const unsubscribeFromType = useCallback((type: string) => {
    setActiveTypes((prev) => {
      const next = new Set(prev);
      next.delete(type);
      return next;
    });
  }, []);

  return {
    signals: signalHistory.length > 0 ? signalHistory : getFilteredSignals(),
    isConnected,
    lastUpdate,
    error,
    isPaused,
    pause,
    resume,
    clear,
    getSignal,
    subscribeToType,
    unsubscribeFromType,
  };
}

export default useSignalStream;
