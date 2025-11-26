import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AgentProfile, AgentStatus, AgentLayer, AgentRole } from '../../../core/api/api-types';
import { createAgent, listAgents } from '../api/agentsApi';

interface Filters {
  layer?: AgentLayer;
  role?: AgentRole;
  status?: AgentStatus;
}

export function useAgents(filters: Filters = {}) {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [agents, setAgents] = useState<AgentProfile[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAgents(token || undefined, filters);
      setAgents(data);
      logEvent('admin.agents_list_open', {
        count: data.length,
        layer: filters.layer,
        role: filters.role,
        status: filters.status,
      });
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('admin.action_error', { page: 'agents', message });
    } finally {
      setLoading(false);
    }
  }, [token, logEvent, filters]);

  useEffect(() => {
    void load();
  }, [load]);

  const create = useCallback(
    async (payload: Parameters<typeof createAgent>[0]) => {
      const created = await createAgent(payload, token || undefined);
      setAgents((prev) => [...prev, created]);
      logEvent('admin.agent_created', { id: created.id, layer: created.layer, role: created.role });
      return created;
    },
    [token, logEvent],
  );

  return { agents, loading, error, reload: load, createAgent: create };
}
