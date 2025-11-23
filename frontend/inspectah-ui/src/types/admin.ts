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

export type TimelineSeverity = 'info' | 'warning' | 'critical' | string;

export interface AdminTimelineEvent {
  id: string;
  case_id: string;
  timestamp: string;
  event_type: string;
  severity?: TimelineSeverity | null;
  source?: string | null;
  summary: string;
}

export interface AdminTimelineResponse {
  case_id: string;
  events: AdminTimelineEvent[];
}

export interface AdminDebunkerSection {
  risk_level?: string | null;
  explanation: string;
  flags: string[];
  last_evaluated_at?: string | null;
}

export interface AdminCommitteeDecision {
  name: string;
  verdict: string;
  confidence?: string | null;
  rationale?: string | null;
  decided_at?: string | null;
}

export interface AdminCommitteesSection {
  summary: string;
  decisions: AdminCommitteeDecision[];
}

export interface AdminAnchorSummary {
  name: string;
  status: string;
  last_check?: string | null;
  reliability?: string | null;
  issues: string[];
}

export interface AdminAnchorsSection {
  summary: string;
  anchors: AdminAnchorSummary[];
}

export interface AdminEvidenceSummary {
  id: string;
  type: string;
  source?: string | null;
  title?: string | null;
  snippet?: string | null;
  url?: string | null;
  captured_at?: string | null;
}

export interface AdminEvidenceSection {
  summary: string;
  evidences: AdminEvidenceSummary[];
}

export interface AdminCaseXRay {
  case_id: string;
  title: string;
  category?: string | null;
  status: string;
  risk?: string | null;
  summary: string;
  debunker: AdminDebunkerSection;
  committees: AdminCommitteesSection;
  anchors: AdminAnchorsSection;
  evidences: AdminEvidenceSection;
}
