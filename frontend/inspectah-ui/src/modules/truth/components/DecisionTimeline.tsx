/**
 * S40-FE-002: Decision Timeline Component
 *
 * Displays a chronological timeline of decisions for a claim.
 */

import { clsx } from 'clsx';
import { useState, useMemo } from 'react';
import type { DecisionBlockSummary, TimelineFilters } from '../types';
import {
  TruthStateBadge,
  DecisionTypeBadge,
  GateBadge,
  LatencyBadge,
} from './StatusBadges';

interface DecisionTimelineProps {
  decisions: DecisionBlockSummary[];
  onDecisionClick?: (decision: DecisionBlockSummary) => void;
  filters?: TimelineFilters;
  isLoading?: boolean;
  className?: string;
}

// Format date for display
function formatDate(dateStr: string): string {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}

// Format relative time
function formatRelativeTime(dateStr: string): string {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'agora';
    if (diffMins < 60) return `${diffMins}m atrás`;
    if (diffHours < 24) return `${diffHours}h atrás`;
    if (diffDays < 7) return `${diffDays}d atrás`;
    return formatDate(dateStr);
  } catch {
    return dateStr;
  }
}

// Timeline item component
interface TimelineItemProps {
  decision: DecisionBlockSummary;
  isFirst: boolean;
  isLast: boolean;
  onClick?: () => void;
}

function TimelineItem({ decision, isFirst, isLast, onClick }: TimelineItemProps) {
  const stateChanged = decision.initial_state !== decision.final_state;

  return (
    <div
      className={clsx(
        'relative pl-8 pb-6',
        onClick && 'cursor-pointer hover:bg-slate-800/30 rounded-lg transition-colors',
        isLast && 'pb-0'
      )}
      onClick={onClick}
    >
      {/* Vertical line */}
      {!isLast && (
        <div className="absolute left-[11px] top-6 bottom-0 w-0.5 bg-slate-700" />
      )}

      {/* Dot indicator */}
      <div
        className={clsx(
          'absolute left-0 w-6 h-6 rounded-full flex items-center justify-center',
          stateChanged
            ? 'bg-violet-500/20 ring-2 ring-violet-500'
            : 'bg-slate-700 ring-2 ring-slate-600'
        )}
      >
        <div
          className={clsx(
            'w-2 h-2 rounded-full',
            stateChanged ? 'bg-violet-400' : 'bg-slate-400'
          )}
        />
      </div>

      {/* Content */}
      <div className="space-y-2">
        {/* Header row */}
        <div className="flex items-center gap-2 flex-wrap">
          <GateBadge gate={decision.gate} size="sm" />
          <DecisionTypeBadge decision={decision.decision_type} size="sm" />
          {decision.latency_ms !== null && decision.latency_ms !== undefined && (
            <LatencyBadge latencyMs={decision.latency_ms} size="sm" />
          )}
        </div>

        {/* State transition */}
        <div className="flex items-center gap-2 text-sm">
          <TruthStateBadge state={decision.initial_state} size="sm" />
          {stateChanged && (
            <>
              <svg
                className="w-4 h-4 text-slate-500"
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
              <TruthStateBadge state={decision.final_state} size="sm" />
            </>
          )}
        </div>

        {/* Metadata row */}
        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span title={formatDate(decision.created_at)}>
            {formatRelativeTime(decision.created_at)}
          </span>
          {decision.policy_name && (
            <span className="text-slate-400">
              Policy: {decision.policy_name}
              {decision.policy_version && ` v${decision.policy_version}`}
            </span>
          )}
        </div>

        {/* Decision ID */}
        <div className="text-xs text-slate-600 font-mono truncate">
          {decision.decision_id}
        </div>
      </div>
    </div>
  );
}

// Loading skeleton
function TimelineSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div key={i} className="relative pl-8">
          <div className="absolute left-0 w-6 h-6 rounded-full bg-slate-700" />
          <div className="space-y-2">
            <div className="flex gap-2">
              <div className="h-5 w-10 bg-slate-700 rounded-full" />
              <div className="h-5 w-16 bg-slate-700 rounded-full" />
            </div>
            <div className="h-4 w-32 bg-slate-700 rounded" />
            <div className="h-3 w-24 bg-slate-800 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

// Empty state
function TimelineEmpty() {
  return (
    <div className="text-center py-12">
      <svg
        className="mx-auto h-12 w-12 text-slate-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p className="mt-4 text-slate-400">Nenhuma decisão encontrada</p>
    </div>
  );
}

