import { endpoints } from '../../../core/api/endpoints';
import { httpClient } from '../../../core/api/http-client';
import type {
  AdminCase,
  AdminCaseDetail,
  AdminCaseXRay,
  AdminHealth,
  AdminSource,
  AdminSourceDetail,
  AdminSourceStatus,
  AdminTimelineResponse,
} from '../../../core/api/api-types';

interface ApiSource {
  id: string;
  name: string;
  type: string;
  info_type?: string;
  is_active?: boolean;
  url_base?: string;
  status: {
    status: AdminSourceStatus;
    last_checked_at?: string | null;
    last_error?: string | null;
    recent_items_count: number;
  };
  history?: Array<{
    checked_at?: string | null;
    status: AdminSourceStatus;
    error?: string | null;
  }>;
}

export async function fetchSources(authToken?: string): Promise<AdminSource[]> {
  const response = await httpClient<{ sources: ApiSource[] }>(endpoints.admin.sources, { authToken });
  return (response.sources || []).map((src) => ({
    id: src.id,
    name: src.name,
    type: src.type,
    info_type: src.info_type,
    is_active: src.is_active ?? true,
    status: src.status?.status || 'unknown',
    last_checked_at: src.status?.last_checked_at,
    last_error: src.status?.last_error,
    recent_items_count: src.status?.recent_items_count ?? 0,
    url_base: src.url_base,
  }));
}

export async function fetchSourceDetail(sourceId: string, authToken?: string): Promise<AdminSourceDetail> {
  const response = await httpClient<{ source: ApiSource }>(endpoints.admin.sourceDetail(sourceId), { authToken });
  const src = response.source;
  return {
    id: src.id,
    name: src.name,
    type: src.type,
    info_type: src.info_type,
    is_active: src.is_active ?? true,
    status: src.status?.status || 'unknown',
    last_checked_at: src.status?.last_checked_at,
    last_error: src.status?.last_error,
    recent_items_count: src.status?.recent_items_count ?? 0,
    url_base: src.url_base,
    history: src.history || [],
  };
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
