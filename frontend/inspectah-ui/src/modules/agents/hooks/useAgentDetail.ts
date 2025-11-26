import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AgentInstructionVersion, AgentProfile } from '../../../core/api/api-types';
import { addInstructionVersion, getAgent, listInstructionVersions, updateAgent } from '../api/agentsApi';

export function useAgentDetail(agentId: string) {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [agent, setAgent] = useState<AgentProfile | null>(null);
  const [versions, setVersions] = useState<AgentInstructionVersion[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [profile, history] = await Promise.all([
        getAgent(agentId, token || undefined),
        listInstructionVersions(agentId, token || undefined),
      ]);
      setAgent(profile);
      setVersions(history);
      logEvent('admin.agent_detail_open', { id: agentId, role: profile.role, layer: profile.layer });
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('admin.action_error', { page: 'agent_detail', message });
    } finally {
      setLoading(false);
    }
  }, [agentId, token, logEvent]);

  useEffect(() => {
    void load();
  }, [load]);

  const saveAgent = useCallback(
    async (updates: Partial<AgentProfile>) => {
      const updated = await updateAgent(agentId, updates, token || undefined);
      setAgent(updated);
      logEvent('admin.agent_saved', { id: updated.id, role: updated.role, layer: updated.layer });
      return updated;
    },
    [agentId, token, logEvent],
  );

  const addVersion = useCallback(
    async (payload: { changelog: string; instructions?: string }) => {
      const version = await addInstructionVersion(agentId, payload, token || undefined);
      setVersions((prev) => [version, ...prev]);
      return version;
    },
    [agentId, token],
  );

  return { agent, versions, loading, error, reload: load, saveAgent, addVersion };
}
