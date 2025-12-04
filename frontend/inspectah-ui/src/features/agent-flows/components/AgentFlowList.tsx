import type { AgentFlowConfig } from '../agentFlowsTypes';

interface Props {
  flows: AgentFlowConfig[];
  selectedId: string | null;
  onSelect: (flow: AgentFlowConfig) => void;
  onCreateNew: () => void;
}

export default function AgentFlowList({ flows, selectedId, onSelect, onCreateNew }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Domínios</p>
          <h3 className="text-lg font-semibold text-white">Fluxos configurados</h3>
        </div>
        <button
          type="button"
          onClick={onCreateNew}
          className="rounded-full bg-sky-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
        >
          Novo fluxo
        </button>
      </div>
      <div className="divide-y divide-white/5 overflow-hidden rounded-2xl border border-white/10 bg-white/5">
        {flows.length === 0 ? (
          <div className="p-4 text-sm text-slate-200">Nenhum fluxo configurado ainda.</div>
        ) : (
          flows.map((flow) => (
            <button
              key={flow.id}
              type="button"
              onClick={() => onSelect(flow)}
              className={`flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition hover:bg-white/5 ${
                selectedId === flow.id ? 'bg-white/10' : ''
              }`}
            >
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">{flow.domain_key}</span>
                <span className="text-xs text-slate-300">{flow.name || 'Fluxo sem nome'}</span>
                <span className="text-[11px] text-slate-400">
                  {flow.steps.length ? summarizeAgents(flow) : 'Sem etapas vinculadas'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-200">
                <span
                  className={`rounded-full px-2 py-1 ${
                    flow.is_active ? 'bg-emerald-500/20 text-emerald-100' : 'bg-amber-500/20 text-amber-100'
                  }`}
                >
                  {flow.is_active ? 'Ativo' : 'Inativo'}
                </span>
                {flow.updated_at ? <span>Atualizado em {new Date(flow.updated_at).toLocaleDateString()}</span> : null}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

function summarizeAgents(flow: AgentFlowConfig): string {
  const labels = (flow.steps || [])
    .map((s) => {
      const params = s.params || {};
      const agentLabel = (params as Record<string, unknown>).agent_label as string | undefined;
      const agentId = (params as Record<string, unknown>).agent_id as string | undefined;
      const roleLabel = s.agent_role.replace('_', ' ');
      if (agentLabel) return `${roleLabel}: ${agentLabel}`;
      if (agentId) return `${roleLabel}: ${agentId}`;
      return `${roleLabel}: —`;
    })
    .slice(0, 3);
  return labels.length ? labels.join(' · ') : 'Sem agentes vinculados';
}
