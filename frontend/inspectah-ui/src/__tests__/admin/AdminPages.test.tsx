import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import { screen, waitFor } from '@testing-library/react';
import AdminOverviewPage from '../../modules/admin/pages/AdminOverviewPage';
import AdminSourcesPage from '../../modules/admin/pages/AdminSourcesPage';
import { renderWithProviders } from '../test-utils';
import { server } from '../mocks/server';

const BASE_URL = 'http://localhost:8000';

describe('AdminOverviewPage', () => {
  it('renderiza cards de health quando API responde', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/health`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            health: {
              sources_total: 3,
              sources_healthy: 2,
              sources_degraded: 1,
              cases_total: 2,
              cases_attention: 1,
              cases_stable: 1,
              integrations: { truth_db: 'ok' },
            },
          }),
        ),
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin" element={<AdminOverviewPage />} />
      </Routes>,
      { route: '/admin' },
    );

    await waitFor(() => {
      expect(screen.getByText(/Fontes ativas/i)).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });
});

describe('AdminSourcesPage', () => {
  it('exibe tabela de fontes', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/sources`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            sources: [
              {
                id: 'src-1',
                name: 'Fonte A',
                type: 'api',
                info_type: 'preco',
                is_active: true,
                status: { status: 'healthy', last_checked_at: '2024-01-01T00:00:00Z', recent_items_count: 5 },
              },
            ],
          }),
        ),
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/sources" element={<AdminSourcesPage />} />
      </Routes>,
      { route: '/admin/sources' },
    );

    await waitFor(() => {
      expect(screen.getByText(/Fonte A/)).toBeInTheDocument();
    });
  });
});
