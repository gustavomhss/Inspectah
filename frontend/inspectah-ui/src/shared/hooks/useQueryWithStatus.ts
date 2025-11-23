import { useCallback, useEffect, useMemo, useState, type DependencyList } from 'react';
import { useLogger } from '../../app/providers/LoggerProvider';

export type QueryState<T> =
  | { state: 'idle' }
  | { state: 'loading' }
  | { state: 'success'; data: T }
  | { state: 'error'; error: string };

interface QueryEvents {
  start?: string;
  success?: string;
  error?: string;
}

export function useQueryWithStatus<T>(
  queryFn: () => Promise<T>,
  deps: DependencyList = [],
  events: QueryEvents = {},
) {
  const { logEvent, logError } = useLogger();
  const [status, setStatus] = useState<QueryState<T>>({ state: 'idle' });

  const run = useCallback(async () => {
    setStatus({ state: 'loading' });
    if (events.start) logEvent(events.start);
    try {
      const data = await queryFn();
      setStatus({ state: 'success', data });
      if (events.success) logEvent(events.success);
    } catch (err) {
      const message = (err as Error).message || 'Erro ao carregar dados';
      setStatus({ state: 'error', error: message });
      logError(err, { event: events.error || 'query_error' });
    }
  }, [events.error, events.start, events.success, logError, logEvent, queryFn]);

  useEffect(() => {
    void run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  const helpers = useMemo(
    () => ({
      refetch: run,
      isLoading: status.state === 'loading',
      isError: status.state === 'error',
      isSuccess: status.state === 'success',
    }),
    [run, status.state],
  );

  return { status, ...helpers };
}
