/**
 * S38-FE-010e: Hook useSourceDryRun
 */

import { useCallback, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import type { DryRunResult } from '../types';
import * as api from '../api/sourcesApi';

interface UseSourceDryRunReturn {
  result: DryRunResult | null;
  loading: boolean;
  error: string | null;
  execute: (sourceId: string, options?: { url?: string; limit?: number }) => Promise<DryRunResult | null>;
  reset: () => void;
}

export function useSourceDryRun(): UseSourceDryRunReturn {
  const { token } = useAuth();
  const [result, setResult] = useState<DryRunResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (sourceId: string, options?: { url?: string; limit?: number }) => {
      setLoading(true);
      setError(null);
      setResult(null);

      try {
        const dryRunResult = await api.dryRunSource(sourceId, options, token || undefined);
        setResult(dryRunResult);
        return dryRunResult;
      } catch (err) {
        const message = (err as Error).message;
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setLoading(false);
  }, []);

  return { result, loading, error, execute, reset };
}
