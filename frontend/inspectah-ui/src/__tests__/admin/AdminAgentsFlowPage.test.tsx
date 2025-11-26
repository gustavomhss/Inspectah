import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { screen } from '@testing-library/react';
import AgentsFlowPage from '../../modules/agents/pages/AgentsFlowPage';
import { renderWithProviders } from '../test-utils';
import { server } from '../mocks/server';

const BASE_URL = 'http://localhost:8000';

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

describe('AgentsFlowPage', () => {
  it('renderiza camadas fixas e permite adicionar intermediária', async () => {
    const handlers = [
      rest.get(`${BASE_URL}/admin/agents`, (_req, res, ctx) => res(ctx.status(200), ctx.json(agentsMock))),
      rest.get(`${BASE_URL}/admin/agents/flow`, (_req, res, ctx) => res(ctx.status(200), ctx.json(flowMock))),
      rest.put(`${BASE_URL}/admin/agents/flow`, async (req, res, ctx) => {
        const body = await req.json();
        // deve incluir pelo menos uma camada decision e librarian
        return res(ctx.status(200), ctx.json(body.map((l: any, idx: number) => ({ ...l, layer_index: idx + 1 }))));
      }),
    ];
    server.use(...handlers);

    renderWithProviders(
      <Routes>
        <Route path="/admin/agents/flow" element={<AgentsFlowPage />} />
      </Routes>,
      { route: '/admin/agents/flow' },
    );

    await screen.findByText(/Fluxo de agentes/);
    await screen.findByText(/Fluxo de agentes/);

    await userEvent.click(screen.getByText(/Adicionar camada intermediária/));
    // seleciona dois agentes debunker + um classifier para chegar em 3
    const multi = await screen.findAllByRole('listbox');
    await userEvent.selectOptions(multi[2], ['d1', 'd2', 'd3']);
    const radios = screen.getAllByRole('radio');
    await userEvent.click(radios[radios.length - 1]);

    await userEvent.click(screen.getByText(/Salvar fluxo/));
    await screen.findByText(/Salvar fluxo/);
  });

  it('bloqueia salvar se camada tiver menos de 3 agentes', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/agents`, (_req, res, ctx) => res(ctx.status(200), ctx.json(agentsMock))),
      rest.get(`${BASE_URL}/admin/agents/flow`, (_req, res, ctx) => res(ctx.status(200), ctx.json(flowMock))),
    );
    renderWithProviders(
      <Routes>
        <Route path="/admin/agents/flow" element={<AgentsFlowPage />} />
      </Routes>,
      { route: '/admin/agents/flow' },
    );

    await screen.findByText(/Fluxo de agentes/);
    const multi = await screen.findAllByRole('listbox');
    await userEvent.deselectOptions(multi[0], ['i1', 'i2', 'i3']);
    await userEvent.click(screen.getByText(/Salvar fluxo/));
    await screen.findByText(/3 a 5 agentes/);
  });
});
