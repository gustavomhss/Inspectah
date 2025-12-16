/**
 * S39-FE-STATE: Global Store Reducer
 *
 * Pure reducer function for state management.
 */

import type { AppAction, AppState, CacheEntry } from './types';

const DEFAULT_CACHE_TTL = 5 * 60 * 1000; // 5 minutes

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

export const initialState: AppState = {
  signals: {},
  notifications: [],
  unreadCount: 0,
  wsConnected: false,
  lastSync: null,
  cache: {},
  sidebarCollapsed: false,
  activeFilters: {},
};

export function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_SIGNAL': {
      return {
        ...state,
        signals: {
          ...state.signals,
          [action.payload.id]: action.payload,
        },
      };
    }

    case 'SET_SIGNALS': {
      const signals = { ...state.signals };
      for (const signal of action.payload) {
        signals[signal.id] = signal;
      }
      return { ...state, signals };
    }

    case 'ADD_NOTIFICATION': {
      const notification = {
        ...action.payload,
        id: generateId(),
        timestamp: Date.now(),
        read: false,
      };
      return {
        ...state,
        notifications: [notification, ...state.notifications].slice(0, 100), // Keep last 100
        unreadCount: state.unreadCount + 1,
      };
    }

    case 'MARK_NOTIFICATION_READ': {
      const notifications = state.notifications.map((n) =>
        n.id === action.payload ? { ...n, read: true } : n
      );
      const unreadCount = notifications.filter((n) => !n.read).length;
      return { ...state, notifications, unreadCount };
    }

    case 'CLEAR_NOTIFICATIONS': {
      return {
        ...state,
        notifications: [],
        unreadCount: 0,
      };
    }

    case 'SET_WS_CONNECTED': {
      return { ...state, wsConnected: action.payload };
    }

    case 'SET_LAST_SYNC': {
      return { ...state, lastSync: action.payload };
    }

    case 'SET_CACHE': {
      const entry: CacheEntry<unknown> = {
        data: action.payload.data,
        timestamp: Date.now(),
        ttl: action.payload.ttl ?? DEFAULT_CACHE_TTL,
      };
      return {
        ...state,
        cache: {
          ...state.cache,
          [action.payload.key]: entry,
        },
      };
    }

    case 'INVALIDATE_CACHE': {
      const keys = Array.isArray(action.payload) ? action.payload : [action.payload];
      const cache = { ...state.cache };
      for (const key of keys) {
        delete cache[key];
      }
      return { ...state, cache };
    }

    case 'CLEAR_CACHE': {
      return { ...state, cache: {} };
    }

    case 'TOGGLE_SIDEBAR': {
      return { ...state, sidebarCollapsed: !state.sidebarCollapsed };
    }

    case 'SET_FILTER': {
      return {
        ...state,
        activeFilters: {
          ...state.activeFilters,
          [action.payload.key]: action.payload.value,
        },
      };
    }

    case 'CLEAR_FILTERS': {
      return { ...state, activeFilters: {} };
    }

    default:
      return state;
  }
}
