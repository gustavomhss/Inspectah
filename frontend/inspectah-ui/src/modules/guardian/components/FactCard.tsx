/**
 * FactCard v1 — S37
 *
 * Card component displaying a claim/decision with its validation status
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { GuardianDecision, DecisionBlock } from '../types';
import DecisionStatusBadge from './DecisionStatusBadge';
import { endpoints } from '../../../core/api/endpoints';
import { httpClient } from '../../../core/api/http-client';

interface FactCardProps {
  decision: GuardianDecision;
  showActions?: boolean;
  onReview?: (decisionId: string) => void;
  initialExpanded?: boolean;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function FactCard({ decision, showActions = true, onReview, initialExpanded = false }: FactCardProps) {
  const [expanded, setExpanded] = useState(initialExpanded);
  const [block, setBlock] = useState<DecisionBlock | null>(null);
  const [loading, setLoading] = useState(false);
  const [blockError, setBlockError] = useState<string | null>(null);

  const isTerminal = ['approved', 'rejected', 'escalated', 'timed_out', 'cancelled'].includes(
    decision.status
  );

  const canReview = decision.status === 'awaiting_review';

  // Fetch decision block when expanded (for completed decisions)
  useEffect(() => {
    if (expanded && isTerminal && !block && !loading) {
      setLoading(true);
      setBlockError(null);
      httpClient<DecisionBlock>(endpoints.admin.guardian.decisionBlock(decision.id))
        .then((data) => setBlock(data))
        .catch((err) => setBlockError(err instanceof Error ? err.message : 'Erro ao carregar'))
        .finally(() => setLoading(false));
    }
  }, [expanded, isTerminal, decision.id, block, loading]);

  return (
    <div className="rounded-lg bg-slate-800/60 border border-white/10 overflow-hidden hover:border-white/20 transition-colors">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <DecisionStatusBadge status={decision.status} />
          <span className="text-sm text-slate-400">
            {decision.domain} / {decision.gate}
          </span>
        </div>
        <span className="text-xs text-slate-500">{formatDate(decision.created_at)}</span>
      </div>

      {/* Body */}
      <div className="px-4 py-4">
        <div className="space-y-3">
          {/* CLAIM SUMMARY - O que está sendo decidido */}
          {decision.claim_summary ? (
            <div className="rounded-lg bg-slate-700/50 p-3 border-l-4 border-sky-500">
              <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Sobre o quê:</p>
              <p className="text-sm text-white font-medium">{decision.claim_summary}</p>
            </div>
          ) : (
            <div className="rounded-lg bg-slate-700/30 p-3 border-l-4 border-slate-600">
              <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Sobre o quê:</p>
              <p className="text-sm text-slate-400 italic">
                Claim ID: <span className="font-mono">{decision.claim_id}</span>
                <br />
                <span className="text-xs">(resumo não informado na submissão)</span>
              </p>
            </div>
          )}

          {/* EVIDENCE SUMMARY - Evidências que ancoram a claim */}
          {decision.evidence_summary && decision.evidence_summary.length > 0 && (
            <div className="rounded-lg bg-emerald-900/30 p-3 border-l-4 border-emerald-500">
              <p className="text-xs text-slate-400 uppercase tracking-wide mb-2">Baseado em:</p>
              <ul className="space-y-1">
                {decision.evidence_summary.map((evidence, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <span className="text-emerald-400 mt-0.5">📄</span>
                    <span className="text-emerald-200">{evidence}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="space-y-2 text-sm">
            {decision.policy_name && (
              <div className="flex items-start gap-2">
                <span className="text-xs text-slate-500 w-16 shrink-0">Policy:</span>
                <span className="text-sm text-sky-300">{decision.policy_name}</span>
              </div>
            )}
            <div className="flex items-start gap-2">
              <span className="text-xs text-slate-500 w-16 shrink-0">Proposto:</span>
              <span className="text-sm text-amber-300">{decision.proposed_state}</span>
            </div>
            {decision.final_state && (
              <div className="flex items-start gap-2">
                <span className="text-xs text-slate-500 w-16 shrink-0">Final:</span>
                <span
                  className={`text-sm font-medium ${
                    decision.final_state === 'verified'
                      ? 'text-green-400'
                      : decision.final_state === 'rejected'
                        ? 'text-red-400'
                        : 'text-slate-300'
                  }`}
                >
                  {decision.final_state}
                </span>
              </div>
            )}
            {decision.final_reason && (
              <div className="flex items-start gap-2">
                <span className="text-xs text-slate-500 w-16 shrink-0">Motivo:</span>
                <span className="text-xs text-slate-400">{decision.final_reason}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      {showActions && (
        <div className="px-4 py-3 border-t border-white/5 flex items-center gap-2">
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-sky-400 hover:text-sky-300 hover:underline"
          >
            {expanded ? '▼ Ocultar detalhes' : '▶ Ver detalhes'}
          </button>
          {canReview && onReview && (
            <>
              <span className="text-slate-600">|</span>
              <button
                onClick={() => onReview(decision.id)}
                className="text-xs text-amber-400 hover:text-amber-300 hover:underline"
              >
                Revisar
              </button>
            </>
          )}
          {decision.committee_id && (
            <>
              <span className="text-slate-600">|</span>
              <Link
                to={`/admin/guardian/decisions/${decision.id}/committee`}
                className="text-xs text-purple-400 hover:text-purple-300 hover:underline"
              >
                Ver comitê
              </Link>
            </>
          )}
        </div>
      )}

      {/* Expanded Details */}
      {expanded && (
        <div className="px-4 py-4 border-t border-white/10 bg-slate-900/50 space-y-4">
          {/* Loading */}
          {loading && (
            <p className="text-xs text-slate-400 animate-pulse">Carregando detalhes da decisão...</p>
          )}

          {/* Error */}
          {blockError && !blockError.includes('404') && (
            <div className="rounded bg-red-500/20 border border-red-500/30 p-3">
              <p className="text-xs text-red-300">{blockError}</p>
            </div>
          )}

          {/* PENDING DECISION - awaiting review/quorum */}
          {!isTerminal && (
            <div className="rounded-lg bg-amber-500/10 border border-amber-500/30 p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-amber-400 text-lg">⏳</span>
                <p className="text-amber-300 font-medium">Decisão Pendente</p>
              </div>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-slate-400">Claim a ser avaliada:</p>
                  <p className="text-sm text-white font-mono">{decision.claim_id}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Estado proposto:</p>
                  <p className="text-lg font-bold text-amber-300">{decision.proposed_state}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Política a aplicar:</p>
                  <p className="text-sm text-sky-300">{decision.policy_name || `${decision.domain}/${decision.gate}`}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Status atual:</p>
                  <p className="text-sm text-slate-200">{decision.status.replace(/_/g, ' ')}</p>
                </div>
                <p className="text-xs text-slate-500 mt-3 pt-3 border-t border-white/10">
                  O reasoning detalhado (invariantes verificados, evidências) estará disponível após a conclusão da revisão.
                </p>
              </div>
            </div>
          )}

          {/* COMPLETED DECISION */}
          {isTerminal && (
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500 mb-2">Decisão</p>
              <div className="rounded-lg bg-slate-800 p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 text-sm">{block?.initial_state || decision.proposed_state}</span>
                    <span className="text-slate-600">→</span>
                    <span className={`text-lg font-bold ${
                      (block?.final_state || decision.final_state) === 'verified' ? 'text-green-400' :
                      (block?.final_state || decision.final_state) === 'rejected' ? 'text-red-400' :
                      'text-amber-400'
                    }`}>
                      {block?.final_state || decision.final_state || 'pendente'}
                    </span>
                  </div>
                  {block?.decision_type && (
                    <span className="rounded-full bg-sky-500/20 px-2 py-1 text-xs text-sky-300">
                      {block.decision_type}
                    </span>
                  )}
                </div>
                {decision.final_reason && (
                  <p className="text-sm text-slate-300 border-l-2 border-sky-500 pl-3">
                    {decision.final_reason}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Invariants - O PORQUÊ (reasoning) */}
          {block?.invariants_checked && Object.keys(block.invariants_checked).length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500 mb-2">Verificações (Reasoning)</p>
              <div className="rounded-lg bg-slate-800 p-3 space-y-2">
                {Object.entries(block.invariants_checked).map(([invariant, passed]) => (
                  <div key={invariant} className="flex items-center gap-2 text-sm">
                    <span className={`text-lg ${passed ? 'text-green-400' : 'text-red-400'}`}>
                      {passed ? '✓' : '✗'}
                    </span>
                    <span className={passed ? 'text-slate-300' : 'text-red-300'}>
                      {invariant.replace(/_/g, ' ')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Evidence References */}
          {block?.evidence_refs && block.evidence_refs.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500 mb-2">Evidências Utilizadas</p>
              <div className="flex flex-wrap gap-2">
                {block.evidence_refs.map((ref, idx) => (
                  <span key={idx} className="rounded bg-slate-800 px-2 py-1 text-xs font-mono text-slate-300">
                    {ref.length > 20 ? `${ref.slice(0, 20)}...` : ref}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Committee Summary */}
          {block?.committee_summary && Object.keys(block.committee_summary).length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500 mb-2">Resumo do Comitê</p>
              <div className="rounded-lg bg-purple-500/10 border border-purple-500/30 p-3">
                <pre className="text-xs text-purple-200 overflow-x-auto">
                  {JSON.stringify(block.committee_summary, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Policy & Timing - only for terminal decisions */}
          {isTerminal && (
            <div className="grid grid-cols-2 gap-3">
              {(block?.policy_name || decision.policy_name) && (
                <div className="rounded bg-slate-800 p-3">
                  <p className="text-[10px] text-slate-500 uppercase">Política</p>
                  <p className="text-sm text-sky-300">{block?.policy_name || decision.policy_name}</p>
                  {block?.policy_version && (
                    <p className="text-[10px] text-slate-500">v{block.policy_version}</p>
                  )}
                </div>
              )}
              {block?.latency_ms && (
                <div className="rounded bg-slate-800 p-3">
                  <p className="text-[10px] text-slate-500 uppercase">Latência</p>
                  <p className="text-sm text-slate-300">{block.latency_ms}ms</p>
                </div>
              )}
            </div>
          )}

          {/* IDs (collapsed) */}
          <details className="text-xs">
            <summary className="text-slate-500 cursor-pointer hover:text-slate-400">
              Identificadores técnicos
            </summary>
            <div className="mt-2 space-y-1 pl-3 border-l border-white/10">
              <p><span className="text-slate-500">Decision:</span> <span className="font-mono text-slate-400">{decision.id}</span></p>
              <p><span className="text-slate-500">Claim:</span> <span className="font-mono text-slate-400">{decision.claim_id}</span></p>
              {decision.committee_id && (
                <p><span className="text-slate-500">Committee:</span> <span className="font-mono text-slate-400">{decision.committee_id}</span></p>
              )}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}

export default FactCard;
