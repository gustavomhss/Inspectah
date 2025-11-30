import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { renderWithProviders } from '../../../__tests__/test-utils';
import { server } from '../../../__tests__/mocks/server';
import SourcesListPage from '../pages/SourcesListPage';
import SourceEditPage from '../pages/SourceEditPage';

const BASE_URL = 'http://localhost:8000';

const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  vi.spyOn(console, 'error').mockImplementation((...args: unknown[]) => {
    const message = args[0];
    if (typeof message === 'string' && message.includes('not wrapped in act')) {
      return;
    }
    // @ts-expect-error mock
    originalError(...args);
  });

  vi.spyOn(console, 'warn').mockImplementation((...args: unknown[]) => {
    const message = args[0];
    if (typeof message === 'string' && message.includes('React Router Future Flag Warning')) {
      return;
    }
    // @ts-expect-error mock
    originalWarn(...args);
  });
});

afterAll(() => {
  (console.error as unknown as { mockRestore: () => void }).mockRestore();
  (console.warn as unknown as { mockRestore: () => void }).mockRestore();
});

const buildSource = (overrides: Record<string, unknown> = {}) => ({
  id: 'src-1',
  name: 'Fonte A',
  type: 'news_rss',
  category: 'gov',
  state: 'PROPOSED',
  description: '',
  endpoint: 'https://api.fonte-a',
  ...overrides,
});

describe('Console de Fontes v2', () => {
  it('renderiza lista de fontes e aplica filtro', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/sources`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            sources: [
              buildSource({ id: 'src-1', name: 'Fonte A', category: 'gov', state: 'ACTIVE' }),
              buildSource({ id: 'src-2', name: 'Fonte B', category: 'finance', state: 'PROPOSED' }),
            ],
          }),
        ),
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/sources" element={<SourcesListPage />} />
      </Routes>,
      { route: '/admin/sources' },
    );

    await screen.findByText('Fonte A');

    const searchInput = screen.getByPlaceholderText(/Filtrar por nome, tipo ou categoria/i);
    await userEvent.clear(searchInput);
    await userEvent.type(searchInput, 'finance');

    expect(screen.queryByText('Fonte A')).not.toBeInTheDocument();
    expect(screen.getByText('Fonte B')).toBeInTheDocument();
  });

  it('cria fonte nova e exibe mensagem de sucesso', async () => {
    server.use(
      rest.post(`${BASE_URL}/admin/sources`, async (req, res, ctx) => {
        const body = await req.json();
        return res(ctx.status(201), ctx.json({ source: { ...body, id: 'src-99', state: body.state || 'PROPOSED' } }));
      }),
      rest.get(`${BASE_URL}/admin/sources/src-99`, (_req, res, ctx) => res(ctx.status(200), ctx.json({ source: buildSource({ id: 'src-99' }) }))),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/sources/new" element={<SourceEditPage />} />
        <Route path="/admin/sources/:sourceId" element={<SourceEditPage />} />
      </Routes>,
      { route: '/admin/sources/new' },
    );

    await userEvent.type(screen.getByLabelText(/Nome da fonte/i), 'Fonte Nova');
    await userEvent.type(screen.getByLabelText(/Slug/i), 'fonte-nova');
    await userEvent.type(screen.getByLabelText(/Categoria/i), 'gov');
    await userEvent.type(screen.getByLabelText(/Endpoint/i), 'https://nova');

    await userEvent.click(screen.getByRole('button', { name: /Salvar/i }));

    await screen.findByText(/Fonte criada com sucesso/i);
  });

  it('altera o estado de uma fonte existente', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/sources/src-1`, (_req, res, ctx) => res(ctx.status(200), ctx.json({ source: buildSource() }))),
      rest.post(`${BASE_URL}/admin/sources/src-1/status`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json({ source: buildSource({ state: 'ACTIVE' }) })),
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/sources/:sourceId" element={<SourceEditPage />} />
      </Routes>,
      { route: '/admin/sources/src-1' },
    );

    await screen.findByText(/Proposta/i);

    await userEvent.click(screen.getByRole('button', { name: /Ativar/i }));

    await screen.findByText(/Ativa/i);
  });

  it('mostra erro quando atualização falha', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/sources/src-err`, (_req, res, ctx) => res(ctx.status(200), ctx.json({ source: buildSource({ id: 'src-err' }) }))),
      rest.post(`${BASE_URL}/admin/sources/src-err/status`, (_req, res, ctx) =>
        res(ctx.status(500), ctx.json({ detail: 'Falha de backend' })),
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/sources/:sourceId" element={<SourceEditPage />} />
      </Routes>,
      { route: '/admin/sources/src-err' },
    );

    await screen.findByText(/Proposta/i);

    await userEvent.click(screen.getByRole('button', { name: /Ativar/i }));

    await screen.findByText(/Falha de backend/i);
  });
});
