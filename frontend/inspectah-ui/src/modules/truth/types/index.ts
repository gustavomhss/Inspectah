/**
 * S40-FE-007: Truth Twin TypeScript Types
 *
 * Types matching backend schemas from app/api/truth_schemas.py
 */

// ===== Claim States =====
export type TruthState =
  | 'UNKNOWN'
  | 'CLAIMED'
  | 'UNDER_REVIEW'
  | 'PROVISIONAL'
  | 'ESTABLISHED_FACT'
  | 'UNDER_DISPUTE'
  | 'RETRACTED'
  | 'PENDING'
  | 'PROMOTED'
  | 'CONTESTABLE'
  | 'REJECTED'
  | 'BLOCKED'
  | 'DEGRADED'
  | 'unknown';

// ===== Decision Types =====
export type DecisionType =
  | 'APPROVE'
  | 'REJECT'
  | 'ESCALATE'
  | 'BLOCK'
  | 'DEGRADE'
  | 'PROMOTE';

// ===== Gate Types =====
export type GateType =
  | 'G0'
  | 'G1'
  | 'G2'
  | 'G3'
  | 'G4'
  | 'NOGO'
  | string;

// ===== Provenance Info =====
export interface ProvenanceInfo {
  source: string;
  timestamp: string;
  policy_version?: string | null;
  policy_name?: string | null;
  actor?: string | null;
  evidence_refs: string[];
  references?: Record<string, unknown> | null;
}

// ===== State Transition Info =====
export interface StateTransitionInfo {
  from_state: string;
  to_state: string;
  reason: string;
  timestamp: string;
  decision_id?: string | null;
}

// ===== Decision Block Summary =====
export interface DecisionBlockSummary {
  id: string;
  decision_id: string;
  gate: string;
  decision_type: string;
  initial_state: string;
  final_state: string;
  created_at: string;
  latency_ms?: number | null;
  policy_name?: string | null;
  policy_version?: string | null;
}

// ===== Committee Summary =====
export interface CommitteeSummary {
  // S40 fields
  decision?: string;
  confidence?: number;
  notes?: string;
  reviewers?: string[];
  // Legacy fields
  total_votes?: number;
  approve_votes?: number;
  reject_votes?: number;
  consensus?: string;
  quorum_reached?: boolean;
  members?: string[];
  [key: string]: unknown;
}

// ===== Invariants Checked =====
export interface InvariantsChecked {
  [invariant_name: string]: boolean | null;
}

// ===== References (S40 - guias, pilares, e40_5) =====
export interface References {
  guias?: Array<{ guia: string; documento: string; versao: string }> | string[];
  pilares?: Array<{ pilar: string; documento: string; versao: string }> | string[];
  e40_5?: {
    status: 'OK' | 'PASS' | 'VIOLATED' | 'FAIL' | 'SKIPPED' | string;
    message?: string | null;
  };
  [key: string]: unknown;
}

// ===== Truth Twin Response =====
export interface TruthTwinResponse {
  claim_id: string;
  slug?: string | null;
  headline?: string | null;
  claim_text?: string | null;  // Full claim text for display
  domain: string;
  current_state: TruthState | string;
  created_at: string;
  updated_at: string;
  decision_timeline: DecisionBlockSummary[];
  provenance?: ProvenanceInfo | null;
  state_history: StateTransitionInfo[];
  metadata: Record<string, unknown>;
  experience_refs: string[];
  last_decision_id?: string | null;
  _latency_ms?: number;
  _provenance_valid?: boolean;
}

// ===== Decision Inspect Response =====
export interface DecisionInspectResponse {
  decision_id: string;
  block_id: string;
  claim_id: string;
  domain: string;
  gate: string;
  decision_type: string;
  initial_state: string;
  final_state: string;
  policy_name?: string | null;
  policy_version?: string | null;
  committee_summary: CommitteeSummary;
  invariants_checked: InvariantsChecked;
  evidence_refs: string[];
  references?: References | null;
  state_transition?: StateTransitionInfo | null;
  experience_refs: string[];
  created_at: string;
  latency_ms?: number | null;
  provenance?: ProvenanceInfo | null;
  _latency_ms?: number;
  _provenance_valid?: boolean;
}

