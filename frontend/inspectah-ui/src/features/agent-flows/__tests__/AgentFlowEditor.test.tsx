import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import AgentFlowEditor from '../components/AgentFlowEditor';
import type { AgentFlowConfigForm } from '../agentFlowsTypes';

vi.mock('@/modules/agents/hooks/useAgents', () => ({
  useAgents: () => ({
    agents: [
      {
        id: 'ag1',
        name: 'Interp One',
        role: 'interpreter',
        layer: 'interpretation',
        description: '',
        instructions: '',
        model_name: null,
        recommended_model_name: null,
        temperature: 0,
        max_tokens: 0,
        top_p: 1,
        status: 'active',
        kb_refs: [],
        created_at: '',
        updated_at: '',
      },
      {
        id: 'ag2',
        name: 'Classifier',
        role: 'classifier',
        layer: 'classification',
        description: '',
        instructions: '',
        model_name: null,
        recommended_model_name: null,
        temperature: 0,
        max_tokens: 0,
        top_p: 1,
        status: 'active',
        kb_refs: [],
        created_at: '',
        updated_at: '',
      },
      {
        id: 'ag3',
        name: 'Decision Maker',
        role: 'decision_maker',
        layer: 'classification',
        description: '',
        instructions: '',
        model_name: null,
        recommended_model_name: null,
        temperature: 0,
        max_tokens: 0,
        top_p: 1,
        status: 'active',
        kb_refs: [],
        created_at: '',
        updated_at: '',
      },
    ],
    loading: false,
    error: null,
    reload: vi.fn(),
  }),
}));

const baseFlow: AgentFlowConfigForm = {
  domain_key: 'news_politics',
  name: 'Fluxo política',
  description: 'Fluxo base',
  is_active: true,
  change_reason: 'seed',
  steps: [
    { position: 1, agent_role: 'interpreter', params: {} },
    { position: 2, agent_role: 'classifier', params: {} },
    { position: 3, agent_role: 'decision_maker', params: { threshold: 0.7 } },
  ],
};

describe('AgentFlowEditor', () => {
  it('renders steps and allows adding a new one', async () => {
    const user = userEvent.setup();
    render(
      <AgentFlowEditor initialFlow={baseFlow} onSave={async () => {}} saving={false} error={null} clearError={() => {}} />,
    );

    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#3')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Adicionar passo/i }));
    expect(screen.getByText('#4')).toBeInTheDocument();
  });

  it('shows backend errors', () => {
    render(
      <AgentFlowEditor
        initialFlow={baseFlow}
        onSave={async () => {}}
        saving={false}
        error="Missing required roles"
        clearError={() => {}}
      />,
    );
    expect(screen.getByText(/Missing required roles/i)).toBeInTheDocument();
  });

  it('blocks save when agentes não estão selecionados', async () => {
    const user = userEvent.setup();
    render(
      <AgentFlowEditor
        initialFlow={baseFlow}
        onSave={async () => {}}
        saving={false}
        error={null}
        clearError={() => {}}
      />,
    );

    await user.click(screen.getByRole('button', { name: /Salvar fluxo/i }));
    expect(screen.getByText(/Selecione um agente real para o passo #1/)).toBeInTheDocument();
  });
});
