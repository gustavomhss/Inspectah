import { useCallback, useState } from 'react';
import { consultTruth } from '../api/inspectahClient';
import { HttpError } from '../api/httpClient';
import { logConsultationError, logConsultationStarted, logConsultationSuccess } from '../observability/logEvents';
import type { ConsultationStatus } from '../types/inspectah';

function friendlyErrorMessage(error: unknown): string {
  if (error instanceof HttpError) {
    if (error.status === 400) {
      return 'Não entendi a pergunta. Tente ser direto sobre o fato ou evento que deseja checar.';
    }
    if (!error.status) {
      return 'Não conseguimos falar com o Inspectah agora. Verifique sua conexão e tente de novo.';
    }
    if (error.status && error.status >= 500) {
      return 'Erro no backend do Inspectah. Tente novamente em instantes.';
    }
    if (error.status === 404) {
      return 'Não encontramos dados suficientes para responder com confiança.';
    }
    return error.message || 'Algo deu errado ao consultar.';
  }
  return 'Não conseguimos falar com o Inspectah agora. Verifique sua conexão e tente de novo.';
}

export function useConsultation() {
  const [status, setStatus] = useState<ConsultationStatus>({ kind: 'idle' });

  const submitQuestion = useCallback(async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed) {
      setStatus({ kind: 'error', message: 'Digite uma pergunta para continuar.' });
      return;
    }

    setStatus({ kind: 'submitting', question: trimmed });
    logConsultationStarted(trimmed.slice(0, 120));

    try {
      const result = await consultTruth({ question: trimmed });
      setStatus({ kind: 'success', question: trimmed, result });
      logConsultationSuccess(result.requestId, result.riskLevel);
    } catch (error) {
      const message = friendlyErrorMessage(error);
      setStatus({ kind: 'error', question: trimmed, message });
      logConsultationError(message);
    }
  }, []);

  return { status, submitQuestion };
}
