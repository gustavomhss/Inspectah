import { Route, Routes } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { screen } from '@testing-library/react';
import { vi } from 'vitest';
import { useState } from 'react';
import AgentsFlowPage from '../../modules/agents/pages/AgentsFlowPage';
import { renderWithProviders } from '../test-utils';
import type { AgentProfile, FlowLayerType } from '../../core/api/api-types';

const agentsMock = [
  { id: 'i1', name: 'Interp 1', role: 'interpreter', layer: 'interpretation' },
  { id: 'i2', name: 'Interp 2', role: 'interpreter', layer: 'interpretation' },
  { id: 'i3', name: 'Interp 3', role: 'interpreter', layer: 'interpretation' },
  { id: 'c1', name: 'Classifier 1', role: 'classifier', layer: 'classification' },
  { id: 'c2', name: 'Classifier 2', role: 'classifier', layer: 'classification' },
  { id: 'c3', name: 'Classifier 3', role: 'classifier', layer: 'classification' },
  { id: 'd1', name: 'Debunker 1', role: 'debunker', layer: 'interpretation' },
  { id: 'd2', name: 'Debunker 2', role: 'debunker', layer: 'interpretation' },
  { id: 'd3', name: 'Debunker 3', role: 'debunker', layer: 'interpretation' },
  { id: 'dm', name: 'Decision', role: 'decision_maker', layer: 'classification' },
  { id: 'lb', name: 'Librarian', role: 'librarian', layer: 'classification' },
];

const flowMock = [
  {
    id: 'l1',
    name: 'Interpretação',
    description: '',
    layer_type: 'interpretation_layer',
    layer_index: 1,
    agent_ids: ['i1', 'i2', 'i3'],
    mediator_agent_id: 'i1',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'l2',
    name: 'Classificação',
    description: '',
    layer_type: 'classification_layer',
    layer_index: 2,
    agent_ids: ['c1', 'c2', 'c3'],
    mediator_agent_id: 'c1',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'l4',
    name: 'Decision',
    description: '',
    layer_type: 'decision_maker_layer',
    layer_index: 4,
    agent_ids: ['dm', 'dm', 'dm'],
    mediator_agent_id: 'dm',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'l5',
    name: 'Librarian',
    description: '',
    layer_type: 'librarian_layer',
    layer_index: 5,
    agent_ids: ['lb', 'lb', 'lb'],
    mediator_agent_id: 'lb',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

vi.mock('../../modules/agents/hooks/useAgents', () => ({
  useAgents: () => ({
    agents: agentsMock as AgentProfile[],
    loading: false,
    error: null,
    reload: vi.fn(),
  }),
}));

vi.mock('../../modules/agents/hooks/useAgentsFlow', () => {
  function buildAllowedRoles(layerType: FlowLayerType | 'intermediate_layer') {
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
  }

  return {
    useAgentsFlow: () => {
      const [layers, setLayers] = useState(flowMock);
      const [validationErrors, setValidationErrors] = useState<string[]>([]);
      const [saving, setSaving] = useState(false);

      const reindex = (items: typeof flowMock) =>
        items.map((l, idx) => ({ ...l, layer_index: idx + 1 }));

      const addIntermediateLayer = () => {
        const insertPos = layers.findIndex((l) => l.layer_type === 'decision_maker_layer');
        const updated = [...layers];
        const newLayer = {
          id: `intermediate-${Date.now()}`,
          name: 'Camada intermediária',
          description: '',
          layer_type: 'intermediate_layer',
          layer_index: 0,
          agent_ids: [],
          mediator_agent_id: '',
          created_at: '',
          updated_at: '',
        };
        if (insertPos >= 0) updated.splice(insertPos, 0, newLayer);
        else updated.push(newLayer);
        setLayers(reindex(updated));
      };

      const removeLayer = (layerId: string) => {
        setLayers((prev) => reindex(prev.filter((l) => l.id !== layerId)));
      };

      const updateLayerAgents = (layerId: string, ids: string[]) => {
        setLayers((prev) =>
          prev.map((l) => (l.id === layerId ? { ...l, agent_ids: ids, mediator_agent_id: ids[0] || '' } : l)),
        );
      };

      const setMediator = (layerId: string, agentId: string) => {
        setLayers((prev) => prev.map((l) => (l.id === layerId ? { ...l, mediator_agent_id: agentId } : l)));
      };

      const validate = (state: typeof flowMock) => {
        const errors: string[] = [];
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
      };

      const save = async () => {
        setSaving(true);
        const ok = validate(layers);
        setSaving(false);
        return ok;
      };

      const allowedRolesForLayer = (layerType: FlowLayerType | 'intermediate_layer') => buildAllowedRoles(layerType);

      return {
        layers,
        loading: false,
        error: null,
        reload: vi.fn(),
        addIntermediateLayer,
        removeLayer,
        updateLayerAgents,
        setMediator,
        validationErrors,
        save,
        allowedRolesForLayer,
        saving,
      };
    },
  };
});

describe('AgentsFlowPage', () => {
  it('renderiza camadas fixas e permite adicionar intermediária', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/agents/flow" element={<AgentsFlowPage />} />
      </Routes>,
      { route: '/admin/agents/flow' },
    );

    const addLayerButton = await screen.findByText(/Adicionar camada intermediária/);
    await userEvent.click(addLayerButton);
    // seleciona dois agentes debunker + um classifier para chegar em 3
    const multi = await screen.findAllByRole('listbox');
    await userEvent.selectOptions(multi[2], ['d1', 'd2', 'd3']);
    const radios = screen.getAllByRole('radio');
    await userEvent.click(radios[radios.length - 1]);

    await userEvent.click(screen.getByText(/Salvar fluxo/));
    await screen.findByText(/Salvar fluxo/);
  });

  it('bloqueia salvar se camada tiver menos de 3 agentes', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/agents/flow" element={<AgentsFlowPage />} />
      </Routes>,
      { route: '/admin/agents/flow' },
    );

    await screen.findByText(/Fluxo de agentes/);
    const multi = await screen.findAllByRole('listbox');
    await userEvent.deselectOptions(multi[0], ['i1', 'i2', 'i3']);

    const saveButton = await screen.findByText(/Salvar fluxo/);
    await userEvent.click(saveButton);

    await screen.findByText(/3 a 5 agentes/);
  });
});
