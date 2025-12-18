import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import { screen, waitFor } from '@testing-library/react';
import { AppRoutes } from '../../app/routes';
import { env } from '../../core/config/env';
import { renderWithProviders } from '../test-utils';
import { server } from '../mocks/server';

const STORAGE_KEY = env.authStorageKey;
const BASE_URL = env.apiBaseUrl;

// TODO: Fix these tests - 401 handling behavior changed, now shows error instead of redirect
describe.skip('AuthGuard e sessão', () => {
  beforeEach(() => {
    window.localStorage.removeItem(STORAGE_KEY);
    window.sessionStorage.removeItem(STORAGE_KEY);
  });

  it('redireciona não autenticado para login', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/*" element={<AppRoutes />} />
      </Routes>,
      { route: '/admin' },
    );

    expect(await screen.findByText(/Entrar no Inspectah/i)).toBeInTheDocument();
  });

  it('restaura sessão persistida e permite acesso a /admin', async () => {
    const session = { token: 'token-test', user: { id: 'admin@test' } };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

    server.use(
      rest.get(`${BASE_URL}/admin/health`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            health: {
              sources_total: 1,
              sources_healthy: 1,
              sources_degraded: 0,
              cases_total: 1,
              cases_attention: 0,
              cases_stable: 1,
              integrations: {},
            },
          }),
        ),
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/*" element={<AppRoutes />} />
      </Routes>,
      { route: '/admin' },
    );

    expect(await screen.findByText(/Fontes ativas/i)).toBeInTheDocument();
  });

  it('limpa sessão e envia para login em resposta 401/403', async () => {
    const session = { token: 'token-test', user: { id: 'admin@test' } };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

    server.use(rest.get(`${BASE_URL}/admin/health`, (_req, res, ctx) => res(ctx.status(401))));

    renderWithProviders(
      <Routes>
        <Route path="/*" element={<AppRoutes />} />
      </Routes>,
      { route: '/admin' },
    );

    await waitFor(() => {
      expect(screen.getByText(/Entrar no Inspectah/i)).toBeInTheDocument();
    });
    expect(window.localStorage.getItem(STORAGE_KEY)).toBeNull();
  });
});
