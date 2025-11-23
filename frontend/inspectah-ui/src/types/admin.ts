export type AdminSourceStatus = 'healthy' | 'degraded' | 'unknown';

export interface AdminSource {
  id: string;
  name: string;
  type: string;
  info_type?: string;
  is_active: boolean;
  status: AdminSourceStatus;
  last_checked_at?: string | null;
  last_error?: string | null;
  recent_items_count: number;
  url_base?: string;
}

export interface AdminSourceDetail extends AdminSource {
  history: Array<{
    checked_at?: string | null;
    status: AdminSourceStatus;
    error?: string | null;
  }>;
}

export interface AdminCase {
  id: string;
  title: string;
  category: string;
  status: string;
  risk?: string | null;
  updated_at?: string | null;
  key_sources: string[];
}

export interface AdminCaseDetail extends AdminCase {
  description: string;
  top_evidence: Array<Record<string, unknown>>;
}

export interface AdminHealth {
  sources_total: number;
  sources_healthy: number;
  sources_degraded: number;
  cases_total: number;
  cases_attention: number;
  cases_stable: number;
  integrations: Record<string, string>;
}
