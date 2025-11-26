import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AgentCommittee, AgentLayer, AgentRun } from '../../../core/api/api-types';
import { createCommittee, listCommitteeRuns, listCommittees, triggerDryRun, updateCommittee } from '../api/agentsApi';

export function useCommittees(layer?: AgentLayer) {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [committees, setCommittees] = useState<AgentCommittee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listCommittees(token || undefined, layer);
      setCommittees(data);
      logEvent('admin.committees_loaded', { count: data.length, layer });
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('admin.action_error', { page: 'committees', message });
    } finally {
      setLoading(false);
    }
  }, [token, logEvent, layer]);

  useEffect(() => {
    void load();
  }, [load]);

  const create = useCallback(
    async (payload: Parameters<typeof createCommittee>[0]) => {
      const created = await createCommittee(payload, token || undefined);
      setCommittees((prev) => [...prev, created]);
      logEvent('admin.committees_config_saved', { id: created.id, layer: created.layer });
      return created;
    },
    [token, logEvent],
  );

  const update = useCallback(
    async (committeeId: string, payload: Parameters<typeof updateCommittee>[1]) => {
      const updated = await updateCommittee(committeeId, payload, token || undefined);
      setCommittees((prev) => prev.map((c) => (c.id === committeeId ? updated : c)));
      logEvent('admin.committees_config_saved', { id: committeeId, layer: updated.layer });
      return updated;
    },
    [token, logEvent],
  );

  const fetchRuns = useCallback(
    async (committeeId: string): Promise<AgentRun[]> => {
      return listCommitteeRuns(committeeId, token || undefined);
    },
    [token],
  );

  const dryRun = useCallback(
    async (committeeId: string, payload: { input_ref: string | null; data: Record<string, unknown> }) => {
      return triggerDryRun(committeeId, payload.input_ref, payload.data, token || undefined);
    },
    [token],
  );

  return { committees, loading, error, reload: load, createCommittee: create, updateCommittee: update, fetchRuns, dryRun };
}
