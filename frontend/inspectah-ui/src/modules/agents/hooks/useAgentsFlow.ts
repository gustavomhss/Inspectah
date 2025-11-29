import { useCallback, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AgentFlowLayer, AgentRole, FlowLayerType } from '../../../core/api/api-types';
import { getAgentsFlow, saveAgentsFlow } from '../api/agentsApi';

export interface EditableLayer extends Omit<AgentFlowLayer, 'created_at' | 'updated_at'> {
  created_at?: string;
  updated_at?: string;
}

export function useAgentsFlow() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [layers, setLayers] = useState<EditableLayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAgentsFlow(token || undefined);
      const normalized = normalizeFlow(data);
      setLayers(normalized);
      logEvent('admin.agents_flow_loaded', { count: normalized.length });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [token, logEvent]);

  useEffect(() => {
    void load();
  }, [load]);

  const addIntermediateLayer = useCallback(() => {
    const nextIndex = layers.length + 1;
    const insertPos = layers.findIndex((l) => l.layer_type === 'decision_maker_layer');
    const newLayer: EditableLayer = {
      id: `layer_new_${Date.now()}`,
      name: `Camada intermediária`,
      description: '',
      layer_type: 'intermediate_layer',
      layer_index: nextIndex,
      agent_ids: [],
      mediator_agent_id: '',
    };
    const updated = [...layers];
    if (insertPos >= 0) {
      updated.splice(insertPos, 0, newLayer);
    } else {
      updated.push(newLayer);
    }
    setLayers(reindex(updated));
  }, [layers]);

  const removeLayer = useCallback(
    (layerId: string) => {
      const layer = layers.find((l) => l.id === layerId);
      if (!layer || layer.layer_type !== 'intermediate_layer') return;
      const updated = layers.filter((l) => l.id !== layerId);
      setLayers(reindex(updated));
    },
    [layers],
  );

  const updateLayerAgents = useCallback(
    (layerId: string, agentIds: string[]) => {
      setLayers((prev) =>
        prev.map((l) => (l.id === layerId ? { ...l, agent_ids: agentIds, mediator_agent_id: agentIds[0] || '' } : l)),
      );
    },
    [],
  );

  const setMediator = useCallback((layerId: string, agentId: string) => {
    setLayers((prev) => prev.map((l) => (l.id === layerId ? { ...l, mediator_agent_id: agentId } : l)));
  }, []);

  const validate = useCallback(
    (state: EditableLayer[]) => {
      const errors: string[] = [];
      if (state.length < 4) errors.push('Fluxo precisa de ao menos 4 camadas.');
      // fixed positions
      const first = state[0]?.layer_type;
      const second = state[1]?.layer_type;
      const last = state[state.length - 1]?.layer_type;
      const penultimate = state[state.length - 2]?.layer_type;
      if (first !== 'interpretation_layer') errors.push('Primeira camada deve ser Interpretação.');
      if (second !== 'classification_layer') errors.push('Segunda camada deve ser Classificação.');
      if (penultimate !== 'decision_maker_layer') errors.push('Penúltima camada deve ser Decision Maker.');
      if (last !== 'librarian_layer') errors.push('Última camada deve ser Librarian.');

      state.forEach((layer) => {
        if (layer.agent_ids.length < 3 || layer.agent_ids.length > 5) {
          errors.push(`Camada ${layer.name} deve ter entre 3 e 5 agentes.`);
        }
        if (!layer.mediator_agent_id || !layer.agent_ids.includes(layer.mediator_agent_id)) {
          errors.push(`Camada ${layer.name} precisa de um mediador dentre os agentes selecionados.`);
        }
      });
      setValidationErrors(errors);
      return errors.length === 0;
    },
    [setValidationErrors],
  );

  const save = useCallback(async () => {
    if (!validate(layers)) {
      return false;
    }
    setSaving(true);
    try {
      const payload = reindex(layers);
      await saveAgentsFlow(payload, token || undefined);
      logEvent('admin.agents_flow_saved', { layers: payload.length });
      setLayers(payload);
      return true;
    } catch (err) {
      setError((err as Error).message);
      return false;
    } finally {
      setSaving(false);
    }
  }, [layers, token, logEvent, validate]);

  const allowedRolesForLayer = useCallback((layerType: FlowLayerType): AgentRole[] => {
    switch (layerType) {
      case 'interpretation_layer':
        return ['interpreter'];
      case 'classification_layer':
        return ['classifier'];
      case 'decision_maker_layer':
        return ['decision_maker'];
      case 'librarian_layer':
        return ['librarian'];
      default:
        return ['interpreter', 'classifier', 'analyst', 'debunker'];
    }
  }, []);

  const value = useMemo(
    () => ({
      layers,
      loading,
      error,
      saving,
      validationErrors,
      reload: load,
      addIntermediateLayer,
      removeLayer,
      updateLayerAgents,
      setMediator,
      save,
      allowedRolesForLayer,
    }),
    [layers, loading, error, saving, validationErrors, load, addIntermediateLayer, removeLayer, updateLayerAgents, setMediator, save, allowedRolesForLayer],
  );

  return value;
}

