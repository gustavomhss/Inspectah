/**
 * S40-FE-008: useTruthTwin Hook
 *
 * React hook for fetching and managing Truth Twin data.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  TruthTwinResponse,
  DecisionInspectResponse,
  TruthApiError,
  UseTruthTwinResult,
  UseDecisionInspectResult,
} from '../types';
import { getTruthTwin, inspectDecision, getDecisionTimeline } from '../api/truthApi';

// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

// Simple in-memory cache
interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const cache = new Map<string, CacheEntry<unknown>>();

function getFromCache<T>(key: string): T | null {
  const entry = cache.get(key);
  if (!entry) return null;

  const isExpired = Date.now() - entry.timestamp > CACHE_DURATION;
  if (isExpired) {
    cache.delete(key);
    return null;
  }

  return entry.data as T;
}

function setCache<T>(key: string, data: T): void {
  cache.set(key, { data, timestamp: Date.now() });
}

/**
 * Hook for fetching Truth Twin data
 *
 * @param claimId - The claim ID to fetch
 * @param options - Hook options
 */
export function useTruthTwin(
  claimId: string | null | undefined,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
    useCache?: boolean;
  }
): UseTruthTwinResult {
  const { enabled = true, refetchInterval, useCache = true } = options || {};

  const [data, setData] = useState<TruthTwinResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<TruthApiError | null>(null);

  const mountedRef = useRef(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Set mounted on first render
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const fetchData = useCallback(async () => {
    if (!claimId || !enabled) {
      return;
    }

    // Check cache first
    const cacheKey = `truth-twin-${claimId}`;
    if (useCache) {
      const cached = getFromCache<TruthTwinResponse>(cacheKey);
      if (cached) {
        setData(cached);
        return;
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await getTruthTwin(claimId);

      if (mountedRef.current) {
        setData(result);
        if (useCache) {
          setCache(cacheKey, result);
        }
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err as TruthApiError);
      }
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [claimId, enabled, useCache]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Refetch interval
  useEffect(() => {
    if (refetchInterval && refetchInterval > 0 && enabled && claimId) {
      intervalRef.current = setInterval(fetchData, refetchInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchData, refetchInterval, enabled, claimId]);

  const refetch = useCallback(async () => {
    // Force refetch by clearing cache
    if (claimId) {
      cache.delete(`truth-twin-${claimId}`);
    }
    await fetchData();
  }, [claimId, fetchData]);

  return {
    data,
    isLoading,
    error,
    refetch,
  };
}

/**
 * Hook for inspecting a specific decision
 *
 * @param decisionId - The decision ID to inspect
 * @param options - Hook options
 */
export function useDecisionInspect(
  decisionId: string | null | undefined,
  options?: {
    enabled?: boolean;
    useCache?: boolean;
  }
): UseDecisionInspectResult {
  const { enabled = true, useCache = true } = options || {};

  const [data, setData] = useState<DecisionInspectResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<TruthApiError | null>(null);

  const mountedRef = useRef(false);

  // Set mounted on first render
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const fetchData = useCallback(async () => {
    if (!decisionId || !enabled) {
      return;
    }

    // Check cache first
    const cacheKey = `decision-inspect-${decisionId}`;
    if (useCache) {
      const cached = getFromCache<DecisionInspectResponse>(cacheKey);
      if (cached) {
        setData(cached);
        return;
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await inspectDecision(decisionId);

      if (mountedRef.current) {
        setData(result);
        if (useCache) {
          setCache(cacheKey, result);
        }
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err as TruthApiError);
      }
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [decisionId, enabled, useCache]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(async () => {
    // Force refetch by clearing cache
    if (decisionId) {
      cache.delete(`decision-inspect-${decisionId}`);
    }
    await fetchData();
  }, [decisionId, fetchData]);

  return {
    data,
    isLoading,
    error,
    refetch,
  };
}

/**
 * Hook for fetching decision timeline
 *
 * @param claimId - The claim ID
 * @param options - Hook options
 */
export function useDecisionTimeline(
  claimId: string | null | undefined,
  options?: {
    enabled?: boolean;
    limit?: number;
    useCache?: boolean;
  }
) {
  const { enabled = true, limit, useCache = true } = options || {};

  const [data, setData] = useState<{
    timeline: TruthTwinResponse['decision_timeline'];
    count: number;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<TruthApiError | null>(null);

  const mountedRef = useRef(false);

  // Set mounted on first render
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const fetchData = useCallback(async () => {
    if (!claimId || !enabled) {
      return;
    }

    const cacheKey = `timeline-${claimId}-${limit || 'default'}`;
    if (useCache) {
      const cached = getFromCache<typeof data>(cacheKey);
      if (cached) {
        setData(cached);
        return;
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await getDecisionTimeline(claimId, limit);

      if (mountedRef.current) {
        const timelineData = { timeline: result.timeline, count: result.count };
        setData(timelineData);
        if (useCache) {
          setCache(cacheKey, timelineData);
        }
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err as TruthApiError);
      }
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [claimId, enabled, limit, useCache]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(async () => {
    if (claimId) {
      cache.delete(`timeline-${claimId}-${limit || 'default'}`);
    }
    await fetchData();
  }, [claimId, limit, fetchData]);

  return {
    data,
    isLoading,
    error,
    refetch,
  };
}

// Export utility to clear all cache
export function clearTruthCache(): void {
  cache.clear();
}
