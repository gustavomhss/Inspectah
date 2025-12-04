import { endpoints } from '@/core/api/endpoints';
import { httpClient } from '@/core/api/http-client';
import type {
  IngestionProfile,
  ProfileDetail,
  ProfileMetrics,
  ProfileRun,
  Provider,
  ProviderDetail,
} from './providersTypes';

export async function fetchProviders(params: Record<string, string | undefined> = {}, authToken?: string): Promise<Provider[]> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v) query.append(k, v);
  });
  const url = `${endpoints.admin.providers.list}${query.toString() ? `?${query.toString()}` : ''}`;
  return httpClient<Provider[]>(url, { authToken });
}

export async function fetchProviderDetail(providerId: string, authToken?: string): Promise<ProviderDetail> {
  return httpClient<ProviderDetail>(endpoints.admin.providers.detail(providerId), { authToken });
}

export async function saveProvider(payload: Provider, authToken?: string, opts: { isNew?: boolean } = {}): Promise<Provider> {
  const isNew = opts.isNew ?? !payload.id;
  const url = isNew ? endpoints.admin.providers.list : endpoints.admin.providers.detail(payload.id);
  const method = isNew ? 'POST' : 'PUT';
  return httpClient<Provider>(url, { method, body: JSON.stringify(payload), authToken });
}

export async function fetchProfiles(
  params: Record<string, string | undefined> = {},
  authToken?: string,
): Promise<IngestionProfile[]> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v) query.append(k, v);
  });
  const url = `${endpoints.admin.providers.profiles}${query.toString() ? `?${query.toString()}` : ''}`;
  return httpClient<IngestionProfile[]>(url, { authToken });
}

export async function fetchProfileDetail(profileId: string, authToken?: string): Promise<ProfileDetail> {
  return httpClient<ProfileDetail>(endpoints.admin.providers.profileDetail(profileId), { authToken });
}

export async function saveProfile(
  payload: IngestionProfile,
  authToken?: string,
  opts: { isNew?: boolean } = {},
): Promise<IngestionProfile> {
  const isNew = opts.isNew ?? !payload.id;
  const url = isNew ? endpoints.admin.providers.profiles : endpoints.admin.providers.profileDetail(payload.id);
  const method = isNew ? 'POST' : 'PUT';
  return httpClient<IngestionProfile>(url, { method, body: JSON.stringify(payload), authToken });
}

export async function runProfile(profileId: string, authToken?: string, limit = 3): Promise<{ run: ProfileRun }> {
  const url = `${endpoints.admin.providers.profileRunNow(profileId)}?limit=${limit}`;
  return httpClient<{ status: string; run: ProfileRun }>(url, { method: 'POST', authToken });
}

export async function fetchProfileRuns(profileId: string, authToken?: string): Promise<ProfileRun[]> {
  return httpClient<ProfileRun[]>(endpoints.admin.providers.profileRuns(profileId), { authToken });
}

export async function fetchProfileMetrics(profileId: string, authToken?: string): Promise<ProfileMetrics> {
  return httpClient<ProfileMetrics>(endpoints.admin.providers.profileMetrics(profileId), { authToken });
}
