import type { RiskLevel } from '../../../core/api/api-types';

interface RiskBadgeProps {
  riskLevel: RiskLevel;
  riskScore?: number;
}

const RISK_COPY: Record<RiskLevel, { label: string; description: string; className: string }> = {
  low: {
    label: 'Risco baixo',
    description: 'Fontes consistentes e confiáveis',
    className: 'border-risk-low/50 bg-risk-low/20 text-risk-low',
  },
  medium: {
    label: 'Risco moderado',
    description: 'Há sinais de cautela ou dados incompletos',
    className: 'border-risk-medium/60 bg-risk-medium/20 text-risk-medium',
  },
  high: {
    label: 'Risco alto',
    description: 'Conflitos claros ou incerteza forte',
    className: 'border-risk-high/60 bg-risk-high/15 text-risk-high',
  },
  unknown: {
    label: 'Risco incerto',
    description: 'Dados insuficientes ou contrato não conclusivo',
    className: 'border-risk-unknown/60 bg-risk-unknown/20 text-risk-unknown',
  },
};

function RiskBadge({ riskLevel, riskScore }: RiskBadgeProps) {
  const copy = RISK_COPY[riskLevel] || RISK_COPY.unknown;
  return (
    <div
      className={`inline-flex min-w-[220px] flex-col gap-1 rounded-xl border px-4 py-3 text-left text-sm font-semibold shadow-card ${copy.className}`}
      role="status"
      aria-label={`Nível de risco: ${copy.label}`}
    >
      <span className="text-base">{copy.label}</span>
      <p className="text-xs font-normal text-white/80">{copy.description}</p>
      {typeof riskScore === 'number' && (
        <span className="text-[11px] font-semibold uppercase tracking-wide text-white/80">Score {riskScore.toFixed(2)}</span>
      )}
    </div>
  );
}

export default RiskBadge;
