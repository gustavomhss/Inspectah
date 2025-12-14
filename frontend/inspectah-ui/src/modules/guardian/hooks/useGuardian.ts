/**
 * Guardian Hooks — S37
 */

import { useCallback, useState } from 'react';
import { endpoints } from '../../../core/api/endpoints';
import { fetchApi } from '../../../core/api/fetchApi';
import type {
  GuardianDecision,
  GuardianMetrics,
  GuardianPolicy,
  ReviewQueueItem,
  ReviewQueueStats,
} from '../types';

interface UseGuardianMetricsReturn {
  metrics: GuardianMetrics | null;
  loading: boolean;
  error: string | null;
  load: () => Promise<void>;
}

export function useGuardianMetrics(): UseGuardianMetricsReturn {
  const [metrics, setMetrics] = useState<GuardianMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchApi<GuardianMetrics>(endpoints.admin.guardian.metrics);
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar métricas');
    } finally {
      setLoading(false);
    }
  }, []);

  return { metrics, loading, error, load };
}

interface UseGuardianDecisionsReturn {
  decisions: GuardianDecision[];
  loading: boolean;
  error: string | null;
  load: (statusFilter?: string) => Promise<void>;
}

export function useGuardianDecisions(): UseGuardianDecisionsReturn {
  const [decisions, setDecisions] = useState<GuardianDecision[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (statusFilter?: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = statusFilter
        ? `${endpoints.admin.guardian.decisions}?status_filter=${encodeURIComponent(statusFilter)}`
        : endpoints.admin.guardian.decisions;
      const data = await fetchApi<GuardianDecision[]>(url);
      setDecisions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar decisões');
    } finally {
      setLoading(false);
    }
  }, []);

  return { decisions, loading, error, load };
}

interface UseAwaitingReviewReturn {
  decisions: GuardianDecision[];
  loading: boolean;
  error: string | null;
  load: () => Promise<void>;
}

export function useAwaitingReview(): UseAwaitingReviewReturn {
  const [decisions, setDecisions] = useState<GuardianDecision[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchApi<GuardianDecision[]>(endpoints.admin.guardian.awaitingReview);
      setDecisions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar fila de revisão');
    } finally {
      setLoading(false);
    }
  }, []);

  return { decisions, loading, error, load };
}

interface UseReviewQueueReturn {
  items: ReviewQueueItem[];
  stats: ReviewQueueStats | null;
  loading: boolean;
  error: string | null;
  load: () => Promise<void>;
}

export function useReviewQueue(): UseReviewQueueReturn {
  const [items, setItems] = useState<ReviewQueueItem[]>([]);
  const [stats, setStats] = useState<ReviewQueueStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [itemsData, statsData] = await Promise.all([
        fetchApi<ReviewQueueItem[]>(endpoints.admin.guardian.reviewQueue),
        fetchApi<ReviewQueueStats>(endpoints.admin.guardian.reviewQueueStats),
      ]);
      setItems(itemsData);
      setStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar fila de revisão');
    } finally {
      setLoading(false);
    }
  }, []);

  return { items, stats, loading, error, load };
}

interface UseGuardianPoliciesReturn {
  policies: GuardianPolicy[];
  loading: boolean;
  error: string | null;
  load: () => Promise<void>;
}

export function useGuardianPolicies(): UseGuardianPoliciesReturn {
  const [policies, setPolicies] = useState<GuardianPolicy[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchApi<GuardianPolicy[]>(endpoints.admin.guardian.policies);
      setPolicies(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar políticas');
    } finally {
      setLoading(false);
    }
  }, []);

  return { policies, loading, error, load };
}
