import { endpoints } from '../../../core/api/endpoints';
import { httpClient } from '../../../core/api/http-client';
import type { IngestionConfig, IngestionRun, IngestionRunsResponse, TriggerRunResponse } from '../../../core/api/api-types';

export async function getRunsBySource(sourceId: string, params: { limit?: number; offset?: number } = {}, authToken?: string) {
  const search = new URLSearchParams();
  if (params.limit) search.set('limit', String(params.limit));
  if (params.offset) search.set('offset', String(params.offset));
  const path = `${endpoints.admin.ingestion.runsBySource(sourceId)}${search.toString() ? `?${search.toString()}` : ''}`;
  return httpClient<IngestionRunsResponse>(path, { authToken });
}

export async function getRun(runId: string, authToken?: string) {
  return httpClient<IngestionRun>(endpoints.admin.ingestion.runDetail(runId), { authToken });
}

export async function runIngestionNow(sourceId: string, authToken?: string) {
  const sid = sourceId || '';
  if (sid === 'newsdata_br' || sid === 'src_afca2b6b12' || sid.includes('newsdata')) {
    return httpClient<TriggerRunResponse>('/api/ingest/newsdata/run', {
      method: 'POST',
      body: JSON.stringify({ trigger_origin: 'admin_ui', size: 50, throttle_seconds: 1, max_attempts: 3 }),
      headers: { 'x-role': 'ops_ingest' },
      authToken,
    });
  }
  return httpClient<TriggerRunResponse>(endpoints.admin.ingestion.run(sid), {
    method: 'POST',
    body: JSON.stringify({ trigger_origin: 'admin_ui', force: true }),
    headers: { 'x-role': 'admin' },
    authToken,
  });
}

export async function toggleIngestionMode(sourceId: string, mode: IngestionConfig['mode'], authToken?: string) {
  return httpClient<IngestionConfig>(endpoints.admin.ingestion.toggleMode(sourceId), {
    method: 'POST',
    body: JSON.stringify({ mode, enabled: true }),
    authToken,
  });
}
