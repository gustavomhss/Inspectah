/**
 * S39-FE-STATE: Global Store Types
 *
 * Type definitions for the global application state.
 */

export interface Signal {
  id: string;
  signal_type: string;
  value: number;
  scope: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
  source?: string;
}

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export interface AppState {
  // Real-time signals
  signals: Record<string, Signal>;

  // Notifications
  notifications: Notification[];
  unreadCount: number;

  // Connection status
  wsConnected: boolean;
  lastSync: number | null;

  // Request cache
  cache: Record<string, CacheEntry<unknown>>;

  // UI state
  sidebarCollapsed: boolean;
  activeFilters: Record<string, unknown>;
}

export type AppAction =
  | { type: 'SET_SIGNAL'; payload: Signal }
  | { type: 'SET_SIGNALS'; payload: Signal[] }
  | { type: 'ADD_NOTIFICATION'; payload: Omit<Notification, 'id' | 'timestamp' | 'read'> }
  | { type: 'MARK_NOTIFICATION_READ'; payload: string }
  | { type: 'CLEAR_NOTIFICATIONS' }
  | { type: 'SET_WS_CONNECTED'; payload: boolean }
  | { type: 'SET_LAST_SYNC'; payload: number }
  | { type: 'SET_CACHE'; payload: { key: string; data: unknown; ttl?: number } }
  | { type: 'INVALIDATE_CACHE'; payload: string | string[] }
  | { type: 'CLEAR_CACHE' }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_FILTER'; payload: { key: string; value: unknown } }
  | { type: 'CLEAR_FILTERS' };

export interface StoreContextValue {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;

  // Convenience methods
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;

  // Cache methods
  getCache: <T>(key: string) => T | null;
  setCache: <T>(key: string, data: T, ttl?: number) => void;
  invalidateCache: (keys: string | string[]) => void;
}
