/**
 * S38-FE-010: API Client para Sources
 */

import { httpClient } from '../../../core/api/http-client';
import type {
  Source,
  SourceDetail,
  SourceFormData,
  SourceMetrics,
  DryRunResult,
  IngestionRun,
} from '../types';

const BASE_URL = '/api/v1/sources';

export interface ListSourcesParams {
  source_type?: string;
  state?: string;
  enabled?: boolean;
  q?: string;
}

export interface IngestionHistoryResponse {
  source_id: string;
  runs: IngestionRun[];
  pagination: {
    limit: number;
    offset: number;
    total: number;
  };
}

export interface TriggerIngestionResponse {
  run_id: string;
  status: string;
  triggered_at: string;
}

export interface HealthCheckResponse {
  source_id: string;
  status: string;
  latency_ms: number;
  checked_at: string;
  consecutive_successes: number;
  consecutive_failures: number;
  uptime_percent: number;
  error_message?: string;
}

/**
 * Lista todas as fontes
 */
export async function listSources(
  params?: ListSourcesParams,
  authToken?: string
): Promise<Source[]> {
  const queryParams = new URLSearchParams();
  if (params?.source_type) queryParams.set('source_type', params.source_type);
  if (params?.state) queryParams.set('state', params.state);
  if (params?.enabled !== undefined) queryParams.set('enabled', String(params.enabled));
  if (params?.q) queryParams.set('q', params.q);

  const url = queryParams.toString() ? `${BASE_URL}?${queryParams}` : BASE_URL;
  return httpClient<Source[]>(url, { authToken });
}

/**
 * Busca detalhes de uma fonte
 */
export async function getSource(sourceId: string, authToken?: string): Promise<SourceDetail> {
  return httpClient<SourceDetail>(`${BASE_URL}/${sourceId}`, { authToken });
}

/**
 * Cria uma nova fonte
 */
export async function createSource(data: SourceFormData, authToken?: string): Promise<Source> {
  return httpClient<Source>(BASE_URL, {
    method: 'POST',
    body: JSON.stringify(data),
    authToken,
  });
}

/**
 * Atualiza uma fonte
 */
export async function updateSource(
  sourceId: string,
  data: Partial<SourceFormData>,
  authToken?: string
): Promise<Source> {
  return httpClient<Source>(`${BASE_URL}/${sourceId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
    authToken,
  });
}

/**
 * Remove uma fonte
 */
export async function deleteSource(sourceId: string, authToken?: string): Promise<void> {
  await httpClient<void>(`${BASE_URL}/${sourceId}`, {
    method: 'DELETE',
    authToken,
  });
}

/**
 * Muda o estado de uma fonte
 */
export async function changeSourceState(
  sourceId: string,
  targetState: string,
  reason: string,
  authToken?: string
): Promise<Source> {
  const params = new URLSearchParams({
    target_state: targetState,
    reason,
  });
  return httpClient<Source>(`${BASE_URL}/${sourceId}/status?${params}`, {
    method: 'POST',
    authToken,
  });
}

/**
 * Executa dry-run de uma fonte
 */
export async function dryRunSource(
  sourceId: string,
  options?: { url?: string; limit?: number },
  authToken?: string
): Promise<DryRunResult> {
  return httpClient<DryRunResult>(`${BASE_URL}/${sourceId}/dry-run`, {
    method: 'POST',
    body: JSON.stringify(options || {}),
    authToken,
  });
}

/**
 * Dispara ingestao de uma fonte
 */
export async function triggerIngestion(
  sourceId: string,
  options?: { force?: boolean; limit?: number },
  authToken?: string
): Promise<TriggerIngestionResponse> {
  return httpClient<TriggerIngestionResponse>(`${BASE_URL}/${sourceId}/trigger`, {
    method: 'POST',
    body: JSON.stringify(options || {}),
    authToken,
  });
}

/**
 * Busca metricas de uma fonte
 */
export async function getSourceMetrics(
  sourceId: string,
  period: '1h' | '24h' | '7d' = '24h',
  authToken?: string
): Promise<SourceMetrics> {
  return httpClient<SourceMetrics>(`${BASE_URL}/${sourceId}/metrics?period=${period}`, {
    authToken,
  });
}

/**
 * Busca historico de ingestao
 */
export async function getIngestionHistory(
  sourceId: string,
  options?: { limit?: number; offset?: number },
  authToken?: string
): Promise<IngestionHistoryResponse> {
  const params = new URLSearchParams();
  if (options?.limit) params.set('limit', String(options.limit));
  if (options?.offset) params.set('offset', String(options.offset));

  const url = params.toString()
    ? `${BASE_URL}/${sourceId}/history?${params}`
    : `${BASE_URL}/${sourceId}/history`;

  return httpClient<IngestionHistoryResponse>(url, { authToken });
}

/**
 * Busca status de saude de uma fonte
 */
export async function getSourceHealth(
  sourceId: string,
  authToken?: string
): Promise<HealthCheckResponse> {
  return httpClient<HealthCheckResponse>(`${BASE_URL}/${sourceId}/health`, { authToken });
}

/**
 * Dispara health check manual
 */
export async function triggerHealthCheck(
  sourceId: string,
  authToken?: string
): Promise<HealthCheckResponse> {
  return httpClient<HealthCheckResponse>(`${BASE_URL}/${sourceId}/health`, {
    method: 'POST',
    authToken,
  });
}
