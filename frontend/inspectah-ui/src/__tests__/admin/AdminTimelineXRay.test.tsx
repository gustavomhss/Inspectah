import { readFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import AdminCaseTimelinePage from '../../pages/admin/AdminCaseTimelinePage';
import AdminCaseXRayPage from '../../pages/admin/AdminCaseXRayPage';
import AdminCasesPage from '../../pages/admin/AdminCasesPage';
import AdminCaseDetailPage from '../../pages/admin/AdminCaseDetailPage';
import { server } from '../mocks/server';

const BASE_URL = 'http://localhost:8000';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_ROOT = path.resolve(__dirname, '..', '..', '..', '..', '..', 'Sprint 19', 'fixtures');

function loadFixture(name: string) {
  const content = readFileSync(path.join(FIXTURE_ROOT, name), 'utf-8');
  return JSON.parse(content);
}

describe('Admin timeline e raio-X', () => {
  it('renderiza timeline com filtros e eventos ordenados', async () => {
    const timeline = loadFixture('timeline_expected_obra_publica_2025_123.json');
    server.use(
      rest.get(`${BASE_URL}/admin/cases/obra_publica:2025-123/timeline`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json({ timeline })),
      ),
    );

    render(
      <MemoryRouter initialEntries={['/admin/cases/obra_publica:2025-123/timeline']}>
        <Routes>
          <Route path="/admin/cases/:caseId/timeline" element={<AdminCaseTimelinePage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText(/Carregando timeline/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/Histórico do caso/)).toBeInTheDocument();
      expect(screen.getByText(/ordem de início publicada/i)).toBeInTheDocument();
    });

    const selects = screen.getAllByRole('combobox');
    fireEvent.change(selects[1], { target: { value: 'critical' } });

    await waitFor(() => {
      expect(screen.getByText(/ancora-falha/i)).toBeInTheDocument();
      expect(screen.queryByText(/ordem de início publicada/i)).not.toBeInTheDocument();
    });
  });

  it('mostra erro amigável quando timeline não existe', async () => {
    server.use(
      rest.get(`${BASE_URL}/admin/cases/desconhecido/timeline`, (_req, res, ctx) =>
        res(ctx.status(404), ctx.json({ detail: 'Timeline não encontrada' })),
      ),
    );

    render(
      <MemoryRouter initialEntries={['/admin/cases/desconhecido/timeline']}>
        <Routes>
          <Route path="/admin/cases/:caseId/timeline" element={<AdminCaseTimelinePage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText(/Timeline não encontrada/i)).toBeInTheDocument();
    });
  });

  it('renderiza raio-X com seções principais', async () => {
    const xray = loadFixture('xray_expected_evento_climatico_inmet_2025_0901.json');
    server.use(
      rest.get(`${BASE_URL}/admin/cases/evento_climatico:inmet-2025-0901/xray`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json({ xray })),
      ),
    );

    render(
      <MemoryRouter initialEntries={['/admin/cases/evento_climatico:inmet-2025-0901/xray']}>
        <Routes>
          <Route path="/admin/cases/:caseId/xray" element={<AdminCaseXRayPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText(/Raio-X do caso/)).toBeInTheDocument();
      expect(screen.getByText(/Avaliação e flags/)).toBeInTheDocument();
      expect(screen.getByText(/Decisões e divergências/)).toBeInTheDocument();
      expect(screen.getByText(/Estado das âncoras/)).toBeInTheDocument();
      expect(screen.getByText(/Principais evidências/)).toBeInTheDocument();
    });
  });

  it('permite navegar da lista de casos para timeline e raio-X', async () => {
    const casesPayload = {
      cases: [
        {
          id: 'obra_publica:2025-123',
          title: 'Contrato 2025-123 — Escola Municipal Vila Verde',
          category: 'obra_publica',
          status: 'em_atraso',
          risk: 'alto',
          updated_at: '2025-09-20T06:35:00Z',
          key_sources: ['s12_obras_diario_niteroi'],
        },
      ],
    };
    const timeline = loadFixture('timeline_expected_obra_publica_2025_123.json');
    const xray = loadFixture('xray_expected_obra_publica_2025_123.json');

    server.use(
      rest.get(`${BASE_URL}/admin/cases`, (_req, res, ctx) => res(ctx.status(200), ctx.json(casesPayload))),
      rest.get(`${BASE_URL}/admin/cases/obra_publica:2025-123/timeline`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json({ timeline })),
      ),
      rest.get(`${BASE_URL}/admin/cases/obra_publica:2025-123/xray`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json({ xray })),
      ),
    );

    render(
      <MemoryRouter initialEntries={['/admin/cases']}>
        <Routes>
          <Route path="/admin/cases" element={<AdminCasesPage />} />
          <Route path="/admin/cases/:caseId" element={<AdminCaseDetailPage />} />
          <Route path="/admin/cases/:caseId/timeline" element={<AdminCaseTimelinePage />} />
          <Route path="/admin/cases/:caseId/xray" element={<AdminCaseXRayPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText(/Contrato 2025-123/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Timeline'));

    await waitFor(() => {
      expect(screen.getByText(/Histórico do caso/)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Ver raio-X/i));

    await waitFor(() => {
      expect(screen.getByText(/Raio-X do caso/)).toBeInTheDocument();
    });
  });
});
