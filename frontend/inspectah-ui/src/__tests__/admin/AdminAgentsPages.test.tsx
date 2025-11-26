import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { screen } from '@testing-library/react';
import AgentsListPage from '../../modules/agents/pages/AgentsListPage';
import AgentDetailPage from '../../modules/agents/pages/AgentDetailPage';
import AgentCommitteesPage from '../../modules/agents/pages/AgentCommitteesPage';
import ModelPolicyPage from '../../modules/agents/pages/ModelPolicyPage';
import { renderWithProviders } from '../test-utils';
import { server } from '../mocks/server';

const BASE_URL = 'http://localhost:8000';

describe('Admin Agents Console', () => {
  it('renderiza lista e cria novo agente', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/agents`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json([
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
          ]),
        ),
      ),
      rest.post(`${BASE_URL}/admin/agents`, async (req, res, ctx) => {
        const body = await req.json();
        return res(
          ctx.status(201),
          ctx.json({
            ...body,
            id: 'ag-new',
            created_at: '2024-01-02T00:00:00Z',
            updated_at: '2024-01-02T00:00:00Z',
          }),
        );
      }),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/agents" element={<AgentsListPage />} />
      </Routes>,
      { route: '/admin/agents' },
    );

    await screen.findByText(/Debunker A/);
    await userEvent.type(screen.getByPlaceholderText(/Nome do novo agente/), 'Mediator One');
    await userEvent.click(screen.getByText(/Novo agente/));
    await screen.findByText(/Agente criado com sucesso/);
  });

  it('renderiza detalhe e salva', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/agents/ag-1`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
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
          }),
        ),
      ),
      rest.get(`${BASE_URL}/admin/agents/ag-1/instructions`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json([
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
          ]),
        ),
      ),
      rest.put(`${BASE_URL}/admin/agents/ag-1`, async (req, res, ctx) => {
        const body = await req.json();
        return res(
          ctx.status(200),
          ctx.json({
            ...body,
            id: 'ag-1',
            role: 'interpreter',
            layer: 'interpretation',
            temperature: 0.2,
            max_tokens: 4000,
            top_p: 1,
            status: 'active',
            kb_refs: [],
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-02T00:00:00Z',
          }),
        );
      }),
      rest.post(`${BASE_URL}/admin/agents/ag-1/instructions`, async (_req, res, ctx) =>
        res(
          ctx.status(201),
          ctx.json({
            id: 'ver-2',
            agent_id: 'ag-1',
            version_number: 2,
            instructions: 'nova',
            kb_snapshot: [],
            changelog: 'ajuste',
            created_at: '2024-01-02T00:00:00Z',
            model_name: 'gpt-plus-latest',
            temperature: 0.2,
            max_tokens: 4000,
            top_p: 1,
          }),
        ),
      ),
    );

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
    server.use(
      rest.get(`${BASE_URL}/admin/agents`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json([
            {
              id: 'deb-a',
              name: 'Debunker A',
              description: '',
              instructions: '',
              role: 'debunker',
              layer: 'interpretation',
              model_name: 'gpt',
              recommended_model_name: 'gpt',
              temperature: 0.2,
              max_tokens: 4000,
              top_p: 1,
              status: 'active',
              kb_refs: [],
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
            {
              id: 'deb-b',
              name: 'Debunker B',
              description: '',
              instructions: '',
              role: 'debunker',
              layer: 'interpretation',
              model_name: 'gpt',
              recommended_model_name: 'gpt',
              temperature: 0.2,
              max_tokens: 4000,
              top_p: 1,
              status: 'active',
              kb_refs: [],
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
            {
              id: 'med-1',
              name: 'Mediador',
              description: '',
              instructions: '',
              role: 'debunker',
              layer: 'interpretation',
              model_name: 'gpt',
              recommended_model_name: 'gpt',
              temperature: 0.2,
              max_tokens: 4000,
              top_p: 1,
              status: 'active',
              kb_refs: [],
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
          ]),
        ),
      ),
      rest.get(`${BASE_URL}/admin/agents/committees`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json([
            {
              id: 'com-1',
              name: 'Interp',
              description: '',
              layer: 'interpretation',
              primary_agents: ['deb-a', 'deb-b'],
              mediator_agent: 'med-1',
              policy: { required_agreement_ratio: 0.67, max_disagreement_tolerance: 0.34, resolve_ties_strategy: 'favor_cautious' },
              status: 'active',
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
          ]),
        ),
      ),
      rest.post(`${BASE_URL}/admin/agents/committees`, async (req, res, ctx) => {
        const body = await req.json();
        return res(
          ctx.status(201),
          ctx.json({
            ...body,
            id: 'com-2',
            created_at: '2024-01-02T00:00:00Z',
            updated_at: '2024-01-02T00:00:00Z',
          }),
        );
      }),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/agents/:agentId/committees" element={<AgentCommitteesPage />} />
      </Routes>,
      { route: '/admin/agents/ag-1/committees' },
    );

    await screen.findByText(/Comitês de Agentes/);
    await userEvent.type(screen.getByPlaceholderText(/Nome do comitê/), 'Novo Comitê');
    const selects = screen.getAllByRole('combobox');
    await userEvent.selectOptions(selects[1], 'interpretation');
    await userEvent.selectOptions(selects[2], 'deb-a');
    await userEvent.selectOptions(selects[3], 'deb-b');
    await userEvent.selectOptions(selects[4], 'med-1');
    await userEvent.click(screen.getByText(/Criar comitê/));
    await screen.findByText(/Comitê Novo Comitê criado/);
  });

  it('exibe e atualiza política global de modelos', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/agents/policies/model-upgrades`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            global_default_model: 'gpt-plus-latest',
            auto_upgrade_enabled: true,
            adoption_delay_days: 15,
            allowed_models: [],
            last_upgrade_at: null,
            next_upgrade_at: null,
            updated_at: '2024-01-01T00:00:00Z',
          }),
        ),
      ),
      rest.put(`${BASE_URL}/admin/agents/policies/model-upgrades`, async (req, res, ctx) => {
        const body = await req.json();
        return res(
          ctx.status(200),
          ctx.json({
            global_default_model: 'gpt-plus-latest',
            auto_upgrade_enabled: body.auto_upgrade_enabled ?? true,
            adoption_delay_days: body.adoption_delay_days ?? 15,
            allowed_models: [],
            last_upgrade_at: null,
            next_upgrade_at: null,
            updated_at: '2024-01-02T00:00:00Z',
          }),
        );
      }),
    );

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
