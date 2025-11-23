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
  },
};
