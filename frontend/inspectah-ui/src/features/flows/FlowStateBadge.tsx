import type { FlowState } from './types';

const styles: Record<FlowState, string> = {
  draft: 'bg-gray-200 text-gray-800',
  em_teste: 'bg-yellow-100 text-yellow-800',
  ativo: 'bg-green-100 text-green-800',
  pausado: 'bg-orange-100 text-orange-800',
  deprecado: 'bg-slate-200 text-slate-700',
};

const labels: Record<FlowState, string> = {
  draft: 'Rascunho',
  em_teste: 'Em teste',
  ativo: 'Ativo',
  pausado: 'Pausado',
  deprecado: 'Deprecado',
};

export function FlowStateBadge({ state }: { state: FlowState }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${styles[state]}`}>
      {labels[state]}
    </span>
  );
}

export default FlowStateBadge;
