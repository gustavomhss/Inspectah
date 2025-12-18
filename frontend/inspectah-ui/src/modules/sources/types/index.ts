/**
 * S38-FE-010: Types para o modulo Sources
 */

export type SourceType = 'official' | 'scraper' | 'rss' | 'api';

export type SourceState =
  | 'PROPOSED'
  | 'TESTING'
  | 'ACTIVE'
  | 'UNDER_REVIEW'
  | 'SUSPECT'
  | 'DISABLED_TEMP'
  | 'DISABLED_PERM';

export type HealthStatus = 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY' | 'UNKNOWN';

export interface Source {
  id: string;
  name: string;
  slug: string;
  source_type: SourceType;
  url: string;
  description?: string;
  config: Record<string, unknown>;
  rate_limit_rpm: number;
  enabled: boolean;
  state: SourceState;
  last_health_status: HealthStatus;
  last_health_check?: string;
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface SourceDetail extends Source {
  health_stats?: HealthStats;
  rate_limit_stats?: RateLimitStats;
  circuit_breaker_stats?: CircuitBreakerStats;
  recent_runs: IngestionRun[];
}

export interface HealthStats {
  source_id: string;
  status: string;
  consecutive_successes: number;
  consecutive_failures: number;
  last_check?: string;
  last_success?: string;
  last_failure?: string;
  avg_latency_ms: number;
  total_checks: number;
  total_failures: number;
  uptime_percent: number;
  error_message?: string;
}

export interface RateLimitStats {
  source_id: string;
  tokens_available: number;
  burst_size: number;
  requests_per_minute: number;
  requests_this_window: number;
  enabled: boolean;
}

export interface CircuitBreakerStats {
  source_id: string;
  state: 'closed' | 'open' | 'half_open';
  failure_count: number;
  success_count: number;
  total_requests: number;
  total_failures: number;
  total_successes: number;
  failure_threshold: number;
  last_failure_time?: number;
  last_success_time?: number;
}

export interface IngestionRun {
  run_id: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  trigger: 'MANUAL' | 'SCHEDULED' | 'WEBHOOK';
  started_at: string;
  finished_at?: string;
  documents_processed: number;
  error_message?: string;
  duration_seconds?: number;
}

export interface SourceMetrics {
  source_id: string;
  period: '1h' | '24h' | '7d';
  total_documents: number;
  documents_per_hour: number;
  avg_latency_ms: number;
  success_rate: number;
  error_count: number;
  last_ingestion?: string;
}

export interface DryRunResult {
  success: boolean;
  source_id: string;
  documents_found: number;
  sample_documents: Record<string, unknown>[];
  latency_ms: number;
  error_message?: string;
}

export interface SourceFormData {
  name: string;
  slug: string;
  source_type: SourceType;
  url: string;
  description?: string;
  config?: Record<string, unknown>;
  rate_limit_rpm: number;
  enabled: boolean;
}
