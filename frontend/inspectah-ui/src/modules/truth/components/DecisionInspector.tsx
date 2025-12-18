/**
 * S40-FE-004: Decision Inspector Component
 *
 * Modal/panel for inspecting full decision details with provenance.
 */

import { clsx } from 'clsx';
import { useEffect, useCallback } from 'react';
import type { DecisionInspectResponse, InvariantsChecked, CommitteeSummary } from '../types';
import {
  TruthStateBadge,
  DecisionTypeBadge,
  GateBadge,
  LatencyBadge,
  ProvenanceBadge,
} from './StatusBadges';
import { ProvenancePanel } from './ProvenancePanel';

interface DecisionInspectorProps {
  decision: DecisionInspectResponse | null;
  claimText?: string | null;  // The claim content to display
  isLoading?: boolean;
  error?: string | null;
  onClose?: () => void;
  className?: string;
}

// Format timestamp for display
function formatTimestamp(timestamp: string): string {
  if (!timestamp) return '';
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return timestamp;
  }
}

// Section component
interface SectionProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

function Section({ title, children, className }: SectionProps) {
  return (
    <div className={clsx('space-y-3', className)}>
      <h3 className="text-sm font-medium text-slate-300 border-b border-slate-700 pb-2">
        {title}
      </h3>
      {children}
    </div>
  );
}

// Invariants display
interface InvariantsDisplayProps {
  invariants: InvariantsChecked;
}

function InvariantsDisplay({ invariants }: InvariantsDisplayProps) {
  const entries = Object.entries(invariants);

  if (entries.length === 0) {
    return <p className="text-sm text-slate-500">Nenhum invariante verificado</p>;
  }

  return (
    <div className="space-y-2">
      {entries.map(([name, passed]) => (
        <div
          key={name}
          className={clsx(
            'flex items-center justify-between px-3 py-2 rounded-lg',
            passed === true && 'bg-emerald-500/10',
            passed === false && 'bg-red-500/10',
            passed === null && 'bg-slate-700/50'
          )}
        >
          <span className="text-sm text-slate-300 font-mono">{name}</span>
          <span
            className={clsx(
              'text-xs font-medium',
              passed === true && 'text-emerald-400',
              passed === false && 'text-red-400',
              passed === null && 'text-slate-500'
            )}
          >
            {passed === true && 'PASS'}
            {passed === false && 'FAIL'}
            {passed === null && 'N/A'}
          </span>
        </div>
      ))}
    </div>
  );
}

// Committee summary display
interface CommitteeDisplayProps {
  committee: CommitteeSummary;
}

