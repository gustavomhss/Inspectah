/**
 * DecisionStatusBadge — S37
 *
 * Badge component for Guardian decision status
 */

import type { DecisionStatus } from '../types';

interface DecisionStatusBadgeProps {
  status: DecisionStatus | string;
  size?: 'sm' | 'md';
}

const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  pending: { label: 'Pendente', color: 'text-slate-200', bg: 'bg-slate-600' },
  validating: { label: 'Validando', color: 'text-blue-200', bg: 'bg-blue-600' },
  awaiting_review: { label: 'Aguardando Revisão', color: 'text-amber-200', bg: 'bg-amber-600' },
  awaiting_quorum: { label: 'Aguardando Quórum', color: 'text-purple-200', bg: 'bg-purple-600' },
  approved: { label: 'Aprovado', color: 'text-green-200', bg: 'bg-green-600' },
  rejected: { label: 'Rejeitado', color: 'text-red-200', bg: 'bg-red-600' },
  escalated: { label: 'Escalado', color: 'text-orange-200', bg: 'bg-orange-600' },
  timed_out: { label: 'Timeout', color: 'text-gray-200', bg: 'bg-gray-600' },
  cancelled: { label: 'Cancelado', color: 'text-gray-300', bg: 'bg-gray-700' },
};

function DecisionStatusBadge({ status, size = 'sm' }: DecisionStatusBadgeProps) {
  const config = STATUS_CONFIG[status] || {
    label: status,
    color: 'text-slate-200',
    bg: 'bg-slate-600',
  };

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${config.bg} ${config.color} ${sizeClasses}`}
    >
      {config.label}
    </span>
  );
}

export default DecisionStatusBadge;
