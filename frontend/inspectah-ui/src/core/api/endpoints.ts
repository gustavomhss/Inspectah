import { env } from '../config/env';

export const endpoints = {
  consult: env.consultationPath,
  auth: {
    login: '/auth/login',
  },
  admin: {
    health: '/admin/health',
    sources: '/admin/sources',
    sourceDetail: (sourceId: string) => `/admin/sources/${encodeURIComponent(sourceId)}`,
    cases: '/admin/cases',
    caseDetail: (caseId: string) => `/admin/cases/${encodeURIComponent(caseId)}`,
    timeline: (caseId: string) => `/admin/cases/${encodeURIComponent(caseId)}/timeline`,
    xray: (caseId: string) => `/admin/cases/${encodeURIComponent(caseId)}/xray`,
    copiloto: {
      sessions: '/admin/copiloto-fontes/sessions',
      messages: (sessionId: string) => `/admin/copiloto-fontes/sessions/${encodeURIComponent(sessionId)}/messages`,
      files: (sessionId: string) => `/admin/copiloto-fontes/sessions/${encodeURIComponent(sessionId)}/files`,
    },
    ingestion: {
      run: (sourceId: string) => `/admin/ingestion/${encodeURIComponent(sourceId)}/run`,
      toggleMode: (sourceId: string) => `/admin/ingestion/${encodeURIComponent(sourceId)}/toggle-mode`,
      runsBySource: (sourceId: string) => `/admin/ingestion/${encodeURIComponent(sourceId)}/runs`,
      runDetail: (runId: string) => `/admin/ingestion/runs/${encodeURIComponent(runId)}`,
    },
    agents: {
      list: '/api/console/agents',
      detail: (agentId: string) => `/api/console/agents/${encodeURIComponent(agentId)}`,
      instructions: (agentId: string) => `/api/console/agents/${encodeURIComponent(agentId)}/instructions`,
      committees: '/api/console/agents/committees',
      committeeDetail: (committeeId: string) => `/api/console/agents/committees/${encodeURIComponent(committeeId)}`,
      committeeRuns: (committeeId: string) => `/api/console/agents/committees/${encodeURIComponent(committeeId)}/runs`,
      committeeDryRun: (committeeId: string) => `/api/console/agents/committees/${encodeURIComponent(committeeId)}/dry-run`,
      modelPolicy: '/api/console/agents/policies/model-upgrades',
      flow: '/api/console/agents/flow',
    },
  },
};
