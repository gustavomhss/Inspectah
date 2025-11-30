import type { AdminSource, AdminSourceDetail, AdminSourceState, AdminSourceHealthStatus } from '@/core/api/api-types';

export type SourceStatus = AdminSourceState;
export type SourceHealth = AdminSourceHealthStatus | 'unknown';

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
  health_status?: SourceHealth | null;
  health_reason?: string | null;
  last_run_status?: string | null;
  last_run_finished_at?: string | null;
  last_run_latency_ms?: number | null;
  last_run_items?: number | null;
  failure_streak?: number;
  recent_items_count?: number;
  ingestion_mode?: string | null;
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
  auth_type?: string;
  auth_config?: Record<string, unknown>;
}

export interface SourceFilters {
  type?: string;
  category?: string;
  state?: SourceStatus;
  health_status?: SourceHealth;
  search?: string;
}

export type SourceSummary = AdminSource & { slug?: string; url_base?: string };
