import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '@/app/providers/AuthProvider';
import { useLogger } from '@/app/providers/LoggerProvider';
import {
  createAgentFlow,
  deleteAgentFlow,
  getAgentFlowByDomain,
  listAgentFlows,
  updateAgentFlow,
} from './agentFlowsApi';
import type { AgentFlowConfig, AgentFlowConfigForm } from './agentFlowsTypes';

export function useAgentFlowsList() {
  const { token } = useAuth();
  const [items, setItems] = useState<AgentFlowConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAgentFlows(token || undefined);
      setItems(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { items, loading, error, reload };
}

export function useAgentFlowByDomain(domainKey: string | null) {
  const { token } = useAuth();
  const [flow, setFlow] = useState<AgentFlowConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!domainKey) return;
    setLoading(true);
    setError(null);
    getAgentFlowByDomain(domainKey, token || undefined)
      .then((data) => setFlow(data))
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, [domainKey, token]);

  return { flow, loading, error, setFlow };
}

export function useSaveAgentFlow(onSaved?: (flow: AgentFlowConfig) => void) {
  const { token, user } = useAuth();
  const { logEvent } = useLogger();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const save = useCallback(
    async (form: AgentFlowConfigForm) => {
      setSaving(true);
      setError(null);
      const payload = {
        ...form,
        created_by: form.created_by || user?.id || user?.email || 'admin-ui',
        updated_by: user?.id || user?.email || 'admin-ui',
      };
      try {
        const result = form.id
          ? await updateAgentFlow(form.id, payload, token || undefined)
          : await createAgentFlow(payload, token || undefined);
        logEvent('admin.agent_flows.saved', { domain: result.domain_key });
        onSaved?.(result);
        return result;
      } catch (err) {
        setError((err as Error).message);
        throw err;
      } finally {
        setSaving(false);
      }
    },
    [token, user, logEvent, onSaved],
  );

  const remove = useCallback(
    async (flowId: string) => {
      setSaving(true);
      try {
        await deleteAgentFlow(flowId, token || undefined);
        logEvent('admin.agent_flows.deleted', { flow_id: flowId });
      } finally {
        setSaving(false);
      }
    },
    [token, logEvent],
  );

  return { save, remove, saving, error, setError };
}
