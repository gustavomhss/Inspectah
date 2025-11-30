import type { AdminSource, AdminSourceDetail, AdminSourceState } from '@/core/api/api-types';

export type SourceStatus = AdminSourceState;
export type Source = AdminSourceDetail & {
  slug?: string;
  url_base?: string;
  created_at?: string;
  updated_at?: string;
  createdAt?: string;
  updatedAt?: string;
  state_updated_at?: string;
  stateUpdatedAt?: string;
  state_reason?: string | null;
};

export interface SourcePayload {
  slug?: string;
  name: string;
  type: string;
  category: string;
  state?: SourceStatus;
  description?: string;
  endpoint?: string;
  themes?: string[];
  info_types?: string[];
  refresh_interval?: number | null;
  url_base?: string;
}

export interface SourceFilters {
  type?: string;
  category?: string;
  state?: SourceStatus;
  search?: string;
}

export type SourceSummary = AdminSource & { slug?: string; url_base?: string };
