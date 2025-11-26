import { Route, Routes } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { screen } from '@testing-library/react';
import { vi } from 'vitest';
import { useState } from 'react';
import AgentsListPage from '../../modules/agents/pages/AgentsListPage';
import AgentDetailPage from '../../modules/agents/pages/AgentDetailPage';
import AgentCommitteesPage from '../../modules/agents/pages/AgentCommitteesPage';
import ModelPolicyPage from '../../modules/agents/pages/ModelPolicyPage';
import { renderWithProviders } from '../test-utils';
import type { AgentCommittee, AgentInstructionVersion, AgentLayer, AgentProfile, AgentStatus } from '../../core/api/api-types';
import type { AgentKBRef } from '../../core/api/api-types';

type AgentPayload = Partial<AgentProfile> & Pick<AgentProfile, 'name' | 'role' | 'layer'>;
type ModelPolicyState = {
  global_default_model: string;
  auto_upgrade_enabled: boolean;
  adoption_delay_days: number;
  allowed_models: string[];
  last_upgrade_at: string | null;
  next_upgrade_at: string | null;
  updated_at: string;
};

vi.mock('../../modules/agents/hooks/useAgents', () => {
  return {
    useAgents: () => {
      const [agents, setAgents] = useState<AgentProfile[]>([
        {
          id: 'ag-1',
          name: 'Debunker A',
          description: 'cético',
          instructions: '',
          role: 'debunker',
          layer: 'interpretation',
          model_name: 'gpt-plus-latest',
          recommended_model_name: 'gpt-plus-latest',
          temperature: 0.2,
          max_tokens: 4000,
          top_p: 1,
          status: 'active',
          kb_refs: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ]);
      const createAgent = async (payload: AgentPayload) => {
        const created: AgentProfile = {
          ...payload,
          id: 'ag-new',
          description: payload.description || '',
          instructions: payload.instructions || '',
          model_name: payload.model_name ?? 'gpt-plus-latest',
          recommended_model_name: payload.recommended_model_name ?? 'gpt-plus-latest',
          temperature: typeof payload.temperature === 'number' ? payload.temperature : 0.2,
          max_tokens: typeof payload.max_tokens === 'number' ? payload.max_tokens : 4000,
          top_p: typeof payload.top_p === 'number' ? payload.top_p : 1,
          status: (payload.status as AgentStatus) || 'active',
          kb_refs: (payload.kb_refs as AgentKBRef[]) || [],
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
        };
        setAgents((prev) => [...prev, created]);
        return created;
      };
      return { agents, loading: false, error: null, reload: vi.fn(), createAgent };
    },
  };
});

vi.mock('../../modules/agents/hooks/useAgentDetail', () => {
  return {
    useAgentDetail: () => {
      const [agent, setAgent] = useState<AgentProfile>({
        id: 'ag-1',
        name: 'Interpreter',
        description: 'interpreta casos',
        instructions: 'siga fontes',
        role: 'interpreter',
        layer: 'interpretation',
        model_name: 'gpt-plus-latest',
        recommended_model_name: 'gpt-plus-latest',
        temperature: 0.2,
        max_tokens: 4000,
        top_p: 1,
        status: 'active',
        kb_refs: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      });
      const [versions, setVersions] = useState<AgentInstructionVersion[]>([
        {
          id: 'ver-1',
          agent_id: 'ag-1',
          version_number: 1,
          instructions: 'original',
          model_name: 'gpt-plus-latest',
          temperature: 0.2,
          max_tokens: 4000,
          top_p: 1,
          kb_snapshot: [],
          changelog: 'criação',
          created_at: '2024-01-01T00:00:00Z',
          created_by: 'tester',
        },
      ]);
      const saveAgent = async (draft: Partial<AgentProfile>) => {
        const updated = { ...agent, ...draft, updated_at: '2024-01-02T00:00:00Z' };
        setAgent(updated);
        return updated;
      };
      const addVersion = async (payload: Record<string, string>) => {
        const newVersion: AgentInstructionVersion = {
          id: `ver-${versions.length + 1}`,
          agent_id: agent.id,
          version_number: versions.length + 1,
          instructions: payload.instructions || 'nova',
          kb_snapshot: [],
          changelog: payload.changelog || 'ajuste',
          created_at: '2024-01-02T00:00:00Z',
          model_name: agent.model_name,
          temperature: agent.temperature,
          max_tokens: agent.max_tokens,
          top_p: agent.top_p,
        };
        setVersions((prev) => [...prev, newVersion]);
        return newVersion;
      };
      return { agent, versions, loading: false, error: null, reload: vi.fn(), saveAgent, addVersion };
    },
  };
});

vi.mock('../../modules/agents/hooks/useCommittees', () => {
  return {
    useCommittees: () => {
      const [committees, setCommittees] = useState<AgentCommittee[]>([]);
      const createCommittee = async (payload: { name: string; primary_agents: string[]; mediator_agent: string; layer: AgentLayer }) => {
        const created: AgentCommittee = {
          ...payload,
          id: `com-${committees.length + 1}`,
          description: payload.name,
          policy: {
            required_agreement_ratio: 0.67,
            max_disagreement_tolerance: 0.34,
            resolve_ties_strategy: 'favor_cautious',
          },
          status: 'active' as AgentStatus,
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
        };
        setCommittees((prev) => [...prev, created]);
        return created;
      };
      return { committees, loading: false, error: null, reload: vi.fn(), createCommittee };
    },
  };
});

vi.mock('../../modules/agents/hooks/useModelPolicy', () => {
  return {
    useModelPolicy: () => {
      const [policy, setPolicy] = useState<ModelPolicyState>({
        global_default_model: 'gpt-plus-latest',
        auto_upgrade_enabled: true,
        adoption_delay_days: 15,
        allowed_models: [],
        last_upgrade_at: null,
        next_upgrade_at: null,
        updated_at: '2024-01-01T00:00:00Z',
      });
      const savePolicy = async (draft: Partial<ModelPolicyState>) => {
        const updated = { ...policy, ...draft, updated_at: '2024-01-02T00:00:00Z' };
        setPolicy(updated);
        return updated;
      };
      return { policy, loading: false, error: null, reload: vi.fn(), save: savePolicy };
    },
  };
});

describe('Admin Agents Console', () => {
  it('renderiza lista e cria novo agente', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/agents" element={<AgentsListPage />} />
      </Routes>,
      { route: '/admin/agents' },
    );

    await screen.findByText(/Debunker A/);
    const nameInput = await screen.findByPlaceholderText(/Nome do novo agente/);
    await userEvent.type(nameInput, 'Mediator One');
    const newAgentButton = await screen.findByText(/Novo agente/);
    await userEvent.click(newAgentButton);
    await screen.findByText(/Agente criado com sucesso/);
  });

  it('renderiza detalhe e salva', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/agents/:agentId" element={<AgentDetailPage />} />
      </Routes>,
      { route: '/admin/agents/ag-1' },
    );

    await screen.findByText(/Interpreter/);
    await userEvent.type(screen.getByDisplayValue(/interpreta casos/), ' atualizado');
    await userEvent.click(screen.getByText(/Salvar alterações/));
    await screen.findByText(/Agente atualizado/);
    await userEvent.click(screen.getByText(/Registrar nova versão/));
    await screen.findByText(/Versão 2 registrada/);
  });

  it('lista e cria comitê', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/agents/committees" element={<AgentCommitteesPage />} />
      </Routes>,
      { route: '/admin/agents/committees' },
    );

    await screen.findByText(/Comitês de Agentes/);
    await userEvent.type(screen.getByPlaceholderText(/Nome do comitê/), 'Novo Comitê');
    const selects = screen.getAllByRole('combobox');
    await userEvent.selectOptions(selects[1], 'interpretation');
    await userEvent.selectOptions(selects[2], 'ag-1');
    await userEvent.selectOptions(selects[3], 'ag-1');
    await userEvent.selectOptions(selects[4], 'ag-1');
    await userEvent.click(screen.getByText(/Criar comitê/));
    await screen.findByText(/Comitê Novo Comitê criado/);
  });

  it('exibe e atualiza política global de modelos', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/agents/model-policy" element={<ModelPolicyPage />} />
      </Routes>,
      { route: '/admin/agents/model-policy' },
    );

    await screen.findByText(/Política global de modelos/);
    await userEvent.click(screen.getByLabelText(/Ativar auto-upgrade/));
    const bufferInput = screen.getByLabelText(/Buffer/);
    await userEvent.clear(bufferInput);
    await userEvent.type(bufferInput, '10');
    await userEvent.click(screen.getByText(/Salvar política/));
    await screen.findByText(/Política atualizada/);
  });
});