// ===== Timeline Response =====
export interface TimelineResponse {
  claim_id: string;
  timeline: DecisionBlockSummary[];
  count: number;
  limit: number;
  _latency_ms?: number;
}

// ===== API Error Response =====
export interface TruthApiError {
  detail: string;
  status_code?: number;
}

// ===== UI State Types =====
export interface TruthTwinLoadingState {
  isLoading: boolean;
  error?: TruthApiError | null;
  data?: TruthTwinResponse | null;
}

export interface DecisionInspectLoadingState {
  isLoading: boolean;
  error?: TruthApiError | null;
  data?: DecisionInspectResponse | null;
}

// ===== Badge Variants =====
export type StateBadgeVariant =
  | 'success'  // PROMOTED
  | 'warning'  // UNDER_REVIEW, CONTESTABLE
  | 'danger'   // REJECTED, BLOCKED
  | 'info'     // PENDING
  | 'default'; // DEGRADED, unknown

// ===== Helper type for state to variant mapping =====
export const STATE_BADGE_MAP: Record<TruthState, StateBadgeVariant> = {
  UNKNOWN: 'default',
  CLAIMED: 'info',
  UNDER_REVIEW: 'warning',
  PROVISIONAL: 'warning',
  ESTABLISHED_FACT: 'success',
  UNDER_DISPUTE: 'warning',
  RETRACTED: 'danger',
  PENDING: 'info',
  PROMOTED: 'success',
  CONTESTABLE: 'warning',
  REJECTED: 'danger',
  BLOCKED: 'danger',
  DEGRADED: 'default',
  unknown: 'default',
};

// ===== Decision type to variant mapping =====
export const DECISION_BADGE_MAP: Record<DecisionType, StateBadgeVariant> = {
  APPROVE: 'success',
  REJECT: 'danger',
  ESCALATE: 'warning',
  BLOCK: 'danger',
  DEGRADE: 'default',
  PROMOTE: 'success',
};

// ===== Gate to variant mapping =====
export const GATE_BADGE_MAP: Record<string, StateBadgeVariant> = {
  G0: 'info',
  G1: 'info',
  G2: 'warning',
  G3: 'warning',
  G4: 'success',
  NOGO: 'danger',
};

// ===== Filter Types =====
export interface TimelineFilters {
  gates?: GateType[];
  decision_types?: DecisionType[];
  states?: TruthState[];
  date_from?: string;
  date_to?: string;
}

// ===== Pagination =====
export interface PaginationParams {
  limit?: number;
  offset?: number;
}

// ===== Sort Options =====
export type SortDirection = 'asc' | 'desc';

export interface SortParams {
  field: string;
  direction: SortDirection;
}

// ===== Hook Return Types =====
export interface UseTruthTwinResult {
  data: TruthTwinResponse | null;
  isLoading: boolean;
  error: TruthApiError | null;
  refetch: () => Promise<void>;
}

export interface UseDecisionInspectResult {
  data: DecisionInspectResponse | null;
  isLoading: boolean;
  error: TruthApiError | null;
  refetch: () => Promise<void>;
}

// ===== Component Props Types =====
export interface StatusBadgeProps {
  state: TruthState | string;
  size?: 'sm' | 'md' | 'lg';
  showDot?: boolean;
}

export interface DecisionTimelineProps {
  decisions: DecisionBlockSummary[];
  onDecisionClick?: (decision: DecisionBlockSummary) => void;
  filters?: TimelineFilters;
  isLoading?: boolean;
}

export interface ProvenancePanelProps {
  provenance: ProvenanceInfo | null | undefined;
  showDetails?: boolean;
}

export interface DecisionInspectorProps {
  decisionId: string;
  onClose?: () => void;
}

// ===== Utility Types =====
export type WithLatency<T> = T & { _latency_ms?: number };
export type WithProvenance<T> = T & { _provenance_valid?: boolean };
