import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { screen, waitFor } from '@testing-library/react';
import IngestionListPage from '../../modules/ingestion/pages/IngestionListPage';
import IngestionSourceDetailPage from '../../modules/ingestion/pages/IngestionSourceDetailPage';
import IngestionRunDetailModal from '../../modules/ingestion/components/IngestionRunDetailModal';
import { renderWithProviders } from '../test-utils';
import { server } from '../mocks/server';

const BASE_URL = 'http://localhost:8000';

describe('IngestionListPage', () => {
  it('lista fontes e roda ingestão', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/sources`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            sources: [
              { id: 'src-1', name: 'Fonte RSS', type: 'news_rss', state: 'ACTIVE', ingestion_mode: 'MANUAL_ONLY' },
              { id: 'src-2', name: 'Fonte API', type: 'data_api', state: 'ACTIVE', ingestion_mode: 'MANUAL_ONLY' },
            ],
          }),
        ),
      ),
      rest.get(`${BASE_URL}/admin/ingestion/src-1/runs`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            runs: [
              {
                id: 'run-1',
                source_id: 'src-1',
                status: 'SUCCESS',
                trigger: 'MANUAL',
                started_at: '2024-01-01T00:00:00Z',
                finished_at: '2024-01-01T00:05:00Z',
                items_processed: 10,
              },
            ],
          }),
        ),
      ),
      rest.get(`${BASE_URL}/admin/ingestion/src-2/runs`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json({ runs: [] })),
      ),
      rest.post(`${BASE_URL}/admin/ingestion/src-2/run`, (_req, res, ctx) =>
        res(ctx.status(201), ctx.json({ run_id: 'run-new', status: 'RUNNING', trigger: 'MANUAL' })),
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/ingestion" element={<IngestionListPage />} />
      </Routes>,
      { route: '/admin/ingestion' },
    );

    await screen.findByText(/Fonte RSS/, { timeout: 8000 });
    await userEvent.click(screen.getAllByText(/Rodar ingestão/)[1]);
    await screen.findByText(/Ingestão iniciada/, { timeout: 8000 });
  });
});

describe('IngestionSourceDetailPage', () => {
  it('mostra histórico e permite rodar', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/sources/src-1`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json({ source: { id: 'src-1', name: 'Fonte RSS', type: 'news_rss', state: 'ACTIVE', ingestion_mode: 'MANUAL_ONLY' } })),
      ),
      rest.get(`${BASE_URL}/admin/ingestion/src-1/runs`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            runs: [
              {
                id: 'run-1',
                source_id: 'src-1',
                status: 'SUCCESS',
                trigger: 'MANUAL',
                started_at: '2024-01-01T00:00:00Z',
                finished_at: '2024-01-01T00:05:00Z',
                items_processed: 10,
              },
            ],
          }),
        ),
      ),
      rest.post(`${BASE_URL}/admin/ingestion/src-1/run`, (_req, res, ctx) =>
        res(ctx.status(201), ctx.json({ run_id: 'run-2', status: 'RUNNING', trigger: 'MANUAL' })),
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/ingestion/sources/:sourceId" element={<IngestionSourceDetailPage />} />
      </Routes>,
      { route: '/admin/ingestion/sources/src-1' },
    );

    await screen.findByText(/Fonte RSS/, { timeout: 8000 });
    await userEvent.click(screen.getByText(/Rodar ingestão agora/));
    await screen.findByText(/Ingestão iniciada/, { timeout: 8000 });
    expect(screen.getByText(/run-1/)).toBeInTheDocument();
  });
});

