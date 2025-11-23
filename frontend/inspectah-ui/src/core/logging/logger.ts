import { loggingConfig } from './logging-config';
import type { LogContext, UiEventName } from './logging-types';

const sanitize = (text: string) => text.replace(/\s+/g, ' ').trim();

function withBase(payload?: LogContext) {
  return {
    ...payload,
    timestamp: new Date().toISOString(),
    route: typeof window !== 'undefined' ? window.location.pathname : undefined,
  };
}

function emit(level: 'info' | 'warn' | 'error', name: string, payload?: LogContext) {
  const entry = withBase(payload);
  if (loggingConfig.console) {
    const prefix = `[${loggingConfig.appName}]`;
    // eslint-disable-next-line no-console
    console[level](`${prefix} ${name}`, entry);
  }
}

export function logEvent(name: UiEventName | string, payload?: LogContext) {
  emit('info', name, payload);
}

export function logError(error: unknown, context?: LogContext) {
  if (error instanceof Error) {
    emit('error', 'ui_error', {
      name: error.name,
      message: sanitize(error.message),
      stack: error.stack,
      ...context,
    });
    return;
  }
  emit('error', 'ui_error', { message: sanitize(String(error)), ...context });
}

export function logNavigation(from: string, to: string, context?: LogContext) {
  logEvent('navigation', { from, to, ...context });
}
