import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { screen, waitFor } from '@testing-library/react';
import IngestionListPage from '../../modules/ingestion/pages/IngestionListPage';
import IngestionSourceDetailPage from '../../modules/ingestion/pages/IngestionSourceDetailPage';
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
              { id: 'src-1', name: 'Fonte RSS', type: 'news_rss', state: 'ACTIVE' },
              { id: 'src-2', name: 'Fonte API', type: 'data_api', state: 'ACTIVE' },
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
        res(ctx.status(200), ctx.json({ source: { id: 'src-1', name: 'Fonte RSS', type: 'news_rss', state: 'ACTIVE' } })),
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
