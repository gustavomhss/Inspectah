import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminSource } from '../../../core/api/api-types';
import type { IngestionRun, IngestionConfig, IngestionMode } from '../../../core/api/api-types';
import { fetchSources } from '../../admin/api';
import { getRunsBySource, runIngestionNow, toggleIngestionMode } from '../api/ingestionApi';

export type IngestionHealth = 'OK' | 'Falhando' | 'Parada' | 'Em andamento';

export interface IngestionSourceRow {
  source: AdminSource;
  lastRun?: IngestionRun;
  health: IngestionHealth;
  mode: IngestionMode;
}

function deriveHealth(lastRun?: IngestionRun, now: Date = new Date()): IngestionHealth {
  if (!lastRun) return 'Parada';
  if (lastRun.status === 'RUNNING') return 'Em andamento';
  if (lastRun.status === 'FAIL' || lastRun.status === 'PARTIAL_SUCCESS') return 'Falhando';
  if (lastRun.status === 'SUCCESS') {
    const finished = lastRun.finished_at || lastRun.started_at;
    if (finished) {
      const deltaMs = now.getTime() - new Date(finished).getTime();
      if (deltaMs < 24 * 60 * 60 * 1000) return 'OK';
    }
    return 'Parada';
  }
  return 'Parada';
}

export function useIngestionSources() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [rows, setRows] = useState<IngestionSourceRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useMemo(
    () => async () => {
      setLoading(true);
      setError(null);
      try {
        const sources = await fetchSources(token || undefined);
        const runsPromises = sources.map(async (source) => {
          try {
            const resp = await getRunsBySource(source.id, { limit: 1 }, token || undefined);
            const lastRun = resp.runs?.[0];
            const mode = resp.config_mode || source.ingestion_mode || 'MANUAL_ONLY';
            return { source, lastRun, health: deriveHealth(lastRun), mode } as IngestionSourceRow;
          } catch (err) {
            logEvent('admin.ingestion.load_error', { source: source.id, message: (err as Error).message });
            const fallbackMode = source.ingestion_mode || 'MANUAL_ONLY';
            return { source, lastRun: undefined, health: 'Parada', mode: fallbackMode } as IngestionSourceRow;
          }
        });
        const results = await Promise.all(runsPromises);
        setRows(results);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    },
    [token, logEvent],
  );

  useEffect(() => {
    void load();
  }, [load]);

  const runNow = async (sourceId: string) => {
    await runIngestionNow(sourceId, token || undefined);
    await load();
  };

  const changeMode = async (sourceId: string, mode: IngestionConfig['mode']) => {
    await toggleIngestionMode(sourceId, mode, token || undefined);
    await load();
  };

  return { rows, loading, error, reload: load, runNow, changeMode };
}
