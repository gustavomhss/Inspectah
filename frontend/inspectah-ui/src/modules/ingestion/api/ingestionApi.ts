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
  return httpClient<TriggerRunResponse>(endpoints.admin.ingestion.run(sourceId), {
    method: 'POST',
    body: JSON.stringify({ trigger_origin: 'admin_ui', force: true }),
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
