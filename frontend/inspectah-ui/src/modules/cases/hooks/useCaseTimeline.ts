import { useCallback, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminTimelineResponse } from '../../../core/api/api-types';
import { getAdminCaseTimeline } from '../../admin/api';

export function useCaseTimeline(caseId?: string) {
  const { token } = useAuth();
  const { logEvent, logError } = useLogger();
  const [timeline, setTimeline] = useState<AdminTimelineResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    logEvent('cases.timeline_load', { caseId });
    try {
      const data = await getAdminCaseTimeline(caseId, token || undefined);
      setTimeline(data);
      logEvent('cases.timeline_success', { caseId, eventsCount: data.events?.length || 0 });
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('cases.timeline_error', { caseId, message });
      logError(err, { scope: 'cases', type: 'timeline', caseId });
    } finally {
      setLoading(false);
    }
  }, [caseId, logError, logEvent, token]);

  return { timeline, load, loading, error };
}
