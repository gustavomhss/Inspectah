import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { ModelUpgradePolicy } from '../../../core/api/api-types';
import { getModelPolicy, updateModelPolicy } from '../api/agentsApi';

export function useModelPolicy() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [policy, setPolicy] = useState<ModelUpgradePolicy | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getModelPolicy(token || undefined);
      setPolicy(data);
      logEvent('admin.model_policy_loaded', { auto: data.auto_upgrade_enabled });
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('admin.action_error', { page: 'model_policy', message });
    } finally {
      setLoading(false);
    }
  }, [token, logEvent]);

  useEffect(() => {
    void load();
  }, [load]);

  const save = useCallback(
    async (updates: Partial<ModelUpgradePolicy>) => {
      const next = await updateModelPolicy(updates, token || undefined);
      setPolicy(next);
      logEvent('admin.model_policy_updated', { auto: next.auto_upgrade_enabled, delay: next.adoption_delay_days });
      return next;
    },
    [token, logEvent],
  );

  return { policy, loading, error, reload: load, save };
}
