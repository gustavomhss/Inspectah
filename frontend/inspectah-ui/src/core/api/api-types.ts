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

export type AdminSourceType =
  | 'news_rss'
  | 'gossip_feed'
  | 'sports_api'
  | 'weather_api'
  | 'official_open'
  | 'data_api'
  | string;

export interface AdminSource {
  id: string;
  slug?: string;
  name: string;
  type: AdminSourceType;
  provider_id?: string | null;
  provider_kind?: string | null;
  derived_from?: string | null;
  meta?: Record<string, unknown>;
  category?: string;
  state: AdminSourceState;
  ingestion_mode?: IngestionMode | null;
  state_reason?: string | null;
  refresh_interval?: number | null;
  last_health_status?: AdminSourceHealthStatus | null;
  last_health_at?: string | null;
  last_health_error?: string | null;
  endpoint?: string;
  url_base?: string;
  themes?: string[];
  info_types?: string[];
  description?: string;
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

export type CopilotoActionType =
  | 'set_field'
  | 'clear_field'
  | 'mark_suggested'
  | 'propose_update'
  | 'plan_status_change'
  | 'SET_FIELD'
  | 'SUGGEST_FIELD'
  | 'CLEAR_FIELD'
  | 'FOCUS_FIELD'
  | 'PROPOSE_UPDATE'
  | 'PLAN_STATUS';

export interface CopilotoAction {
  type: CopilotoActionType;
  field?: string;
  value?: unknown;
  changes?: Array<{ field: string; from: unknown; to: unknown }>;
  plan?: { from_state: string; to_state: string; reason?: string };
}

export interface CopilotoMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface CopilotoSessionResponse {
  session_id: string;
  agent_mode?: boolean;
  source_id?: string | null;
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

// Ingestão 2.0 (Sprint 22)
export type IngestionMode = 'MANUAL_ONLY' | 'AUTOMATIC' | 'DERIVED';
export type IngestionStatus = 'PENDING' | 'RUNNING' | 'SUCCESS' | 'PARTIAL_SUCCESS' | 'FAIL';

export interface IngestionConfig {
  id: string;
  source_id: string;
  enabled: boolean;
  mode: IngestionMode;
  interval_minutes: number;
  max_attempts: number;
  timeout_seconds: number;
  last_run_id?: string | null;
  updated_at: string;
}

export interface IngestionRun {
  id: string;
  source_id: string;
  status: IngestionStatus;
  trigger: string;
  started_at: string;
  finished_at?: string | null;
  items_processed?: number;
  error_code?: string | null;
  error_message?: string | null;
  payload_ref?: string | null;
  meta?: Record<string, unknown>;
}

export interface IngestionRunsResponse {
  runs: IngestionRun[];
  pagination?: { limit?: number; offset?: number; count?: number };
  config_mode?: IngestionMode | null;
}

export interface TriggerRunResponse {
  run_id: string;
  status: IngestionStatus;
  trigger: string;
}

// Sprint 23 — Agents & Committees
export type AgentLayer = 'interpretation' | 'classification' | 'debunk';
export type AgentRole = 'interpreter' | 'classifier' | 'analyst' | 'debunker' | 'decision_maker' | 'librarian';
export type AgentStatus = 'active' | 'paused' | 'deprecated';
export type AgentRunStatus = 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAIL' | 'CANCELLED';

export interface AgentKBRef {
  id: string;
  kind: string;
  label: string;
  path_or_uri: string;
}

export interface AgentProfile {
  id: string;
  name: string;
  description: string;
  instructions: string;
  role: AgentRole;
  layer: AgentLayer;
  model_name?: string | null;
  recommended_model_name?: string | null;
  temperature: number;
  max_tokens: number;
  top_p: number;
  status: AgentStatus;
  kb_refs: AgentKBRef[];
  created_at: string;
  updated_at: string;
  created_by?: string | null;
  last_modified_by?: string | null;
}

export interface AgentInstructionVersion {
  id: string;
  agent_id: string;
  version_number: number;
  instructions?: string | null;
  model_name?: string | null;
  temperature?: number | null;
  max_tokens?: number | null;
  top_p?: number | null;
  kb_snapshot: AgentKBRef[];
  changelog: string;
  created_at: string;
  created_by?: string | null;
}

export interface CommitteePolicy {
  required_agreement_ratio: number;
  max_disagreement_tolerance: number;
  resolve_ties_strategy: string;
}

export interface AgentCommittee {
  id: string;
  name: string;
  description: string;
  layer: AgentLayer;
  primary_agents: string[];
  mediator_agent: string;
  policy: CommitteePolicy;
  status: AgentStatus;
  created_at: string;
  updated_at: string;
}

export interface ModelUpgradePolicy {
  global_default_model: string;
  auto_upgrade_enabled: boolean;
  adoption_delay_days: number;
  allowed_models: string[];
  last_upgrade_at?: string | null;
  next_upgrade_at?: string | null;
  updated_at: string;
}

export interface AgentRun {
  id: string;
  committee_id: string;
  input_ref?: string | null;
  payload_snapshot: Record<string, unknown>;
  result_bundle_ref?: string | null;
  status: AgentRunStatus;
  error?: string | null;
  started_at: string;
  finished_at?: string | null;
  created_at: string;
}

// Flow layers
export type FlowLayerType =
  | 'interpretation_layer'
  | 'classification_layer'
  | 'intermediate_layer'
  | 'decision_maker_layer'
  | 'librarian_layer';

export interface AgentFlowLayer {
  id: string;
  name: string;
  description: string;
  layer_type: FlowLayerType;
  layer_index: number;
  agent_ids: string[];
  mediator_agent_id: string;
  created_at: string;
  updated_at: string;
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

// Agent Tracing types
export interface AgentTrace {
  id: string;
  claim_id?: string | null;
  risk_level?: string | null;
  steps_count?: number | null;
  steps_json?: string | null;
  created_at?: string;
  duration_ms?: number;
  status?: string;
}
