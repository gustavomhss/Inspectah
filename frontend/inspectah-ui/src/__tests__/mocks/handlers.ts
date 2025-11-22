import { rest } from 'msw';
import type { ConsultationResponseRaw } from '../../types/inspectah';

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
