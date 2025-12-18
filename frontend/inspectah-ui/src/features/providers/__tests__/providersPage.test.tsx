import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { renderWithProviders } from '../../../__tests__/test-utils';
import { server } from '../../../__tests__/mocks/server';
import ProvidersPage from '../ProvidersPage';

const BASE_URL = 'http://localhost:8000';
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  vi.spyOn(console, 'error').mockImplementation((...args: unknown[]) => {
    const message = args[0];
    if (typeof message === 'string' && message.includes('not wrapped in act')) {
      return;
    }
    originalError.apply(console, args as Parameters<typeof console.error>);
  });

  vi.spyOn(console, 'warn').mockImplementation((...args: unknown[]) => {
    const message = args[0];
    if (typeof message === 'string' && message.includes('React Router Future Flag Warning')) {
      return;
    }
    originalWarn.apply(console, args as Parameters<typeof console.warn>);
  });
});

afterAll(() => {
  (console.error as unknown as { mockRestore: () => void }).mockRestore();
  (console.warn as unknown as { mockRestore: () => void }).mockRestore();
});

const provider = {
  id: 'prov-news',
  name: 'News Pilot',
  kind: 'news_provider',
  description: 'Provider de notícias',
  status: 'active',
};

const profile = {
  id: 'prof-1',
  provider_id: 'prov-news',
  name: 'Perfil BR',
  slug: 'perfil-br',
  kind: 'news',
  country: 'BR',
  language: 'pt',
  categories: [],
  keywords: [],
  filters: {},
  frequency_minutes: 60,
  budget_daily_calls: 10,
  budget_monthly_calls: 200,
  enabled: true,
  status: 'active',
  metadata: {},
};

describe('ProvidersPage', () => {
  beforeEach(() => {
    server.use(
      rest.get(`${BASE_URL}/api/providers`, (_req, res, ctx) => res(ctx.status(200), ctx.json([provider]))),
      rest.get(`${BASE_URL}/api/providers/${provider.id}`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            provider,
            profiles: [
              {
                profile,
                metrics: { total_runs: 1, success: 1, fail: 0, last_run_at: '2024-01-01', items: 3, persisted: 3 },
                last_run: {
                  run_id: 'run1',
                  provider_id: provider.id,
                  profile_id: profile.id,
                  started_at: '2024-01-01',
                  finished_at: '2024-01-01',
                  status: 'success',
                  items: 3,
                  persisted: 3,
                  calls: 3,
                },
              },
            ],
          }),
        ),
      ),
    );
  });

  it('renderiza providers e perfis com estados básicos', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/providers" element={<ProvidersPage />} />
      </Routes>,
      { route: '/admin/providers' },
    );

    await screen.findByText('News Pilot');
    await screen.findByText('Perfil BR');
    expect(screen.getByText(/Runs: 1/)).toBeInTheDocument();
  });

  it('aciona run-now para um perfil', async () => {
    const runSpy = vi.fn();
    server.use(
      rest.post(`${BASE_URL}/api/providers/profiles/${profile.id}/run-now`, async (_req, res, ctx) => {
        runSpy();
        return res(
          ctx.status(200),
          ctx.json({
            status: 'queued',
            run: {
              run_id: 'run-queued',
              provider_id: provider.id,
              profile_id: profile.id,
              started_at: '2024-01-01',
              finished_at: '2024-01-01',
              status: 'success',
              items: 2,
              persisted: 2,
              calls: 2,
            },
          }),
        );
      }),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/providers" element={<ProvidersPage />} />
      </Routes>,
      { route: '/admin/providers' },
    );

    const providerRow = await screen.findByRole('button', { name: /News Pilot/i });
    await userEvent.click(providerRow);

    const runButton = await screen.findByRole('button', { name: /Rodar agora/i });
    await userEvent.click(runButton);

    await waitFor(() => expect(runSpy).toHaveBeenCalled());
    expect(await screen.findByText(/Execução enviada/)).toBeInTheDocument();
  });
});
