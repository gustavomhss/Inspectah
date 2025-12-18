/**
 * S38-FE-010: Hook useSources
 */

import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import type { Source, SourceDetail } from '../types';
import * as api from '../api/sourcesApi';

interface UseSourcesOptions {
  autoFetch?: boolean;
  source_type?: string;
  state?: string;
  enabled?: boolean;
  q?: string;
}

interface UseSourcesReturn {
  sources: Source[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useSources(options: UseSourcesOptions = {}): UseSourcesReturn {
  const { token } = useAuth();
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { autoFetch = true, source_type, state, enabled, q } = options;

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.listSources(
        { source_type, state, enabled, q },
        token || undefined
      );
      setSources(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [token, source_type, state, enabled, q]);

  useEffect(() => {
    if (autoFetch) {
      void refresh();
    }
  }, [autoFetch, refresh]);

  return { sources, loading, error, refresh };
}

interface UseSourceDetailReturn {
  source: SourceDetail | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useSourceDetail(sourceId: string | null): UseSourceDetailReturn {
  const { token } = useAuth();
  const [source, setSource] = useState<SourceDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!sourceId) return;

    setLoading(true);
    setError(null);
    try {
      const result = await api.getSource(sourceId, token || undefined);
      setSource(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [sourceId, token]);

  useEffect(() => {
    if (sourceId) {
      void refresh();
    }
  }, [sourceId, refresh]);

  return { source, loading, error, refresh };
}
