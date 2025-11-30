import { endpoints } from '@/core/api/endpoints';
import { httpClient } from '@/core/api/http-client';
import type { Source, SourceFilters, SourcePayload, SourceStatus } from '../types/Source';

function slugify(text: string): string {
  return text
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '')
    .trim();
}

function normalizeSource(source: Source): Source {
  const endpoint = source.endpoint || (source as Source & { url_base?: string }).url_base || '';
  return { ...source, endpoint };
}

function buildQuery(filters?: SourceFilters): string {
  const params = new URLSearchParams();
  if (filters?.type) params.set('type', filters.type);
  if (filters?.category) params.set('category', filters.category);
  if (filters?.state) params.set('state', filters.state);
  if (filters?.health_status) params.set('health_status', filters.health_status);
  return params.toString() ? `?${params.toString()}` : '';
}

export async function listSources(filters?: SourceFilters): Promise<Source[]> {
  const query = buildQuery(filters);
  const response = await httpClient<{ sources: Source[] }>(`${endpoints.admin.sources}${query}`);
  return (response.sources || []).map(normalizeSource);
}

export async function getSourceById(id: string): Promise<Source | null> {
  const response = await httpClient<{ source: Source }>(endpoints.admin.sourceDetail(id));
  return response.source ? normalizeSource(response.source) : null;
}

export async function createSource(payload: SourcePayload): Promise<Source> {
  const slug = payload.slug || slugify(payload.name);
  const body = {
    ...payload,
    slug,
    url_base: payload.endpoint || payload.url_base || '',
    endpoint: undefined,
    themes: payload.themes ?? [],
    info_types: payload.info_types ?? [],
    refresh_interval: payload.refresh_interval ?? null,
  };

  const response = await httpClient<{ source: Source }>(endpoints.admin.sources, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  return normalizeSource(response.source);
}

export async function updateSource(id: string, payload: SourcePayload): Promise<Source> {
  const body = {
    ...payload,
    url_base: payload.endpoint || payload.url_base,
    endpoint: undefined,
  };
  const response = await httpClient<{ source: Source }>(endpoints.admin.sourceDetail(id), {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  return normalizeSource(response.source);
}

async function changeSourceState(id: string, target_state: SourceStatus, reason: string): Promise<Source> {
  const response = await httpClient<{ source: Source }>(`${endpoints.admin.sourceDetail(id)}/status`, {
    method: 'POST',
    body: JSON.stringify({ target_state, reason, changed_by: 'admin-ui' }),
  });
  return normalizeSource(response.source);
}

export async function activateSource(id: string): Promise<Source> {
  return changeSourceState(id, 'ACTIVE', 'Ativação via Console de Fontes');
}

export async function deactivateSource(id: string): Promise<Source> {
  return changeSourceState(id, 'DISABLED_TEMP', 'Pausa via Console de Fontes');
}

export async function archiveSource(id: string): Promise<Source> {
  return changeSourceState(id, 'DISABLED_PERM', 'Arquivamento via Console de Fontes');
}

export async function triggerManualRun(id: string): Promise<{ run_id: string; status: string }> {
  return httpClient<{ run_id: string; status: string }>(`${endpoints.admin.sourceDetail(id)}/ingestion/run`, { method: 'POST' });
}

export async function pauseIngestion(id: string): Promise<void> {
  await httpClient(`${endpoints.admin.sourceDetail(id)}/ingestion/pause`, { method: 'POST' });
}

export async function resumeIngestion(id: string): Promise<void> {
  await httpClient(`${endpoints.admin.sourceDetail(id)}/ingestion/resume`, { method: 'POST' });
}