export function DecisionTimeline({
  decisions,
  onDecisionClick,
  filters,
  isLoading = false,
  className,
}: DecisionTimelineProps) {
  // Apply filters
  const filteredDecisions = useMemo(() => {
    if (!filters) return decisions;

    return decisions.filter((d) => {
      // Filter by gates
      if (filters.gates?.length && !filters.gates.includes(d.gate as any)) {
        return false;
      }
      // Filter by decision types
      if (
        filters.decision_types?.length &&
        !filters.decision_types.includes(d.decision_type as any)
      ) {
        return false;
      }
      // Filter by states
      if (filters.states?.length) {
        const matchesState =
          filters.states.includes(d.initial_state as any) ||
          filters.states.includes(d.final_state as any);
        if (!matchesState) return false;
      }
      // Filter by date range
      if (filters.date_from) {
        const from = new Date(filters.date_from);
        const created = new Date(d.created_at);
        if (created < from) return false;
      }
      if (filters.date_to) {
        const to = new Date(filters.date_to);
        const created = new Date(d.created_at);
        if (created > to) return false;
      }
      return true;
    });
  }, [decisions, filters]);

  if (isLoading) {
    return (
      <div className={className}>
        <TimelineSkeleton />
      </div>
    );
  }

  if (!filteredDecisions.length) {
    return (
      <div className={className}>
        <TimelineEmpty />
      </div>
    );
  }

  return (
    <div className={clsx('space-y-0', className)}>
      {filteredDecisions.map((decision, index) => (
        <TimelineItem
          key={decision.id || decision.decision_id || index}
          decision={decision}
          isFirst={index === 0}
          isLast={index === filteredDecisions.length - 1}
          onClick={onDecisionClick ? () => onDecisionClick(decision) : undefined}
        />
      ))}
    </div>
  );
}

// ===== Timeline Filters Component =====
interface TimelineFiltersBarProps {
  filters: TimelineFilters;
  onFiltersChange: (filters: TimelineFilters) => void;
  availableGates?: string[];
  availableDecisionTypes?: string[];
  className?: string;
}

export function TimelineFiltersBar({
  filters,
  onFiltersChange,
  availableGates = ['G0', 'G1', 'G2', 'G3', 'G4', 'NOGO'],
  availableDecisionTypes = ['APPROVE', 'REJECT', 'ESCALATE', 'BLOCK', 'DEGRADE', 'PROMOTE'],
  className,
}: TimelineFiltersBarProps) {
  const [showFilters, setShowFilters] = useState(false);

  const activeFilterCount =
    (filters.gates?.length || 0) +
    (filters.decision_types?.length || 0) +
    (filters.states?.length || 0) +
    (filters.date_from ? 1 : 0) +
    (filters.date_to ? 1 : 0);

  const toggleGate = (gate: string) => {
    const current = filters.gates || [];
    const newGates = current.includes(gate as any)
      ? current.filter((g) => g !== gate)
      : [...current, gate as any];
    onFiltersChange({ ...filters, gates: newGates.length ? newGates : undefined });
  };

  const toggleDecisionType = (type: string) => {
    const current = filters.decision_types || [];
    const newTypes = current.includes(type as any)
      ? current.filter((t) => t !== type)
      : [...current, type as any];
    onFiltersChange({
      ...filters,
      decision_types: newTypes.length ? newTypes : undefined,
    });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  return (
    <div className={clsx('space-y-3', className)}>
      {/* Toggle button */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={clsx(
            'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors',
            showFilters
              ? 'bg-violet-500/20 text-violet-400'
              : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
          )}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            />
          </svg>
          Filtros
          {activeFilterCount > 0 && (
            <span className="px-1.5 py-0.5 bg-violet-500 text-white text-xs rounded-full">
              {activeFilterCount}
            </span>
          )}
        </button>

        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            className="text-xs text-slate-500 hover:text-slate-400"
          >
            Limpar filtros
          </button>
        )}
      </div>

      {/* Filter options */}
      {showFilters && (
        <div className="p-4 bg-slate-800/50 rounded-lg space-y-4">
          {/* Gates */}
          <div>
            <label className="block text-xs text-slate-500 mb-2">Gates</label>
            <div className="flex flex-wrap gap-2">
              {availableGates.map((gate) => (
                <button
                  key={gate}
                  onClick={() => toggleGate(gate)}
                  className={clsx(
                    'px-2 py-1 text-xs rounded-full transition-colors',
                    filters.gates?.includes(gate as any)
                      ? 'bg-violet-500 text-white'
                      : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                  )}
                >
                  {gate}
                </button>
              ))}
            </div>
          </div>

          {/* Decision Types */}
          <div>
            <label className="block text-xs text-slate-500 mb-2">Tipos de Decisão</label>
            <div className="flex flex-wrap gap-2">
              {availableDecisionTypes.map((type) => (
                <button
                  key={type}
                  onClick={() => toggleDecisionType(type)}
                  className={clsx(
                    'px-2 py-1 text-xs rounded-full transition-colors',
                    filters.decision_types?.includes(type as any)
                      ? 'bg-violet-500 text-white'
                      : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                  )}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
