/**
 * Tests for the global store reducer
 */

import { describe, it, expect } from 'vitest';
import { appReducer, initialState } from '../../core/store/reducer';
import type { AppAction, AppState, Signal } from '../../core/store/types';

describe('appReducer', () => {
  describe('initial state', () => {
    it('should have correct initial values', () => {
      expect(initialState.signals).toEqual({});
      expect(initialState.notifications).toEqual([]);
      expect(initialState.unreadCount).toBe(0);
      expect(initialState.wsConnected).toBe(false);
      expect(initialState.lastSync).toBeNull();
      expect(initialState.cache).toEqual({});
      expect(initialState.sidebarCollapsed).toBe(false);
      expect(initialState.activeFilters).toEqual({});
    });
  });

  describe('SET_SIGNAL', () => {
    it('should add a new signal', () => {
      const signal: Signal = {
        id: 'sig_1',
        signal_type: 'lies_in_circulation',
        value: 0.75,
        scope: 'national',
        updated_at: '2025-01-01T00:00:00Z',
      };

      const action: AppAction = { type: 'SET_SIGNAL', payload: signal };
      const newState = appReducer(initialState, action);

      expect(newState.signals['sig_1']).toEqual(signal);
    });

    it('should update existing signal', () => {
      const existingSignal: Signal = {
        id: 'sig_1',
        signal_type: 'lies_in_circulation',
        value: 0.5,
        scope: 'national',
        updated_at: '2025-01-01T00:00:00Z',
      };

      const stateWithSignal: AppState = {
        ...initialState,
        signals: { sig_1: existingSignal },
      };

      const updatedSignal: Signal = {
        ...existingSignal,
        value: 0.8,
        updated_at: '2025-01-02T00:00:00Z',
      };

      const action: AppAction = { type: 'SET_SIGNAL', payload: updatedSignal };
      const newState = appReducer(stateWithSignal, action);

      expect(newState.signals['sig_1'].value).toBe(0.8);
    });
  });

  describe('SET_SIGNALS', () => {
    it('should add multiple signals', () => {
      const signals: Signal[] = [
        {
          id: 'sig_1',
          signal_type: 'lies_in_circulation',
          value: 0.5,
          scope: 'national',
          updated_at: '2025-01-01T00:00:00Z',
        },
        {
          id: 'sig_2',
          signal_type: 'battleground_index',
          value: 0.7,
          scope: 'regional',
          updated_at: '2025-01-01T00:00:00Z',
        },
      ];

      const action: AppAction = { type: 'SET_SIGNALS', payload: signals };
      const newState = appReducer(initialState, action);

      expect(Object.keys(newState.signals)).toHaveLength(2);
      expect(newState.signals['sig_1']).toBeDefined();
      expect(newState.signals['sig_2']).toBeDefined();
    });
  });

  describe('ADD_NOTIFICATION', () => {
    it('should add a notification with generated id and timestamp', () => {
      const action: AppAction = {
        type: 'ADD_NOTIFICATION',
        payload: {
          type: 'info',
          title: 'Test Notification',
          message: 'This is a test',
        },
      };

      const newState = appReducer(initialState, action);

      expect(newState.notifications).toHaveLength(1);
      expect(newState.notifications[0].id).toBeDefined();
      expect(newState.notifications[0].timestamp).toBeDefined();
      expect(newState.notifications[0].read).toBe(false);
      expect(newState.notifications[0].title).toBe('Test Notification');
      expect(newState.unreadCount).toBe(1);
    });

    it('should prepend new notifications', () => {
      const stateWithNotification: AppState = {
        ...initialState,
        notifications: [
          {
            id: 'old',
            type: 'info',
            title: 'Old',
            message: 'Old notification',
            timestamp: 1000,
            read: false,
          },
        ],
        unreadCount: 1,
      };

      const action: AppAction = {
        type: 'ADD_NOTIFICATION',
        payload: {
          type: 'warning',
          title: 'New',
          message: 'New notification',
        },
      };

      const newState = appReducer(stateWithNotification, action);

      expect(newState.notifications).toHaveLength(2);
      expect(newState.notifications[0].title).toBe('New');
      expect(newState.notifications[1].title).toBe('Old');
      expect(newState.unreadCount).toBe(2);
    });

    it('should limit to 100 notifications', () => {
      const manyNotifications = Array.from({ length: 100 }, (_, i) => ({
        id: `n${i}`,
        type: 'info' as const,
        title: `Notification ${i}`,
        message: `Message ${i}`,
        timestamp: i,
        read: false,
      }));

      const stateWithMany: AppState = {
        ...initialState,
        notifications: manyNotifications,
        unreadCount: 100,
      };

      const action: AppAction = {
        type: 'ADD_NOTIFICATION',
        payload: {
          type: 'error',
          title: 'New',
          message: 'Should push out oldest',
        },
      };

      const newState = appReducer(stateWithMany, action);

      expect(newState.notifications).toHaveLength(100);
      expect(newState.notifications[0].title).toBe('New');
    });
  });

  describe('MARK_NOTIFICATION_READ', () => {
    it('should mark notification as read', () => {
      const stateWithUnread: AppState = {
        ...initialState,
        notifications: [
          {
            id: 'n1',
            type: 'info',
            title: 'Test',
            message: 'Test',
            timestamp: 1000,
            read: false,
          },
        ],
        unreadCount: 1,
      };

      const action: AppAction = { type: 'MARK_NOTIFICATION_READ', payload: 'n1' };
      const newState = appReducer(stateWithUnread, action);

      expect(newState.notifications[0].read).toBe(true);
      expect(newState.unreadCount).toBe(0);
    });
  });

  describe('CLEAR_NOTIFICATIONS', () => {
    it('should clear all notifications', () => {
      const stateWithNotifications: AppState = {
        ...initialState,
        notifications: [
          { id: 'n1', type: 'info', title: 'T1', message: 'M1', timestamp: 1, read: false },
          { id: 'n2', type: 'info', title: 'T2', message: 'M2', timestamp: 2, read: true },
        ],
        unreadCount: 1,
      };

      const action: AppAction = { type: 'CLEAR_NOTIFICATIONS' };
      const newState = appReducer(stateWithNotifications, action);

      expect(newState.notifications).toHaveLength(0);
      expect(newState.unreadCount).toBe(0);
    });
  });

  describe('SET_WS_CONNECTED', () => {
    it('should set connection status', () => {
      const action: AppAction = { type: 'SET_WS_CONNECTED', payload: true };
      const newState = appReducer(initialState, action);

      expect(newState.wsConnected).toBe(true);
    });
  });

  describe('SET_LAST_SYNC', () => {
    it('should set last sync timestamp', () => {
      const now = Date.now();
      const action: AppAction = { type: 'SET_LAST_SYNC', payload: now };
      const newState = appReducer(initialState, action);

      expect(newState.lastSync).toBe(now);
    });
  });

  describe('SET_CACHE', () => {
    it('should add cache entry with default TTL', () => {
      const action: AppAction = {
        type: 'SET_CACHE',
        payload: { key: 'test_key', data: { foo: 'bar' } },
      };

      const newState = appReducer(initialState, action);

      expect(newState.cache['test_key']).toBeDefined();
      expect(newState.cache['test_key'].data).toEqual({ foo: 'bar' });
      expect(newState.cache['test_key'].ttl).toBe(5 * 60 * 1000); // 5 minutes
    });

    it('should add cache entry with custom TTL', () => {
      const action: AppAction = {
        type: 'SET_CACHE',
        payload: { key: 'test_key', data: 'value', ttl: 60000 },
      };

      const newState = appReducer(initialState, action);

      expect(newState.cache['test_key'].ttl).toBe(60000);
    });
  });

  describe('INVALIDATE_CACHE', () => {
    it('should invalidate single cache key', () => {
      const stateWithCache: AppState = {
        ...initialState,
        cache: {
          key1: { data: 'a', timestamp: 0, ttl: 1000 },
          key2: { data: 'b', timestamp: 0, ttl: 1000 },
        },
      };

      const action: AppAction = { type: 'INVALIDATE_CACHE', payload: 'key1' };
      const newState = appReducer(stateWithCache, action);

      expect(newState.cache['key1']).toBeUndefined();
      expect(newState.cache['key2']).toBeDefined();
    });

    it('should invalidate multiple cache keys', () => {
      const stateWithCache: AppState = {
        ...initialState,
        cache: {
          key1: { data: 'a', timestamp: 0, ttl: 1000 },
          key2: { data: 'b', timestamp: 0, ttl: 1000 },
          key3: { data: 'c', timestamp: 0, ttl: 1000 },
        },
      };

      const action: AppAction = { type: 'INVALIDATE_CACHE', payload: ['key1', 'key2'] };
      const newState = appReducer(stateWithCache, action);

      expect(newState.cache['key1']).toBeUndefined();
      expect(newState.cache['key2']).toBeUndefined();
      expect(newState.cache['key3']).toBeDefined();
    });
  });

  describe('CLEAR_CACHE', () => {
    it('should clear all cache entries', () => {
      const stateWithCache: AppState = {
        ...initialState,
        cache: {
          key1: { data: 'a', timestamp: 0, ttl: 1000 },
          key2: { data: 'b', timestamp: 0, ttl: 1000 },
        },
      };

      const action: AppAction = { type: 'CLEAR_CACHE' };
      const newState = appReducer(stateWithCache, action);

      expect(Object.keys(newState.cache)).toHaveLength(0);
    });
  });

  describe('TOGGLE_SIDEBAR', () => {
    it('should toggle sidebar collapsed state', () => {
      const action: AppAction = { type: 'TOGGLE_SIDEBAR' };

      let state = appReducer(initialState, action);
      expect(state.sidebarCollapsed).toBe(true);

      state = appReducer(state, action);
      expect(state.sidebarCollapsed).toBe(false);
    });
  });

  describe('SET_FILTER', () => {
    it('should set filter value', () => {
      const action: AppAction = {
        type: 'SET_FILTER',
        payload: { key: 'status', value: 'active' },
      };

      const newState = appReducer(initialState, action);

      expect(newState.activeFilters['status']).toBe('active');
    });

    it('should update existing filter', () => {
      const stateWithFilter: AppState = {
        ...initialState,
        activeFilters: { status: 'active' },
      };

      const action: AppAction = {
        type: 'SET_FILTER',
        payload: { key: 'status', value: 'inactive' },
      };

      const newState = appReducer(stateWithFilter, action);

      expect(newState.activeFilters['status']).toBe('inactive');
    });
  });

  describe('CLEAR_FILTERS', () => {
    it('should clear all filters', () => {
      const stateWithFilters: AppState = {
        ...initialState,
        activeFilters: { status: 'active', type: 'admin' },
      };

      const action: AppAction = { type: 'CLEAR_FILTERS' };
      const newState = appReducer(stateWithFilters, action);

      expect(Object.keys(newState.activeFilters)).toHaveLength(0);
    });
  });

  describe('unknown action', () => {
    it('should return unchanged state for unknown action', () => {
      const unknownAction = { type: 'UNKNOWN_ACTION' } as unknown as AppAction;
      const newState = appReducer(initialState, unknownAction);

      expect(newState).toBe(initialState);
    });
  });
});
