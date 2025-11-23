export type TruthState =
  | 'ACCEPTED'
  | 'DISPUTED'
  | 'UNDER_REVIEW'
  | 'INSUFFICIENT_EVIDENCE'
  | 'AT_RISK'
  | 'UNKNOWN';

export const truthStateMeta: Record<
  TruthState,
  {
    label: string;
    tone: 'success' | 'warning' | 'danger' | 'info';
    description: string;
  }
> = {
  ACCEPTED: {
    label: 'Aceito/estabilizado',
    tone: 'success',
    description: 'Estado consolidado com evidência suficiente.',
  },
  AT_RISK: {
    label: 'Em atenção/risco',
    tone: 'warning',
    description: 'Há sinais de risco ou degradação que precisam de acompanhamento.',
  },
  DISPUTED: {
    label: 'Em disputa',
    tone: 'warning',
    description: 'Informação contestada ou com versões conflitantes.',
  },
  UNDER_REVIEW: {
    label: 'Em análise',
    tone: 'info',
    description: 'Em processamento ou aguardando evidências adicionais.',
  },
  INSUFFICIENT_EVIDENCE: {
    label: 'Evidência insuficiente',
    tone: 'warning',
    description: 'Faltam dados para afirmar com confiança.',
  },
  UNKNOWN: {
    label: 'Estado desconhecido',
    tone: 'danger',
    description: 'Não foi possível inferir o estado de verdade.',
  },
};
