import type { AgentProfile, AgentFlowLayer, AgentRole, FlowLayerType } from '../../../core/api/api-types';

interface Props {
  layer: AgentFlowLayer;
  agents: AgentProfile[];
  allowedRoles: AgentRole[];
  onChangeAgents: (agentIds: string[]) => void;
  onSelectMediator: (agentId: string) => void;
  canRemove?: boolean;
  onRemove?: () => void;
  isFixed?: boolean;
}

const roleLabel: Record<AgentRole, string> = {
  interpreter: 'Interpreter',
  classifier: 'Classifier',
  analyst: 'Analyst',
  debunker: 'Debunker',
  decision_maker: 'Decision Maker',
  librarian: 'Librarian',
};

export function AgentFlowLayerCard({ layer, agents, allowedRoles, onChangeAgents, onSelectMediator, canRemove, onRemove, isFixed }: Props) {
  const selectableAgents = agents.filter((a) => allowedRoles.includes(a.role));
  const selectedAgents = selectableAgents.filter((a) => layer.agent_ids.includes(a.id));
  const warnings: string[] = [];
  if (layer.agent_ids.length < 3 || layer.agent_ids.length > 5) warnings.push('Camada precisa de 3 a 5 agentes.');
  if (!layer.mediator_agent_id || !layer.agent_ids.includes(layer.mediator_agent_id)) warnings.push('Defina um mediador.');

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-300">{layerTitle(layer.layer_type)}</p>
          <h3 className="text-lg font-bold text-white">{layer.name}</h3>
          {layer.description && <p className="text-sm text-slate-300">{layer.description}</p>}
        </div>
        {canRemove && onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="text-xs font-semibold text-rose-200 hover:text-white"
            aria-label="Remover camada intermediária"
          >
            Remover
          </button>
        )}
      </div>

      <div className="mt-3 space-y-2">
        <label className="text-sm text-slate-200">
          Selecione agentes (3–5) — {allowedRoles.length === 1 ? roleLabel[allowedRoles[0]] : 'Misturar roles permitidos'}
          <select
            multiple
            value={layer.agent_ids}
            onChange={(e) => {
              const options = Array.from(e.target.selectedOptions).map((o) => o.value);
              onChangeAgents(options);
            }}
            className="mt-1 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white h-28"
          >
            {selectableAgents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} — {roleLabel[agent.role]}
              </option>
            ))}
          </select>
        </label>

        {selectedAgents.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs uppercase text-slate-400">Mediador</p>
            <div className="space-y-1 rounded-lg border border-white/10 bg-white/5 p-2">
              {selectedAgents.map((agent) => (
                <label key={agent.id} className="flex items-center gap-2 text-sm text-white">
                  <input
                    type="radio"
                    name={`mediator-${layer.id}`}
                    checked={layer.mediator_agent_id === agent.id}
                    onChange={() => onSelectMediator(agent.id)}
                  />
                  <span>{agent.name}</span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>

      {warnings.length > 0 && (
        <ul className="mt-2 space-y-1 text-xs text-amber-200">
          {warnings.map((w) => (
            <li key={w}>• {w}</li>
          ))}
        </ul>
      )}

      {isFixed && <p className="mt-2 text-xs text-slate-400">Camada fixa (não removível).</p>}
    </div>
  );
}

function layerTitle(type: FlowLayerType): string {
  switch (type) {
    case 'interpretation_layer':
      return 'Interpretação (fixa)';
    case 'classification_layer':
      return 'Classificação (fixa)';
    case 'decision_maker_layer':
      return 'Decision Maker (fixa)';
    case 'librarian_layer':
      return 'Librarian (fixa)';
    default:
      return 'Camada intermediária';
  }
}

export default AgentFlowLayerCard;
