/**
 * S39-FE-STATE: Global Store Provider
 *
 * React context provider for global application state.
 */

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useReducer,
  type ReactNode,
} from 'react';
import { appReducer, initialState } from './reducer';
import type { Notification, StoreContextValue } from './types';

const StoreContext = createContext<StoreContextValue | undefined>(undefined);

export function StoreProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const addNotification = useCallback(
    (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
      dispatch({ type: 'ADD_NOTIFICATION', payload: notification });
    },
    []
  );

  const markNotificationRead = useCallback((id: string) => {
    dispatch({ type: 'MARK_NOTIFICATION_READ', payload: id });
  }, []);

  const clearNotifications = useCallback(() => {
    dispatch({ type: 'CLEAR_NOTIFICATIONS' });
  }, []);

  const getCache = useCallback(
    <T,>(key: string): T | null => {
      const entry = state.cache[key];
      if (!entry) return null;

      const isExpired = Date.now() - entry.timestamp > entry.ttl;
      if (isExpired) {
        dispatch({ type: 'INVALIDATE_CACHE', payload: key });
        return null;
      }

      return entry.data as T;
    },
    [state.cache]
  );

  const setCache = useCallback(<T,>(key: string, data: T, ttl?: number) => {
    dispatch({ type: 'SET_CACHE', payload: { key, data, ttl } });
  }, []);

  const invalidateCache = useCallback((keys: string | string[]) => {
    dispatch({ type: 'INVALIDATE_CACHE', payload: keys });
  }, []);

  const value = useMemo<StoreContextValue>(
    () => ({
      state,
      dispatch,
      addNotification,
      markNotificationRead,
      clearNotifications,
      getCache,
      setCache,
      invalidateCache,
    }),
    [
      state,
      addNotification,
      markNotificationRead,
      clearNotifications,
      getCache,
      setCache,
      invalidateCache,
    ]
  );

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore(): StoreContextValue {
  const ctx = useContext(StoreContext);
  if (!ctx) {
    throw new Error('useStore must be used within StoreProvider');
  }
  return ctx;
}

// Selector hooks for specific state slices
export function useSignals() {
  const { state } = useStore();
  return state.signals;
}

export function useSignal(id: string) {
  const { state } = useStore();
  return state.signals[id] ?? null;
}

export function useNotifications() {
  const { state, markNotificationRead, clearNotifications } = useStore();
  return {
    notifications: state.notifications,
    unreadCount: state.unreadCount,
    markRead: markNotificationRead,
    clearAll: clearNotifications,
  };
}

export function useConnectionStatus() {
  const { state } = useStore();
  return {
    isConnected: state.wsConnected,
    lastSync: state.lastSync,
  };
}

export function useSidebar() {
  const { state, dispatch } = useStore();
  const toggle = useCallback(() => {
    dispatch({ type: 'TOGGLE_SIDEBAR' });
  }, [dispatch]);

  return {
    isCollapsed: state.sidebarCollapsed,
    toggle,
  };
}

export function useFilters() {
  const { state, dispatch } = useStore();

  const setFilter = useCallback(
    (key: string, value: unknown) => {
      dispatch({ type: 'SET_FILTER', payload: { key, value } });
    },
    [dispatch]
  );

  const clearFilters = useCallback(() => {
    dispatch({ type: 'CLEAR_FILTERS' });
  }, [dispatch]);

  return {
    filters: state.activeFilters,
    setFilter,
    clearFilters,
  };
}
