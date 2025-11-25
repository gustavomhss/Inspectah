import { useEffect, useMemo, useRef, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { IngestionMode, IngestionRun } from '../../../core/api/api-types';
import { getRun, getRunsBySource } from '../api/ingestionApi';

export function useIngestionRuns(sourceId: string) {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [configMode, setConfigMode] = useState<IngestionMode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useMemo(
    () => async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await getRunsBySource(sourceId, { limit: 20, offset: 0 }, token || undefined);
        const ordered = (resp.runs || []).slice().sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime());
        setRuns(ordered);
        setConfigMode(resp.config_mode ?? null);
      } catch (err) {
        const message = (err as Error).message;
        setError(message);
        logEvent('admin.ingestion.runs_error', { source: sourceId, message });
      } finally {
        setLoading(false);
      }
    },
    [sourceId, token, logEvent],
  );

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const hasRunning = runs.some((run) => run.status === 'RUNNING');
    if (hasRunning && !pollRef.current) {
      pollRef.current = setInterval(() => {
        void load();
      }, 2500);
    }
    if (!hasRunning && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [runs, load]);

  return { runs, configMode, loading, error, reload: load };
}

export function useRunDetail(runId?: string) {
  const { token } = useAuth();
  const [run, setRun] = useState<IngestionRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;
    setLoading(true);
    setError(null);
    getRun(runId, token || undefined)
      .then((resp) => setRun(resp))
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, [runId, token]);

  return { run, loading, error };
}