function normalizeFlow(data: unknown): EditableLayer[] {
  const arrayData = Array.isArray(data) ? data : [];
  const safeLayers: EditableLayer[] = arrayData.map((raw, idx) => {
    const item = (raw || {}) as Record<string, unknown>;
    const layerType = isValidLayerType(item.layer_type) ? item.layer_type : 'intermediate_layer';
    const agentIds = Array.isArray(item.agent_ids) ? item.agent_ids.map(String) : [];
    const mediator = typeof item.mediator_agent_id === 'string' ? item.mediator_agent_id : '';
    const description = typeof item.description === 'string' ? item.description : '';
    const name = typeof item.name === 'string' ? item.name : `Camada ${idx + 1}`;
    const id = typeof item.id === 'string' ? item.id : `layer_${idx + 1}`;
    const layerIndex = typeof item.layer_index === 'number' ? item.layer_index : idx + 1;
    const createdAt = typeof item.created_at === 'string' ? item.created_at : undefined;
    const updatedAt = typeof item.updated_at === 'string' ? item.updated_at : undefined;

    return {
      id,
      name,
      description,
      layer_type: layerType,
      layer_index: layerIndex,
      agent_ids: agentIds,
      mediator_agent_id: mediator,
      created_at: createdAt,
      updated_at: updatedAt,
    };
  });

  const base = ensureFixedLayers(safeLayers);
  return reindex(base);
}

function ensureFixedLayers(layers: EditableLayer[]): EditableLayer[] {
  const findLayerByType = (type: FlowLayerType) => layers.find((l) => l.layer_type === type);

  const interpretation = findLayerByType('interpretation_layer') || buildDefaultLayer('interpretation_layer', 1);
  const classification = findLayerByType('classification_layer') || buildDefaultLayer('classification_layer', 2);
  const decision = findLayerByType('decision_maker_layer') || buildDefaultLayer('decision_maker_layer', layers.length + 1);
  const librarian = findLayerByType('librarian_layer') || buildDefaultLayer('librarian_layer', layers.length + 2);

  const intermediates = layers.filter((l) => l.layer_type === 'intermediate_layer');
  return [interpretation, classification, ...intermediates, decision, librarian];
}

function buildDefaultLayer(layerType: FlowLayerType, idx: number): EditableLayer {
  const names: Record<FlowLayerType, string> = {
    interpretation_layer: 'Interpretação',
    classification_layer: 'Classificação',
    decision_maker_layer: 'Decision Maker',
    librarian_layer: 'Librarian',
  };
  return {
    id: `layer_${layerType}_${idx}`,
    name: names[layerType] || `Camada ${idx}`,
    description: '',
    layer_type: layerType,
    layer_index: idx,
    agent_ids: [],
    mediator_agent_id: '',
  };
}

function isValidLayerType(value: unknown): value is FlowLayerType | 'intermediate_layer' {
  return (
    value === 'interpretation_layer' ||
    value === 'classification_layer' ||
    value === 'decision_maker_layer' ||
    value === 'librarian_layer' ||
    value === 'intermediate_layer'
  );
}

function reindex(layers: EditableLayer[]): EditableLayer[] {
  return layers
    .map((l, idx) => ({
      ...l,
      layer_index: idx + 1,
    }))
    .sort((a, b) => a.layer_index - b.layer_index);
}
