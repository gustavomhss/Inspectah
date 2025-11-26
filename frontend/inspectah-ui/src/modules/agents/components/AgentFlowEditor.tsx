import type { AgentProfile } from '../../../core/api/api-types';
import { AgentFlowLayerCard } from './AgentFlowLayerCard';
import type { EditableLayer } from '../hooks/useAgentsFlow';

interface Props {
  layers: EditableLayer[];
  agents: AgentProfile[];
  validationErrors: string[];
  onAddIntermediate: () => void;
  onRemove: (layerId: string) => void;
  onChangeAgents: (layerId: string, agentIds: string[]) => void;
  onSetMediator: (layerId: string, agentId: string) => void;
  onSave: () => Promise<boolean>;
  allowedRolesForLayer: (layerType: EditableLayer['layer_type']) => AgentProfile['role'][];
  saving: boolean;
}

export function AgentFlowEditor({
  layers,
  agents,
  validationErrors,
  onAddIntermediate,
  onRemove,
  onChangeAgents,
  onSetMediator,
  onSave,
  allowedRolesForLayer,
  saving,
}: Props) {
  return (
    <div className="space-y-4">
      {validationErrors.length > 0 && (
        <div className="rounded-lg border border-amber-400/40 bg-amber-500/10 p-3 text-sm text-amber-100">
          <p className="font-semibold">Ajustes necessários:</p>
          <ul className="list-disc pl-4">
            {validationErrors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="space-y-3">
        {layers.map((layer) => (
          <AgentFlowLayerCard
            key={layer.id}
            layer={layer as any}
            agents={agents}
            allowedRoles={allowedRolesForLayer(layer.layer_type)}
            onChangeAgents={(ids) => onChangeAgents(layer.id, ids)}
            onSelectMediator={(id) => onSetMediator(layer.id, id)}
            canRemove={layer.layer_type === 'intermediate_layer'}
            onRemove={() => onRemove(layer.id)}
            isFixed={layer.layer_type !== 'intermediate_layer'}
          />
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={onAddIntermediate}
          className="rounded-md bg-white/10 px-3 py-2 text-sm font-semibold text-white hover:bg-white/20"
        >
          Adicionar camada intermediária
        </button>
        <button
          type="button"
          onClick={() => {
            void onSave();
          }}
          className="rounded-md bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-400 disabled:opacity-60"
          disabled={saving}
        >
          {saving ? 'Salvando...' : 'Salvar fluxo'}
        </button>
      </div>
    </div>
  );
}

export default AgentFlowEditor;
