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
  template_origem_id?: string | null;
  percentual_teste?: number;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
  steps?: FlowStep[];
}

export interface FlowTemplate {
  id: string;
  slug: string;
  versao: string;
  tipo_entrada: string;
  estrutura: Record<string, unknown>;
  ativo?: boolean;
  metadata?: Record<string, unknown>;
}

export interface FlowExecution {
  id: string;
  flow_id: string;
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
