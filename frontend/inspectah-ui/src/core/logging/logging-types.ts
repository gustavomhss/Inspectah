export type UiEventName =
  | 'consult.query_submitted'
  | 'consult.query_success'
  | 'consult.query_error'
  | 'admin.page_open'
  | 'admin.action_error'
  | 'cases.timeline_load'
  | 'cases.timeline_success'
  | 'cases.timeline_error'
  | 'cases.xray_load'
  | 'cases.xray_success'
  | 'cases.xray_error'
  | 'navigation'
  | 'ui_error';

export interface LogContext {
  [key: string]: unknown;
}

export interface Logger {
  logEvent: (name: UiEventName | string, payload?: LogContext) => void;
  logError: (error: unknown, context?: LogContext) => void;
  logNavigation: (from: string, to: string, context?: LogContext) => void;
}