function CommitteeDisplay({ committee }: CommitteeDisplayProps) {
  const hasVotes =
    committee.total_votes !== undefined ||
    committee.approve_votes !== undefined ||
    committee.reject_votes !== undefined;

  const hasS40Fields = committee.decision || committee.notes || committee.confidence !== undefined;
  const hasLegacyFields = hasVotes || committee.consensus || committee.members?.length;

  if (!hasS40Fields && !hasLegacyFields) {
    return <p className="text-sm text-slate-500">Sem informações de comitê</p>;
  }

  return (
    <div className="space-y-4">
      {/* S40: Decision & Confidence */}
      {(committee.decision || committee.confidence !== undefined) && (
        <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
          {committee.decision && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">Decisão:</span>
              <span
                className={clsx(
                  'px-2 py-1 text-sm font-bold rounded',
                  committee.decision === 'APPROVE' && 'bg-emerald-500/20 text-emerald-400',
                  committee.decision === 'REJECT' && 'bg-red-500/20 text-red-400',
                  !['APPROVE', 'REJECT'].includes(committee.decision) && 'bg-slate-700 text-slate-300'
                )}
              >
                {committee.decision}
              </span>
            </div>
          )}
          {committee.confidence !== undefined && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">Confiança:</span>
              <span className="text-sm font-mono text-violet-400">
                {(committee.confidence * 100).toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      )}

      {/* S40: Notes */}
      {committee.notes && (
        <div className="p-3 bg-slate-800/30 rounded-lg border-l-2 border-violet-500">
          <p className="text-xs text-slate-500 mb-1">Notas</p>
          <p className="text-sm text-slate-200">{committee.notes}</p>
        </div>
      )}

      {/* S40: Reviewers */}
      {committee.reviewers && committee.reviewers.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-2">Revisores ({committee.reviewers.length})</p>
          <div className="flex flex-wrap gap-2">
            {committee.reviewers.map((reviewer, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-violet-500/20 text-violet-300 text-xs rounded-full"
              >
                {reviewer}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Legacy: Votes */}
      {hasVotes && (
        <div className="grid grid-cols-3 gap-3">
          {committee.total_votes !== undefined && (
            <div className="bg-slate-700/50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-slate-200">
                {committee.total_votes}
              </p>
              <p className="text-xs text-slate-500">Total</p>
            </div>
          )}
          {committee.approve_votes !== undefined && (
            <div className="bg-emerald-500/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-emerald-400">
                {committee.approve_votes}
              </p>
              <p className="text-xs text-slate-500">Aprovação</p>
            </div>
          )}
          {committee.reject_votes !== undefined && (
            <div className="bg-red-500/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-red-400">
                {committee.reject_votes}
              </p>
              <p className="text-xs text-slate-500">Rejeição</p>
            </div>
          )}
        </div>
      )}

      {/* Legacy: Consensus & Quorum */}
      {(committee.consensus || committee.quorum_reached !== undefined) && (
        <div className="flex items-center gap-4">
          {committee.consensus && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">Consenso:</span>
              <span className="text-sm text-slate-300 font-medium">
                {committee.consensus}
              </span>
            </div>
          )}
          {committee.quorum_reached !== undefined && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">Quórum:</span>
              <span
                className={clsx(
                  'text-sm font-medium',
                  committee.quorum_reached ? 'text-emerald-400' : 'text-red-400'
                )}
              >
                {committee.quorum_reached ? 'Atingido' : 'Não atingido'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Legacy: Members */}
      {committee.members && committee.members.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-2">Membros ({committee.members.length})</p>
          <div className="flex flex-wrap gap-2">
            {committee.members.map((member, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded-full"
              >
                {member}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Loading skeleton
function InspectorSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="flex gap-4">
        <div className="h-8 w-20 bg-slate-700 rounded-full" />
        <div className="h-8 w-24 bg-slate-700 rounded-full" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="h-20 bg-slate-800 rounded-lg" />
        <div className="h-20 bg-slate-800 rounded-lg" />
      </div>
      <div className="h-32 bg-slate-800 rounded-lg" />
      <div className="h-48 bg-slate-800 rounded-lg" />
    </div>
  );
}

// Error state
interface ErrorDisplayProps {
  error: string;
  onRetry?: () => void;
}

function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  return (
    <div className="text-center py-12">
      <svg
        className="mx-auto h-12 w-12 text-red-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
      <p className="mt-4 text-slate-400">{error}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-4 py-2 bg-violet-500 text-white text-sm rounded-lg hover:bg-violet-600 transition-colors"
        >
          Tentar novamente
        </button>
      )}
    </div>
  );
}

export function DecisionInspector({
  decision,
  claimText,
  isLoading = false,
  error,
  onClose,
  className,
}: DecisionInspectorProps) {
  // Close on Escape key
  const handleKeyDown = useCallback(
    (e: globalThis.KeyboardEvent) => {
      if (e.key === 'Escape' && onClose) {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (isLoading) {
    return (
      <div className={clsx('bg-slate-900 rounded-xl p-6', className)}>
        <InspectorSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className={clsx('bg-slate-900 rounded-xl p-6', className)}>
        <ErrorDisplay error={error} />
      </div>
    );
  }

  if (!decision) {
    return null;
  }

  const stateChanged = decision.initial_state !== decision.final_state;
  const isProvenanceValid =
    decision.provenance !== null &&
    decision.provenance !== undefined &&
    !!decision.provenance.source;

  return (
    <div className={clsx('bg-slate-900 rounded-xl overflow-hidden', className)}>
      {/* Header */}
      <div className="px-6 py-4 bg-slate-800/50 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-slate-200">Inspeção de Decisão</h2>
          <ProvenanceBadge isValid={isProvenanceValid} size="sm" />
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
        {/* CLAIM CONTENT - What this decision is about */}
        {claimText && (
          <div className="p-4 bg-violet-500/10 rounded-xl border border-violet-500/30">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-4 h-4 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-xs font-semibold uppercase tracking-wider text-violet-400">
                A Claim
              </span>
            </div>
            <p className="text-lg font-semibold text-white leading-relaxed">
              {claimText}
            </p>
          </div>
        )}

        {/* Badges row */}
        <div className="flex items-center gap-3 flex-wrap">
          <GateBadge gate={decision.gate} size="md" />
          <DecisionTypeBadge decision={decision.decision_type} size="md" />
          {decision.latency_ms !== null && decision.latency_ms !== undefined && (
            <LatencyBadge latencyMs={decision.latency_ms} size="md" />
          )}
        </div>

        {/* State transition */}
        <Section title="Transição de Estado">
          <div className="flex items-center gap-4 p-4 bg-slate-800/30 rounded-lg">
            <div className="text-center">
              <p className="text-xs text-slate-500 mb-1">Estado Inicial</p>
              <TruthStateBadge state={decision.initial_state} size="lg" showDot />
            </div>
            {stateChanged && (
              <>
                <svg
                  className="w-8 h-8 text-violet-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M14 5l7 7m0 0l-7 7m7-7H3"
                  />
                </svg>
                <div className="text-center">
                  <p className="text-xs text-slate-500 mb-1">Estado Final</p>
                  <TruthStateBadge state={decision.final_state} size="lg" showDot />
                </div>
              </>
            )}
            {!stateChanged && (
              <p className="text-sm text-slate-400 ml-4">Estado mantido</p>
            )}
          </div>
          {/* Reason for transition */}
          {decision.state_transition?.reason && (
            <div className="mt-3 p-3 bg-violet-500/10 rounded-lg border-l-2 border-violet-500">
              <p className="text-xs text-slate-500 mb-1">Razão da Decisão</p>
              <p className="text-sm text-slate-200">{decision.state_transition.reason}</p>
            </div>
          )}
        </Section>

        {/* IDs */}
        <Section title="Identificadores">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-800/30 p-3 rounded-lg">
              <p className="text-xs text-slate-500 mb-1">Decision ID</p>
              <p className="text-sm text-slate-300 font-mono truncate" title={decision.decision_id}>
                {decision.decision_id}
              </p>
            </div>
            <div className="bg-slate-800/30 p-3 rounded-lg">
              <p className="text-xs text-slate-500 mb-1">Block ID</p>
              <p className="text-sm text-slate-300 font-mono truncate" title={decision.block_id}>
                {decision.block_id}
              </p>
            </div>
            <div className="bg-slate-800/30 p-3 rounded-lg">
              <p className="text-xs text-slate-500 mb-1">Claim ID</p>
              <p className="text-sm text-slate-300 font-mono truncate" title={decision.claim_id}>
                {decision.claim_id}
              </p>
            </div>
            <div className="bg-slate-800/30 p-3 rounded-lg">
              <p className="text-xs text-slate-500 mb-1">Domínio</p>
              <p className="text-sm text-slate-300">{decision.domain || '-'}</p>
            </div>
          </div>
        </Section>

        {/* Policy */}
        {(decision.policy_name || decision.policy_version) && (
          <Section title="Policy">
            <div className="flex items-center gap-4 bg-slate-800/30 p-3 rounded-lg">
              {decision.policy_name && (
                <div>
                  <p className="text-xs text-slate-500">Nome</p>
                  <p className="text-sm text-slate-300">{decision.policy_name}</p>
                </div>
              )}
              {decision.policy_version && (
                <div>
                  <p className="text-xs text-slate-500">Versão</p>
                  <p className="text-sm text-slate-300 font-mono">
                    v{decision.policy_version}
                  </p>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Committee */}
        {decision.committee_summary &&
          Object.keys(decision.committee_summary).length > 0 && (
            <Section title="Comitê">
              <CommitteeDisplay committee={decision.committee_summary} />
            </Section>
          )}

        {/* Invariants */}
        {decision.invariants_checked &&
          Object.keys(decision.invariants_checked).length > 0 && (
            <Section title="Invariantes Verificados">
              <InvariantsDisplay invariants={decision.invariants_checked} />
            </Section>
          )}

        {/* Evidence refs */}
        {decision.evidence_refs && decision.evidence_refs.length > 0 && (
          <Section title="Referências de Evidência">
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {decision.evidence_refs.map((ref, index) => (
                <div
                  key={index}
                  className="text-xs text-slate-400 font-mono bg-slate-800 px-3 py-2 rounded truncate"
                  title={ref}
                >
                  {ref}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Provenance */}
        <Section title="Proveniência">
          <ProvenancePanel provenance={decision.provenance} showDetails />
        </Section>

        {/* Timestamp */}
        <div className="pt-4 border-t border-slate-700 text-xs text-slate-500">
          Criado em: {formatTimestamp(decision.created_at)}
        </div>
      </div>
    </div>
  );
}

// ===== Modal wrapper =====
interface DecisionInspectorModalProps extends DecisionInspectorProps {
  isOpen: boolean;
}

export function DecisionInspectorModal({
  isOpen,
  onClose,
  ...props
}: DecisionInspectorModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Content */}
      <div className="relative w-full max-w-3xl max-h-[90vh]">
        <DecisionInspector {...props} onClose={onClose} />
      </div>
    </div>
  );
}
