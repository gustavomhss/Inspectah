/**
 * Guardian Types — S37
 */

export interface GuardianDecision {
  id: string;
  claim_id: string;
  claim_summary: string | null;  // Human-readable: "O que está sendo decidido?"
  evidence_summary: string[] | null;  // Evidências que ancoram a claim
  domain: string;
  gate: string;
  proposed_state: string;
  status: string;
  policy_name: string | null;
  committee_id: string | null;
  final_state: string | null;
  final_reason: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface GuardianFlowContext {
  decision: GuardianDecision;
  current_state: string;
  transitions: FlowTransition[];
  elapsed_ms: number;
  policy_result: PolicyResult | null;
  invariants: Record<string, boolean> | null;
  error: string | null;
}

export interface FlowTransition {
  from_state: string;
  to_state: string;
  event: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface PolicyResult {
  policy_name: string;
  final_action: string | null;
  all_requirements_met: boolean;
}

export interface GuardianCommittee {
  id: string;
  decision_id: string;
  member_count: number;
  vote_count: number;
  quorum_required: number;
  has_quorum: boolean;
  vote_counts: Record<string, number>;
}

export interface DecisionBlock {
  id: string;
  decision_id: string;
  claim_id: string;
  domain: string;
  gate: string;
  initial_state: string;
  final_state: string;
  decision_type: string;
  policy_name: string | null;
  policy_version: string | null;
  committee_summary: Record<string, unknown> | null;
  invariants_checked: Record<string, boolean>;
  evidence_refs: string[];
  created_at: string;
  latency_ms: number | null;
}

export interface ReviewQueueItem {
  id: string;
  decision_id: string;
  claim_id: string;
  domain: string;
  gate: string;
  proposed_state: string;
  priority: string;
  status: string;
  reason: string | null;
  context_summary: Record<string, unknown>;
  assigned_to: string | null;
  assigned_at: string | null;
  created_at: string;
  expires_at: string | null;
}

export interface ReviewQueueStats {
  total_items: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_domain: Record<string, number>;
  total_reviewers: number;
  total_submissions: number;
}

export interface GuardianMetrics {
  decisions_submitted: number;
  decisions_approved: number;
  decisions_rejected: number;
  decisions_timed_out: number;
  avg_latency_ms: number;
  pending_decisions: number;
  awaiting_review: number;
  awaiting_quorum: number;
}

export interface GuardianPolicy {
  name: string;
  domain: string;
  gate: string;
  version: string;
  requirements: number;
  rules: number;
}

export interface PolicyRequirement {
  field: string;
  operator: string;
  value: string | number | boolean;
  modifier: string | null;
}

export interface PolicyRule {
  condition_field: string;
  condition_operator: string;
  condition_value: string | number | boolean;
  action: string;
  action_params: Record<string, unknown>;
}

export interface PolicyDetail {
  name: string;
  domain: string;
  gate: string;
  version: string;
  requirements: PolicyRequirement[];
  rules: PolicyRule[];
  metadata: Record<string, unknown>;
}

export type DecisionStatus =
  | 'pending'
  | 'validating'
  | 'awaiting_review'
  | 'awaiting_quorum'
  | 'approved'
  | 'rejected'
  | 'escalated'
  | 'timed_out'
  | 'cancelled';

export type ReviewPriority = 'urgent' | 'high' | 'normal' | 'low';

export type ReviewStatus = 'queued' | 'assigned' | 'in_progress' | 'completed' | 'expired' | 'cancelled';
