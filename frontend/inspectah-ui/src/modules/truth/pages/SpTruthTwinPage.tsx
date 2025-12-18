/**
 * S40-FE-001: Truth Twin Page
 *
 * Admin page for viewing Truth Twin status and decision history.
 */

import { useState, useCallback } from 'react';
import { clsx } from 'clsx';
import { SpCard } from '../../spovest/components/ui/Card';
import { SpButton } from '../../spovest/components/ui/Button';
import { SpInput } from '../../spovest/components/ui/Input';
import {
  TruthStateBadge,
  DecisionTimeline,
  TimelineFiltersBar,
  ProvenancePanel,
  ProvenanceIndicator,
  DecisionInspectorModal,
  LatencyBadge,
} from '../components';
import { useTruthTwin, useDecisionInspect } from '../hooks';
import type { DecisionBlockSummary, TimelineFilters } from '../types';

// Loading skeleton for the main content
function PageSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-32 bg-slate-800 rounded-xl" />
      <div className="grid grid-cols-3 gap-4">
        <div className="h-24 bg-slate-800 rounded-xl" />
        <div className="h-24 bg-slate-800 rounded-xl" />
        <div className="h-24 bg-slate-800 rounded-xl" />
      </div>
      <div className="h-64 bg-slate-800 rounded-xl" />
    </div>
  );
}

// Error state
interface ErrorStateProps {
  error: string;
  onRetry: () => void;
}

function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <SpCard className="text-center py-12">
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
      <h3 className="mt-4 text-lg font-medium text-slate-200">Erro ao carregar</h3>
      <p className="mt-2 text-slate-400">{error}</p>
      <SpButton onClick={onRetry} variant="primary" className="mt-6">
        Tentar novamente
      </SpButton>
    </SpCard>
  );
}

// Empty state (no claim selected)
function EmptyState() {
  return (
    <SpCard className="text-center py-16">
      <svg
        className="mx-auto h-16 w-16 text-slate-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <h3 className="mt-4 text-lg font-medium text-slate-200">Truth Twin</h3>
      <p className="mt-2 text-slate-400 max-w-md mx-auto">
        Digite um Claim ID ou slug para visualizar o histórico de decisões e
        proveniência completa.
      </p>
    </SpCard>
  );
}

// Stat card component
interface StatCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

function StatCard({ label, value, subValue, variant = 'default' }: StatCardProps) {
  const variantColors = {
    default: 'text-slate-200',
    success: 'text-emerald-400',
    warning: 'text-yellow-400',
    danger: 'text-red-400',
  };

  return (
    <div className="bg-slate-800/50 rounded-xl p-4">
      <p className="text-xs text-slate-500 uppercase tracking-wide">{label}</p>
      <p className={clsx('text-2xl font-bold mt-1', variantColors[variant])}>
        {value}
      </p>
      {subValue && <p className="text-xs text-slate-500 mt-1">{subValue}</p>}
    </div>
  );
}

