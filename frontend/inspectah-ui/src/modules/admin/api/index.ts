import { endpoints } from '../../../core/api/endpoints';
import { httpClient } from '../../../core/api/http-client';
import type {
  AdminCase,
  AdminCaseDetail,
  AdminCaseXRay,
  AdminHealth,
  AdminSource,
  AdminSourceDetail,
  AdminSourceHealthStatus,
  AdminTimelineResponse,
} from '../../../core/api/api-types';

export async function fetchSources(authToken?: string): Promise<AdminSource[]> {
  const response = await httpClient<{ sources: AdminSource[] }>(endpoints.admin.sources, { authToken });
  return response.sources || [];
}

export async function fetchSourceDetail(sourceId: string, authToken?: string): Promise<AdminSourceDetail> {
  const response = await httpClient<{ source: AdminSourceDetail }>(endpoints.admin.sourceDetail(sourceId), { authToken });
  return response.source;
}

export async function createSource(payload: Partial<AdminSource>, authToken?: string): Promise<AdminSourceDetail> {
  const response = await httpClient<{ source: AdminSourceDetail }>(endpoints.admin.sources, {
    method: 'POST',
    body: JSON.stringify(payload),
    authToken,
  });
  return response.source;
}

export async function updateSource(sourceId: string, payload: Partial<AdminSource>, authToken?: string): Promise<AdminSourceDetail> {
  const response = await httpClient<{ source: AdminSourceDetail }>(endpoints.admin.sourceDetail(sourceId), {
    method: 'PUT',
    body: JSON.stringify(payload),
    authToken,
  });
  return response.source;
}

export async function triggerSourceHealthcheck(sourceId: string, authToken?: string): Promise<{ status: AdminSourceHealthStatus }> {
  const response = await httpClient<{ status: AdminSourceHealthStatus }>(`${endpoints.admin.sourceDetail(sourceId)}/healthcheck`, {
    method: 'POST',
    authToken,
  });
  return response;
}

export async function fetchHealthchecks(sourceId: string, authToken?: string) {
  const response = await httpClient<{ healthchecks: Array<{ status: AdminSourceHealthStatus; checked_at?: string; error?: string; latency_ms?: number }> }>(
    `${endpoints.admin.sourceDetail(sourceId)}/healthchecks`,
    { authToken }
  );
  return response.healthchecks || [];
}

export async function fetchCases(authToken?: string): Promise<AdminCase[]> {
  const response = await httpClient<{ cases: AdminCase[] }>(endpoints.admin.cases, { authToken });
  return response.cases || [];
}

export async function fetchCaseDetail(caseId: string, authToken?: string): Promise<AdminCaseDetail> {
  const response = await httpClient<{ case: AdminCaseDetail }>(endpoints.admin.caseDetail(caseId), { authToken });
  return response.case;
}

export async function getAdminCaseTimeline(caseId: string, authToken?: string): Promise<AdminTimelineResponse> {
  const response = await httpClient<{ timeline: AdminTimelineResponse }>(endpoints.admin.timeline(caseId), { authToken });
  return response.timeline;
}

export async function getAdminCaseXRay(caseId: string, authToken?: string): Promise<AdminCaseXRay> {
  const response = await httpClient<{ xray: AdminCaseXRay }>(endpoints.admin.xray(caseId), { authToken });
  return response.xray;
}

export async function fetchHealth(authToken?: string): Promise<AdminHealth> {
  const response = await httpClient<{ health: AdminHealth }>(endpoints.admin.health, { authToken });
  return response.health;
}
