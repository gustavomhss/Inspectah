import { truthStateMeta, type TruthState } from '../lib/truth-states';

function normalize(state?: string | null): TruthState {
  const value = (state || '').toUpperCase();
  if (['ACCEPTED', 'STABLE', 'ESTAVEL', 'OK'].includes(value)) return 'ACCEPTED';
  if (value.includes('DISPUT') || value.includes('CONTEST')) return 'DISPUTED';
  if (value.includes('REVIEW') || value.includes('ANALISE') || value.includes('ANÁLISE')) return 'UNDER_REVIEW';
  if (value.includes('INSUF') || value.includes('SEM_EVIDENCIA') || value.includes('NO_EVIDENCE')) return 'INSUFFICIENT_EVIDENCE';
  if (value.includes('ATRASO') || value.includes('RISCO')) return 'AT_RISK';
  return 'UNKNOWN';
}

export function useTruthStateLabel(state?: string | null) {
  const normalized = normalize(state);
  return {
    state: normalized,
    ...truthStateMeta[normalized],
  };
}
