export type FlowState = 'draft' | 'em_teste' | 'ativo' | 'pausado' | 'deprecado';
export type FlowStepType = 'interprete' | 'classificador' | 'analista' | 'debunker' | 'decision_maker';
export type FlowExecutionStatus = 'em_andamento' | 'concluido' | 'falhou' | 'cancelado';
export type FlowStepExecutionStatus = 'pendente' | 'ok' | 'erro' | 'skipped';

export interface FlowStep {
  id: string;
  flow_id: string;
  ordem: number;
  tipo_etapa: FlowStepType;
  agent_role: string;
  agent_binding?: string | null;
  config?: Record<string, unknown>;
  flags?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface Flow {
  id: string;
  nome: string;
  slug: string;
  tipo_entrada: string;
  estado: FlowState;
  domain?: string;
  flow_version_id?: string | null;
  active_version_id?: string | null;
  test_version_id?: string | null;
  rollout_mode?: string | null;
  rollout_state?: string | null;
  rollout_started_at?: string | null;
  rollout_criteria?: Record<string, unknown>;
  catalog_hash?: string | null;
  catalog_signature?: string | null;
  flow_ops_profile_id?: string | null;
  template_origem_id?: string | null;
  percentual_teste?: number;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
  steps?: FlowStep[];
}

export interface FlowVersion {
  id: string;
  flow_id: string;
  version_id: string;
  template_slug: string;
  estado: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface FlowOperation {
  id: string;
  flow_id: string;
  flow_version_id?: string | null;
  operacao: string;
  payload?: Record<string, unknown>;
  resultado: string;
  mode?: string | null;
  actor?: string | null;
  catalog_hash?: string | null;
  operation_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface FlowTemplate {
  id: string;
  slug: string;
  versao: string;
  tipo_entrada: string;
  domain?: string;
  description?: string;
  estrutura: Record<string, unknown>;
  ativo?: boolean;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface FlowExecution {
  id: string;
  flow_id: string;
  flow_version_id?: string | null;
  mode?: string | null;
  operation_id?: string | null;
  item_id: string;
  tipo_entrada: string;
  status: FlowExecutionStatus;
  started_at: string;
  finished_at?: string | null;
  erro_resumo?: string | null;
  metadata?: Record<string, unknown>;
}

export interface FlowStepExecution {
  id: string;
  flow_execution_id: string;
  step_id: string;
  status: FlowStepExecutionStatus;
  started_at: string;
  finished_at?: string | null;
  output_resumo?: string | null;
  erro_resumo?: string | null;
  raw_ref?: string | null;
}

export interface FlowExecutionDetail extends FlowExecution {
  steps: FlowStepExecution[];
}

export interface FlowCreatePayload {
  template_slug: string;
  nome: string;
  slug: string;
  bindings: Record<string, string>;
  metadata?: Record<string, unknown>;
  percentual_teste?: number;
}

export interface FlowUpdateStatePayload {
  novo_estado: FlowState;
  percentual_teste?: number | null;
}

export interface FlowReplaceAgentPayload {
  step_id: string;
  agent_binding: string;
}

export interface FlowReprocessPayload {
  criteria: {
    item_ids: string[];
    max_items?: number;
    janela_horas?: number;
  };
  motivo?: string;
}

export interface FlowCatalogEntry {
  flow_id: string;
  domain?: string;
  version?: string;
  flow_version_id?: string | null;
  template_ref?: string;
  policies?: Record<string, unknown>;
  rollout_defaults?: Record<string, unknown>;
  hash?: string;
  signature?: string;
}

export interface FlowRolloutStatus {
  flow_id: string;
  flow_version_id?: string | null;
  active_version_id?: string | null;
  test_version_id?: string | null;
  rollout_mode?: string | null;
  rollout_state?: string | null;
  operation_id?: string | null;
  catalog_hash?: string | null;
  catalog_signature?: string | null;
  rollout_started_at?: string | null;
  rollout_criteria?: Record<string, unknown>;
  alerts?: string[];
  policy_violations?: string[];
}

export interface NewsdataItem {
  id: string;
  title: string;
  link: string;
  pubDate: string;
  source_id: string;
  category?: string[];
  description?: string;
  hash?: string;
}

export interface NewsdataRun {
  run_id: string;
  status: string;
  items_processed: number;
  payload_ref?: string | null;
  meta?: {
    fetched?: number;
    deduped?: number;
    duplicates?: number;
    throttle_seconds?: number;
    max_attempts?: number;
    items_sample?: NewsdataItem[];
    duration_seconds?: number;
  };
}
