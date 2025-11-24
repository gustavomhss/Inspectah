export type RiskLevel = 'low' | 'medium' | 'high' | 'unknown';

export interface EvidenceItemUi {
  id: string;
  sourceName: string;
  sourceType: string;
  description: string;
  link?: string;
  credibility?: string;
}

export interface ConsultationRequest {
  question: string;
  locale?: string;
  context?: string;
}

export interface EvidenceItemRaw {
  id?: string;
  source_name?: string;
  source?: string;
  source_type?: string;
  type?: string;
  description?: string;
  summary?: string;
  link?: string;
  credibility?: string;
}

export interface ConsultationResponseRaw {
  answer?: string;
  answer_text?: string;
  risk_level?: RiskLevel | string;
  risk_score?: number;
  risk_flags?: string[];
  confidence?: {
    level?: string;
    score?: number;
    reasons?: string[];
  };
  evidences?: EvidenceItemRaw[];
  evidence?: {
    items_preview?: EvidenceItemRaw[];
    sources?: EvidenceItemRaw[];
  };
  request_id?: string;
  generated_at?: string;
  summary_card?: {
    risk_level?: RiskLevel | string;
    confidence_level?: string;
    confidence_score?: number;
    limitations?: string[];
  };
}

export interface ConsultationResponseUi {
  answer: string;
  riskLevel: RiskLevel;
  riskScore?: number;
  riskFlags?: string[];
  truthState?: string | null;
  evidences: EvidenceItemUi[];
  requestId?: string;
  generatedAt?: string;
}

export type ConsultationStatus =
  | { kind: 'idle' }
  | { kind: 'submitting'; question: string }
  | { kind: 'success'; question: string; result: ConsultationResponseUi }
  | { kind: 'error'; question?: string; message: string };

// Admin API types
export type AdminSourceHealthStatus = 'OK' | 'DEGRADED' | 'FAIL' | 'unknown';
export type AdminSourceState =
  | 'PROPOSED'
  | 'TESTING'
  | 'ACTIVE'
  | 'UNDER_REVIEW'
  | 'SUSPECT'
  | 'DISABLED_TEMP'
  | 'DISABLED_PERM';

export interface AdminSource {
  id: string;
  name: string;
  type: string;
  info_type?: string;
  category?: string;
  state: AdminSourceState;
  last_health_status?: AdminSourceHealthStatus | null;
  last_health_at?: string | null;
  last_health_error?: string | null;
  url_base?: string;
  themes?: string[];
  info_types?: string[];
}

export interface AdminSourceDetail extends AdminSource {
  state_history?: Array<{
    created_at?: string | null;
    from_state?: string | null;
    to_state: string;
    reason?: string | null;
  }>;
  healthchecks?: Array<{
    checked_at?: string | null;
    status: AdminSourceHealthStatus;
    error?: string | null;
    latency_ms?: number | null;
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