describe('Ingestion – ops_only e meta', () => {
  it('exibe banner, modo ops_only e link de histórico para newsdata_br', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/sources`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            sources: [
              { id: 'newsdata_br', slug: 'newsdata_br', name: 'newsdata', type: 'news_api', state: 'ACTIVE', ingestion_mode: 'MANUAL_ONLY' },
              { id: 'src-2', name: 'Outra Fonte', type: 'data_api', state: 'ACTIVE', ingestion_mode: 'MANUAL_ONLY' },
            ],
          }),
        ),
      ),
      rest.get(`${BASE_URL}/admin/ingestion/newsdata_br/runs`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            runs: [
              {
                id: 'run-ops',
                source_id: 'newsdata_br',
                status: 'SUCCESS',
                trigger: 'MANUAL',
                started_at: '2024-02-01T00:00:00Z',
                finished_at: '2024-02-01T00:01:00Z',
                items_processed: 12,
                meta: { requests_count: 5, per_request_size: 10, requested_size: 50, throttle_seconds: 1 },
              },
            ],
            config_mode: 'MANUAL_ONLY',
          }),
        ),
      ),
      rest.get(`${BASE_URL}/admin/ingestion/src-2/runs`, (_req, res, ctx) => res(ctx.status(200), ctx.json({ runs: [] }))),
      rest.post(`${BASE_URL}/api/ingest/newsdata/run`, (_req, res, ctx) =>
        res(ctx.status(201), ctx.json({ run_id: 'new-run', status: 'RUNNING', trigger: 'MANUAL' })),
      ),
      rest.post('/api/ingest/newsdata/run', (_req, res, ctx) => res(ctx.status(201), ctx.json({ run_id: 'new-run', status: 'RUNNING', trigger: 'MANUAL' }))),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/ingestion" element={<IngestionListPage />} />
      </Routes>,
      { route: '/admin/ingestion' },
    );

    const slugCells = await screen.findAllByText(/newsdata_br/, { timeout: 8000 });
    expect(slugCells.length).toBeGreaterThan(0);
    expect(screen.getByText(/CTA ops_ingest aciona pipeline real/i)).toBeInTheDocument();
    expect(screen.getByText(/Modo fixo/)).toBeInTheDocument();
    expect(screen.getAllByText(/Ver histórico/).length).toBeGreaterThanOrEqual(1);
    const runButtons = screen.getAllByText(/Rodar ingestão/i);
    await userEvent.click(runButtons[0]);
    await screen.findByText(/Ingestão iniciada/i, { timeout: 8000 });
  }, 10000);

  it('mostra meta e erro no detalhe e permite retry ops_only', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/sources/newsdata_br`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({ source: { id: 'newsdata_br', slug: 'newsdata_br', name: 'Newsdata', type: 'news_api', state: 'ACTIVE', ingestion_mode: 'MANUAL_ONLY' } }),
        ),
      ),
      rest.get(`${BASE_URL}/admin/ingestion/newsdata_br/runs`, (_req, res, ctx) =>
        res(
          ctx.status(200),
          ctx.json({
            runs: [
              {
                id: 'run-fail',
                source_id: 'newsdata_br',
                status: 'FAIL',
                trigger: 'MANUAL',
                started_at: '2024-02-01T00:00:00Z',
                finished_at: '2024-02-01T00:01:00Z',
                items_processed: 5,
                error_message: 'Erro 500',
                meta: {
                  requests_count: 3,
                  requested_size: 50,
                  per_request_size: 10,
                  throttle_seconds: 1,
                  domains: ['g1.globo.com'],
                  trigger_origin: 'admin_ui',
                },
              },
            ],
          }),
        ),
      ),
      rest.post(`${BASE_URL}/api/ingest/newsdata/run`, (_req, res, ctx) =>
        res(ctx.status(201), ctx.json({ run_id: 'new-run', status: 'RUNNING', trigger: 'MANUAL' })),
      ),
      rest.post('/api/ingest/newsdata/run', (_req, res, ctx) => res(ctx.status(201), ctx.json({ run_id: 'new-run', status: 'RUNNING', trigger: 'MANUAL' }))),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/ingestion/sources/:sourceId" element={<IngestionSourceDetailPage />} />
      </Routes>,
      { route: '/admin/ingestion/sources/newsdata_br' },
    );

    await screen.findByText(/Newsdata/, { timeout: 8000 });
    expect(screen.getByText(/Histórico é só leitura/i)).toBeInTheDocument();
    expect(screen.getByText(/Tentar novamente/)).toBeInTheDocument();
    expect(screen.getByText(/Size por requisição/i)).toBeInTheDocument();
    expect(screen.getByText(/Size total/i)).toBeInTheDocument();
    expect(screen.getByText(/Requests/)).toBeInTheDocument();
    expect(screen.getByText(/Erro do último run/i)).toBeInTheDocument();
    await userEvent.click(screen.getByText(/Tentar novamente/));
  }, 10000);

  it('renderiza modal com tentativas e backoff/duração', () => {
    const run = {
      id: 'run-meta',
      source_id: 'newsdata_br',
      status: 'FAIL',
      trigger: 'MANUAL',
      started_at: '2024-02-01T00:00:00Z',
      finished_at: '2024-02-01T00:01:00Z',
      items_processed: 0,
      payload_ref: 'ref-123',
      meta: {
        attempts: [
          { attempt: 1, status_code: 500, error: 'http_error', backoff_seconds: 1.2, duration_seconds: 0.5 },
          { attempt: 2, status_code: 200, backoff_seconds: 0.0, duration_seconds: 1.0 },
        ],
        requested_size: 50,
        per_request_size: 10,
        throttle_seconds: 1,
        requests_count: 2,
      },
    };

    renderWithProviders(<IngestionRunDetailModal run={run as any} open onClose={() => undefined} />);

    expect(screen.getByText(/Tentativas/i)).toBeInTheDocument();
    expect(screen.getByText(/1.20s/)).toBeInTheDocument();
    expect(screen.getByText(/0.50s/)).toBeInTheDocument();
    expect(screen.getByText(/ref-123/)).toBeInTheDocument();
  });
});