export function SpTruthTwinPage() {
  // Search state
  const [searchInput, setSearchInput] = useState('');
  const [activeClaimId, setActiveClaimId] = useState<string | null>(null);

  // Timeline filters
  const [filters, setFilters] = useState<TimelineFilters>({});

  // Decision inspector state
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null);

  // Fetch Truth Twin data
  const {
    data: truthTwin,
    isLoading,
    error,
    refetch,
  } = useTruthTwin(activeClaimId, {
    enabled: !!activeClaimId,
  });

  // Fetch selected decision details
  const { data: selectedDecision, isLoading: isLoadingDecision } = useDecisionInspect(
    selectedDecisionId,
    { enabled: !!selectedDecisionId }
  );

  // Handle search
  const handleSearch = useCallback(() => {
    const trimmed = searchInput.trim();
    if (trimmed) {
      setActiveClaimId(trimmed);
    }
  }, [searchInput]);

  // Handle decision click
  const handleDecisionClick = useCallback((decision: DecisionBlockSummary) => {
    setSelectedDecisionId(decision.decision_id);
  }, []);

  // Handle close inspector
  const handleCloseInspector = useCallback(() => {
    setSelectedDecisionId(null);
  }, []);

  // Format date for display
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR');
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Truth Twin</h1>
        <p className="text-slate-400 mt-1">
          Visualize o histórico de decisões e proveniência de uma claim
        </p>
      </div>

      {/* Search bar */}
      <SpCard className="mb-6">
        <div className="flex gap-4">
          <SpInput
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Digite o Claim ID ou slug..."
            className="flex-1"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
          />
          <SpButton onClick={handleSearch} variant="primary" disabled={!searchInput.trim()}>
            Buscar
          </SpButton>
          {activeClaimId && (
            <SpButton onClick={() => refetch()} variant="secondary">
              Atualizar
            </SpButton>
          )}
        </div>
      </SpCard>

      {/* Main content */}
      {!activeClaimId && <EmptyState />}

      {activeClaimId && isLoading && <PageSkeleton />}

      {activeClaimId && error && (
        <ErrorState error={error.detail} onRetry={refetch} />
      )}

      {activeClaimId && truthTwin && !isLoading && !error && (
        <div className="space-y-6" data-testid="truth-twin-results">
          {/* CLAIM CONTENT - Main focus area */}
          <SpCard className="border-l-4 border-violet-500">
            {/* Header with label */}
            <div className="flex items-center gap-2 mb-4">
              <svg className="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-xs font-semibold uppercase tracking-wider text-violet-400">
                A Claim
              </span>
            </div>

            {/* Main claim text - VERY PROMINENT */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white leading-relaxed" data-testid="claim-text">
                {truthTwin.claim_text || truthTwin.headline || truthTwin.slug || 'Conteúdo não disponível'}
              </h2>
            </div>

            {/* Status and metadata row */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-700">
              <div className="flex items-center gap-4">
                <TruthStateBadge state={truthTwin.current_state} size="lg" showDot />
                <span className="text-sm text-slate-400">
                  Domínio: <span className="text-slate-200">{truthTwin.domain || '-'}</span>
                </span>
              </div>

              <div className="flex items-center gap-4">
                {truthTwin._latency_ms && (
                  <LatencyBadge latencyMs={truthTwin._latency_ms} />
                )}
                <ProvenanceIndicator
                  provenance={truthTwin.provenance}
                  onClick={() => {
                    document.getElementById('provenance-section')?.scrollIntoView({
                      behavior: 'smooth',
                    });
                  }}
                />
              </div>
            </div>

            {/* Claim ID and source link */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-700/50">
              <p className="text-xs text-slate-500 font-mono">
                ID: {truthTwin.claim_id}
              </p>
              {typeof truthTwin.metadata?.source_url === 'string' && truthTwin.metadata.source_url && (
                <a
                  href={truthTwin.metadata.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-violet-400 hover:text-violet-300 transition-colors"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  Ver fonte original
                </a>
              )}
            </div>
          </SpCard>

          {/* Stats row */}
          <div className="grid grid-cols-4 gap-4">
            <StatCard
              label="Total Decisões"
              value={truthTwin.decision_timeline.length}
            />
            <StatCard
              label="Transições de Estado"
              value={truthTwin.state_history.length}
            />
            <StatCard
              label="Criado em"
              value={formatDate(truthTwin.created_at)}
            />
            <StatCard
              label="Atualizado em"
              value={formatDate(truthTwin.updated_at)}
            />
          </div>

          {/* Two column layout */}
          <div className="grid grid-cols-3 gap-6">
            {/* Timeline column */}
            <div className="col-span-2 space-y-4">
              <SpCard>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-200">
                    Timeline de Decisões
                  </h3>
                  <span className="text-sm text-slate-500">
                    {truthTwin.decision_timeline.length} decisão(ões)
                  </span>
                </div>

                <TimelineFiltersBar
                  filters={filters}
                  onFiltersChange={setFilters}
                  className="mb-4"
                />

                <DecisionTimeline
                  decisions={truthTwin.decision_timeline}
                  filters={filters}
                  onDecisionClick={handleDecisionClick}
                />
              </SpCard>
            </div>

            {/* Provenance column */}
            <div className="space-y-4" id="provenance-section">
              <SpCard>
                <h3 className="text-lg font-semibold text-slate-200 mb-4">
                  Proveniência
                </h3>
                <ProvenancePanel provenance={truthTwin.provenance} showDetails />
              </SpCard>

              {/* Experience refs */}
              {truthTwin.experience_refs && truthTwin.experience_refs.length > 0 && (
                <SpCard>
                  <h3 className="text-lg font-semibold text-slate-200 mb-4">
                    Experiências Similares
                  </h3>
                  <div className="space-y-2">
                    {truthTwin.experience_refs.map((ref, index) => (
                      <div
                        key={index}
                        className="text-sm text-slate-400 font-mono bg-slate-800 px-3 py-2 rounded truncate"
                        title={ref}
                      >
                        {ref}
                      </div>
                    ))}
                  </div>
                </SpCard>
              )}

              {/* Metadata */}
              {truthTwin.metadata && Object.keys(truthTwin.metadata).length > 0 && (
                <SpCard>
                  <h3 className="text-lg font-semibold text-slate-200 mb-4">
                    Metadata
                  </h3>
                  <pre className="text-xs text-slate-400 bg-slate-800 p-3 rounded overflow-x-auto">
                    {JSON.stringify(truthTwin.metadata, null, 2)}
                  </pre>
                </SpCard>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Decision Inspector Modal */}
      <DecisionInspectorModal
        isOpen={!!selectedDecisionId}
        decision={selectedDecision ?? null}
        claimText={truthTwin?.claim_text || truthTwin?.headline}
        isLoading={isLoadingDecision}
        onClose={handleCloseInspector}
      />
    </div>
  );
}
