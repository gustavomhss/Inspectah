import { rest } from 'msw';
import type { ConsultationResponseRaw } from '../../core/api/api-types';

const BASE_URL = 'http://localhost:8000';

export const buildResponse = (overrides: Partial<ConsultationResponseRaw> = {}): ConsultationResponseRaw => ({
  answer: 'Sim, o fato foi confirmado por múltiplas fontes independentes.',
  risk_level: 'low',
  risk_score: 0.12,
  evidences: [
    {
      id: 'ev-1',
      source_name: 'Agência Oficial',
      source_type: 'documento',
      description: 'Comunicado oficial confirmando o fato.',
      link: 'https://example.com/oficial',
    },
  ],
  request_id: 'req-123',
  generated_at: '2024-01-01T12:00:00Z',
  ...overrides,
});

export const successHandler = rest.post(`${BASE_URL}/api/consultation`, async (_req, res, ctx) => {
  return res(ctx.status(200), ctx.json(buildResponse()));
});

export const highRiskHandler = rest.post(`${BASE_URL}/api/consultation`, async (_req, res, ctx) => {
  return res(ctx.status(200), ctx.json(buildResponse({ risk_level: 'high', risk_score: 0.78 })));
});

export const unknownRiskHandler = rest.post(`${BASE_URL}/api/consultation`, async (_req, res, ctx) => {
  return res(ctx.status(200), ctx.json(buildResponse({ risk_level: 'unknown', risk_flags: ['Dados limitados'] })));
});

export const errorHandler = (status: number, message?: string) =>
  rest.post(`${BASE_URL}/api/consultation`, async (_req, res, ctx) => {
    return res(
      ctx.status(status),
      ctx.json({ error: message || (status >= 500 ? 'server error' : 'client error') }),
    );
  });

export const handlers = [successHandler];

export const authHandler = rest.post(`${BASE_URL}/auth/login`, async (req, res, ctx) => {
  const body = await req.json();
  return res(
    ctx.status(200),
    ctx.json({
      token: 'test-token',
      user: {
        id: body.username ?? 'tester',
        email: `${body.username ?? 'tester'}@inspectah.local`,
      },
    }),
  );
});

handlers.push(authHandler);

// Ops Cockpit
handlers.push(
  rest.get(`${BASE_URL}/api/ops/cockpit/overview`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        components: 3,
        incidents: 2,
        slos: [
          { slo_id: 's33_slo_recencia_fonte_noticias', status: 'OK', metrica: 'metric', janela: '15m', limiar: '<=900' },
          { slo_id: 's33_slo_latencia_pipeline_noticias', status: 'DEGRADED', metrica: 'metric', janela: '30m', limiar: '<=60' },
        ],
      }),
    ),
  ),
  rest.get(`${BASE_URL}/api/ops/cockpit/components`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json([
        { id: 'fonte_noticias_principal', tipo: 'fonte', criticidade: 'alta', descricao: 'Feed' },
        { id: 'pipeline_noticias', tipo: 'pipeline', criticidade: 'alta', descricao: 'Pipeline' },
      ]),
    ),
  ),
  rest.get(`${BASE_URL}/api/ops/cockpit/incidents`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json([
        { id: 'inc1', title: 'Falha fonte', severity: 'HIGH', state: 'OPEN', component_id: 'fonte_noticias_principal' },
        { id: 'inc2', title: 'Latência alta', severity: 'MEDIUM', state: 'TRIAGE', component_id: 'pipeline_noticias' },
      ]),
    ),
  ),
);
