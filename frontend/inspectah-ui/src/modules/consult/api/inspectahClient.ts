import { httpClient } from '../../../core/api/http-client';
import { endpoints } from '../../../core/api/endpoints';
import type {
  ConsultationRequest,
  ConsultationResponseRaw,
  ConsultationResponseUi,
  EvidenceItemRaw,
  EvidenceItemUi,
  RiskLevel,
} from '../../../core/api/api-types';

function normalizeRiskLevel(level?: string): RiskLevel {
  const normalized = (level || '').toLowerCase();
  if (normalized === 'low') return 'low';
  if (normalized === 'medium' || normalized === 'moderate') return 'medium';
  if (normalized === 'high' || normalized === 'critical') return 'high';
  return 'unknown';
}

function normalizeEvidenceItem(raw: EvidenceItemRaw, index: number): EvidenceItemUi {
  return {
    id: raw.id || `evidence-${index}`,
    sourceName: raw.source_name || raw.source || 'Fonte não informada',
    sourceType: raw.source_type || raw.type || 'desconhecida',
    description: raw.description || raw.summary || 'Sem descrição disponível',
    link: raw.link,
    credibility: raw.credibility,
  };
}

function mapToUi(raw: ConsultationResponseRaw): ConsultationResponseUi {
  const evidencesRaw: EvidenceItemRaw[] = [
    ...(raw.evidences || []),
    ...(raw.evidence?.items_preview || []),
    ...(raw.evidence?.sources || []),
  ];

  const evidences = evidencesRaw.map((item, index) => normalizeEvidenceItem(item, index));

  const riskLevel = normalizeRiskLevel(
    raw.risk_level || raw.summary_card?.risk_level || raw.confidence?.level || raw.summary_card?.confidence_level,
  );

  const answer = raw.answer || raw.answer_text || 'Não encontramos uma resposta confiável para essa pergunta.';
  const truthState =
    (raw as Record<string, unknown>)?.truth_state?.toString() ||
    raw.summary_card?.confidence_level ||
    raw.summary_card?.risk_level ||
    raw.risk_level;

  return {
    answer,
    riskLevel,
    riskScore: raw.risk_score || raw.confidence?.score || raw.summary_card?.confidence_score,
    riskFlags: raw.risk_flags || raw.confidence?.reasons,
    truthState: truthState as string,
    evidences,
    requestId: raw.request_id,
    generatedAt: raw.generated_at,
  };
}

export async function consultTruth(request: ConsultationRequest): Promise<ConsultationResponseUi> {
  const payload = {
    question: request.question,
    locale: request.locale || 'pt-BR',
    context: request.context,
  };

  const raw = await httpClient<ConsultationResponseRaw>(endpoints.consult, {
    method: 'POST',
    body: JSON.stringify(payload),
  });

  return mapToUi(raw);
}
