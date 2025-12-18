import { renderWithProviders } from '../../../../__tests__/test-utils';
import { screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import type { AgentFlowLayer, AgentProfile } from '../../../../core/api/api-types';
import { useAgents } from '../useAgents';
import { useAgentsFlow } from '../useAgentsFlow';
import * as agentsApi from '../../api/agentsApi';

const baseAgent: AgentProfile = {
  id: 'agent-1',
  name: 'Agente 1',
  description: '',
  instructions: '',
  role: 'debunker',
  layer: 'interpretation',
  model_name: null,
  recommended_model_name: null,
  temperature: 0.7,
  max_tokens: 1024,
  top_p: 1,
  status: 'active',
  kb_refs: [],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const flowMock: AgentFlowLayer[] = [
  {
    id: 'l1',
    name: 'Interpretação',
    description: '',
    layer_type: 'interpretation_layer',
    layer_index: 1,
    agent_ids: ['agent-1'],
    mediator_agent_id: 'agent-1',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

function AgentsConsumer({ layer }: { layer?: AgentProfile['layer'] }) {
  const { agents, loading } = useAgents(layer ? { layer } : {});
  return <div>{loading ? 'loading' : `agents-${agents.length}`}</div>;
}

function AgentsFlowConsumer() {
  const { layers, loading } = useAgentsFlow();
  return <div>{loading ? 'loading' : `layers-${layers.length}`}</div>;
}

describe('useAgents hooks não disparam loops', () => {
  beforeEach(() => {
    vi.spyOn(agentsApi, 'listAgents').mockResolvedValue([baseAgent]);
    vi.spyOn(agentsApi, 'getAgentsFlow').mockResolvedValue(flowMock);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('faz fetch de agentes uma única vez mesmo com rerender', async () => {
    const { rerender } = renderWithProviders(<AgentsConsumer />);
    await screen.findByText('agents-1');
    expect(agentsApi.listAgents).toHaveBeenCalledTimes(1);

    rerender(<AgentsConsumer />);
    await screen.findByText('agents-1');
    expect(agentsApi.listAgents).toHaveBeenCalledTimes(1);
  });

  it('não refaz fetch ao renderizar com filtros idênticos, mas refaz quando o filtro muda', async () => {
    const { rerender } = renderWithProviders(<AgentsConsumer layer="interpretation" />);
    await screen.findByText('agents-1');
    expect(agentsApi.listAgents).toHaveBeenCalledTimes(1);

    rerender(<AgentsConsumer layer="interpretation" />);
    await screen.findByText('agents-1');
    expect(agentsApi.listAgents).toHaveBeenCalledTimes(1);

    rerender(<AgentsConsumer layer="debunk" />);
    await waitFor(() => expect(agentsApi.listAgents).toHaveBeenCalledTimes(2));
  });

  it('carrega fluxo de agentes apenas uma vez por montagem', async () => {
    const { rerender, unmount } = renderWithProviders(<AgentsFlowConsumer />);
    await screen.findByText('layers-4');
    expect(agentsApi.getAgentsFlow).toHaveBeenCalledTimes(1);

    rerender(<AgentsFlowConsumer />);
    await screen.findByText('layers-4');
    expect(agentsApi.getAgentsFlow).toHaveBeenCalledTimes(1);

    unmount();
  });
});
