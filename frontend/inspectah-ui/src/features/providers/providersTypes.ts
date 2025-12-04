export type ProviderStatus = 'active' | 'inactive' | 'paused';
export type ProviderKind = 'news_provider' | 'social_provider';
export type ProfileKind = 'news' | 'social';

export interface Provider {
  id: string;
  name: string;
  kind: ProviderKind;
  description: string;
  status: ProviderStatus;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  limits?: Record<string, unknown>;
}

export interface IngestionProfile {
  id: string;
  provider_id: string;
  name: string;
  slug: string;
  kind: ProfileKind;
  country?: string | null;
  language?: string | null;
  categories?: string[];
  keywords?: string[];
  filters?: Record<string, unknown>;
  frequency_minutes: number;
  budget_daily_calls?: number | null;
  budget_monthly_calls?: number | null;
  enabled: boolean;
  status: ProviderStatus;
  metadata?: Record<string, unknown>;
  created_by?: string;
  updated_by?: string;
}

export interface ProfileRun {
  run_id: string;
  provider_id: string;
  profile_id: string;
  started_at: string;
  finished_at: string;
  status: string;
  items: number;
  persisted: number;
  calls: number;
  evidence_path?: string | null;
  message?: string | null;
}

export interface ProfileMetrics {
  total_runs: number;
  success: number;
  fail: number;
  last_run_at?: string | null;
  items: number;
  persisted: number;
}

export interface ProviderDetail {
  provider: Provider;
  profiles: { profile: IngestionProfile; metrics: ProfileMetrics; last_run?: ProfileRun | null }[];
}

export interface ProfileDetail {
  profile: IngestionProfile;
  runs: ProfileRun[];
  metrics: ProfileMetrics;
}
