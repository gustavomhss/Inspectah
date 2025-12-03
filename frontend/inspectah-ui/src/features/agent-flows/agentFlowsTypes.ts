export type AgentRoleOption =
  | 'interpreter'
  | 'classifier'
  | 'analyst'
  | 'debunker'
  | 'decision_maker'
  | 'mediator'
  | 'librarian';

export interface AgentFlowStepBase {
  position: number;
  agent_role: AgentRoleOption;
  params?: Record<string, unknown>;
  required?: boolean;
  can_fail_soft?: boolean;
}

export interface AgentFlowStep extends AgentFlowStepBase {
  id: string;
  flow_id: string;
  created_at?: string;
  updated_at?: string;
}

export interface AgentFlowStepForm extends AgentFlowStepBase {
  id?: string;
}

export interface AgentFlowConfigBase {
  domain_key: string;
  name?: string | null;
  description?: string | null;
  is_active?: boolean;
  change_reason?: string | null;
  created_by?: string | null;
  updated_by?: string | null;
}

export interface AgentFlowConfig extends AgentFlowConfigBase {
  id: string;
  created_at?: string;
  updated_at?: string;
  steps: AgentFlowStep[];
}

export interface AgentFlowConfigForm extends AgentFlowConfigBase {
  id?: string;
  steps: AgentFlowStepForm[];
}

export interface AgentFlowError {
  errors: string[];
}
