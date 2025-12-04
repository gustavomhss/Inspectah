import type { FlowExecutionDetail } from './types';
import { FlowStateBadge } from './FlowStateBadge';

interface Props {
  execution: FlowExecutionDetail | null;
  onClose?: () => void;
}

export function FlowExecutionDetailDrawer({ execution, onClose }: Props) {
  if (!execution) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex justify-end">
      <div className="w-full max-w-xl bg-white h-full overflow-y-auto p-6 shadow-2xl">
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-xs text-slate-500">Execução</p>
            <h3 className="text-lg font-semibold">{execution.id}</h3>
            <p className="text-sm text-slate-600">Item: {execution.item_id}</p>
            <p className="text-sm text-slate-600">Status: {execution.status}</p>
          </div>
          <button className="text-sm text-blue-600" onClick={onClose}>
            Fechar
          </button>
        </div>
        <div className="space-y-3">
          {execution.steps.map((step) => (
            <div key={step.id} className="rounded border border-slate-200 p-3">
              <div className="flex justify-between">
                <div>
                  <p className="text-sm font-semibold">{step.step_id || step.id}</p>
                  <p className="text-xs text-slate-500">Status: {step.status}</p>
                </div>
                <FlowStateBadge state="ativo" />
              </div>
              {step.output_resumo && <p className="text-sm text-slate-700 mt-1">{step.output_resumo}</p>}
              {step.erro_resumo && <p className="text-sm text-red-600 mt-1">{step.erro_resumo}</p>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default FlowExecutionDetailDrawer;
