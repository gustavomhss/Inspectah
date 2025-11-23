import { httpClient } from '../httpClient';
import type { AdminCase, AdminCaseDetail, AdminHealth, AdminSource, AdminSourceDetail, AdminSourceStatus } from '../../types/admin';

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

const ADMIN_BASE = '/admin';

export async function fetchSources(): Promise<AdminSource[]> {
  const response = await httpClient<{ sources: ApiSource[] }>(`${ADMIN_BASE}/sources`);
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

export async function fetchSourceDetail(sourceId: string): Promise<AdminSourceDetail> {
  const response = await httpClient<{ source: ApiSource }>(`${ADMIN_BASE}/sources/${encodeURIComponent(sourceId)}`);
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

export async function fetchCases(): Promise<AdminCase[]> {
  const response = await httpClient<{ cases: AdminCase[] }>(`${ADMIN_BASE}/cases`);
  return response.cases || [];
}

export async function fetchCaseDetail(caseId: string): Promise<AdminCaseDetail> {
  const response = await httpClient<{ case: AdminCaseDetail }>(`${ADMIN_BASE}/cases/${encodeURIComponent(caseId)}`);
  return response.case;
}

export async function fetchHealth(): Promise<AdminHealth> {
  const response = await httpClient<{ health: AdminHealth }>(`${ADMIN_BASE}/health`);
  return response.health;
}
