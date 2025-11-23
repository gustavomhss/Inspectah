import { useCallback, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminCaseXRay } from '../../../core/api/api-types';
import { getAdminCaseXRay } from '../../admin/api';

export function useCaseXray(caseId?: string) {
  const { token } = useAuth();
  const { logEvent, logError } = useLogger();
  const [xray, setXray] = useState<AdminCaseXRay | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    logEvent('cases.xray_load', { caseId });
    try {
      const data = await getAdminCaseXRay(caseId, token || undefined);
      setXray(data);
      logEvent('cases.xray_success', { caseId });
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('cases.xray_error', { caseId, message });
      logError(err, { scope: 'cases', type: 'xray', caseId });
    } finally {
      setLoading(false);
    }
  }, [caseId, logError, logEvent, token]);

  return { xray, load, loading, error };
}
