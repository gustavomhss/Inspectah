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
  evidences: EvidenceItemUi[];
  requestId?: string;
  generatedAt?: string;
}

export type ConsultationStatus =
  | { kind: 'idle' }
  | { kind: 'submitting'; question: string }
  | { kind: 'success'; question: string; result: ConsultationResponseUi }
  | { kind: 'error'; question?: string; message: string };
