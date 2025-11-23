import { createContext, useContext, useEffect, useMemo, useRef, type ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import { logError as baseLogError, logEvent as baseLogEvent, logNavigation as baseLogNavigation } from '../../core/logging/logger';
import type { Logger } from '../../core/logging/logging-types';

export const LoggerContext = createContext<Logger | undefined>(undefined);

export function LoggerProvider({ children }: { children: ReactNode }) {
  const location = useLocation();
  const prevPath = useRef<string | null>(null);
  const { user } = useAuth();

  const value = useMemo<Logger>(
    () => ({
      logEvent: (name, payload) => baseLogEvent(name, { ...payload, userId: user?.id }),
      logError: (error, context) => baseLogError(error, { ...context, userId: user?.id }),
      logNavigation: (from, to, context) => baseLogNavigation(from, to, { ...context, userId: user?.id }),
    }),
    [user?.id],
  );

  useEffect(() => {
    const current = location.pathname;
    if (prevPath.current && prevPath.current !== current) {
      value.logNavigation(prevPath.current, current);
    }
    prevPath.current = current;
  }, [location.pathname, value]);

  return <LoggerContext.Provider value={value}>{children}</LoggerContext.Provider>;
}

export function useLogger(): Logger {
  const ctx = useContext(LoggerContext);
  if (!ctx) {
    throw new Error('useLogger deve ser usado dentro de LoggerProvider');
  }
  return ctx;
}
