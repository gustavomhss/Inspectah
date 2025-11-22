import type { RiskLevel } from '../types/inspectah';

const sanitize = (text: string) => text.replace(/\s+/g, ' ').trim();

export function logConsultationStarted(questionSnippet: string) {
  console.info('[inspectah-ui] consultation_started', {
    questionSnippet: sanitize(questionSnippet).slice(0, 120),
    timestamp: new Date().toISOString(),
  });
}

export function logConsultationSuccess(requestId?: string, riskLevel?: RiskLevel) {
  console.info('[inspectah-ui] consultation_success', {
    requestId,
    riskLevel,
    timestamp: new Date().toISOString(),
  });
}

export function logConsultationError(message: string) {
  console.warn('[inspectah-ui] consultation_error', {
    message: sanitize(message),
    timestamp: new Date().toISOString(),
  });
}

export function logUiError(error: Error, info?: unknown) {
  const safeInfo = typeof info === 'string' ? info.slice(0, 500) : info;
  console.error('[inspectah-ui] ui_error', {
    name: error.name,
    message: sanitize(error.message),
    info: safeInfo,
    timestamp: new Date().toISOString(),
  });
}
