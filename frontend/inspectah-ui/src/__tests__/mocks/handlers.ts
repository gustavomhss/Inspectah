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

// Admin cases timeline/xray (fallback)
handlers.push(
  rest.get(new RegExp(`${BASE_URL}/admin/cases/.+/timeline`), (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        timeline: [
          { id: 'evt-1', timestamp: '2024-01-01T00:00:00Z', event_type: 'start', title: 'ordem de início publicada' },
        ],
      }),
    ),
  ),
  rest.get(new RegExp(`${BASE_URL}/admin/cases/.+/xray`), (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        xray: {
          case_id: 'fallback',
          summary: 'Raio-X do caso',
          risk: 'alto',
          anchors: [],
          evidence: [],
        },
      }),
    ),
  ),
  rest.get(`${BASE_URL}/admin/cases`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        cases: [
          {
            id: 'obra_publica:2025-123',
            title: 'Caso fallback',
            category: 'obra_publica',
            status: 'em_atraso',
            risk: 'alto',
            updated_at: '2025-01-01T00:00:00Z',
            key_sources: ['fallback'],
          },
        ],
      }),
    ),
  ),
);

// Providers/profiles fallback
handlers.push(
  rest.get(`${BASE_URL}/api/providers`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json([
        { id: 'prov-news', name: 'News Pilot', kind: 'news_provider', description: 'Provider de notícias', status: 'active' },
      ]),
    ),
  ),
  rest.get(`${BASE_URL}/api/providers/profiles`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json([
        {
          profile: {
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
          },
          metrics: { total_runs: 1, success: 1, fail: 0, last_run_at: '2024-01-01', items: 3, persisted: 3 },
          last_run: {
            run_id: 'run1',
            provider_id: 'prov-news',
            profile_id: 'prof-1',
            started_at: '2024-01-01',
            finished_at: '2024-01-01',
            status: 'success',
            items: 3,
            persisted: 3,
            calls: 3,
          },
        },
      ]),
    ),
  ),
  rest.get(`${BASE_URL}/api/providers/:id`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        provider: { id: 'prov-news', name: 'News Pilot', kind: 'news_provider', description: 'Provider de notícias', status: 'active' },
        profiles: [],
      }),
    ),
  ),
  rest.post(`${BASE_URL}/api/providers/profiles/:profileId/run-now`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        status: 'queued',
        run: {
          run_id: 'run-queued',
          provider_id: 'prov-news',
          profile_id: 'prof-1',
          started_at: '2024-01-01',
          finished_at: '2024-01-01',
          status: 'success',
          items: 2,
          persisted: 2,
          calls: 2,
        },
      }),
    ),
  ),
);

// Guardian API
handlers.push(
  rest.get(`${BASE_URL}/api/guardian/metrics`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        decisions_submitted: 100,
        decisions_approved: 80,
        decisions_rejected: 15,
        decisions_timed_out: 5,
        avg_latency_ms: 150.5,
        pending_decisions: 10,
        awaiting_review: 3,
        awaiting_quorum: 2,
      }),
    ),
  ),
  rest.get(`${BASE_URL}/api/guardian/decisions`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json([
        {
          id: 'dec_001',
          claim_id: 'claim_001',
          claim_summary: 'Lula foi condenado pelo TRF4',
          evidence_summary: ['Acórdão TRF4', 'Reportagem Folha'],
          domain: 'politics',
          gate: 'G7',
          proposed_state: 'verified',
          status: 'awaiting_review',
          policy_name: 'pilot_politics_v1',
          committee_id: null,
          final_state: null,
          final_reason: null,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          completed_at: null,
        },
      ]),
    ),
  ),
  rest.get(`${BASE_URL}/api/guardian/decisions/awaiting-review`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json([
        {
          id: 'dec_001',
          claim_id: 'claim_001',
          claim_summary: 'Lula foi condenado pelo TRF4',
          evidence_summary: ['Acórdão TRF4'],
          domain: 'politics',
          gate: 'G7',
          proposed_state: 'verified',
          status: 'awaiting_review',
          policy_name: 'pilot_politics_v1',
          committee_id: null,
          final_state: null,
          final_reason: null,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          completed_at: null,
        },
      ]),
    ),
  ),
  rest.get(`${BASE_URL}/api/guardian/policies`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json([
        {
          name: 'pilot_politics_v1',
          domain: 'politics',
          gate: 'G7',
          version: '1.0.0',
          requirements: 4,
          rules: 5,
        },
        {
          name: 'economia_v1',
          domain: 'economia',
          gate: 'G7',
          version: '1.0.0',
          requirements: 4,
          rules: 6,
        },
      ]),
    ),
  ),
  rest.get(`${BASE_URL}/api/guardian/policies/:name`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        name: 'pilot_politics_v1',
        domain: 'politics',
        gate: 'G7',
        version: '1.0.0',
        requirements: [
          { field: 'sources', operator: '>=', value: 2, modifier: 'independent' },
          { field: 'evidence_strength', operator: '>=', value: 0.6, modifier: null },
        ],
        rules: [
          { condition_field: 'high_confidence', condition_operator: '=', condition_value: true, action: 'auto_approve', action_params: {} },
          { condition_field: 'low_confidence', condition_operator: '=', condition_value: true, action: 'human_review', action_params: {} },
        ],
        metadata: {},
      }),
    ),
  ),
);
