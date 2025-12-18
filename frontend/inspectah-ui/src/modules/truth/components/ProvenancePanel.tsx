/**
 * S40-FE-003: Provenance Panel Component
 *
 * Displays full provenance information with references (guias, pilares, e40_5).
 */

import { clsx } from 'clsx';
import { useState } from 'react';
import type { ProvenanceInfo, References } from '../types';
import { ProvenanceBadge, E405Badge } from './StatusBadges';

interface ProvenancePanelProps {
  provenance: ProvenanceInfo | null | undefined;
  showDetails?: boolean;
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

// Section component for consistent styling
interface SectionProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

function Section({ title, children, className }: SectionProps) {
  return (
    <div className={clsx('space-y-2', className)}>
      <h4 className="text-xs font-medium text-slate-500 uppercase tracking-wide">
        {title}
      </h4>
      {children}
    </div>
  );
}

// Expandable list for references (handles both string[] and object[])
interface ReferenceListProps {
  title: string;
  items: unknown[];
  maxVisible?: number;
}

function formatReferenceItem(item: unknown): string {
  if (typeof item === 'string') {
    return item;
  }
  if (typeof item === 'object' && item !== null) {
    const obj = item as Record<string, unknown>;
    // Handle guia/pilar objects
    if ('guia' in obj && 'documento' in obj) {
      return `${obj.guia}: ${obj.documento} (v${obj.versao || '?'})`;
    }
    if ('pilar' in obj && 'documento' in obj) {
      return `${obj.pilar}: ${obj.documento} (v${obj.versao || '?'})`;
    }
    // Fallback to JSON
    return JSON.stringify(obj);
  }
  return String(item);
}

function ReferenceList({ title, items, maxVisible = 3 }: ReferenceListProps) {
  const [expanded, setExpanded] = useState(false);

  if (!items || items.length === 0) {
    return null;
  }

  const visibleItems = expanded ? items : items.slice(0, maxVisible);
  const hasMore = items.length > maxVisible;

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500">{title}</span>
        <span className="text-xs text-slate-600">{items.length} item(s)</span>
      </div>
      <ul className="space-y-1">
        {visibleItems.map((item, index) => {
          const displayText = formatReferenceItem(item);
          return (
            <li
              key={index}
              className="text-sm text-slate-300 font-mono bg-slate-800/50 px-2 py-1 rounded truncate"
              title={displayText}
            >
              {displayText}
            </li>
          );
        })}
      </ul>
      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-violet-400 hover:text-violet-300"
        >
          {expanded ? 'Ver menos' : `Ver mais ${items.length - maxVisible}`}
        </button>
      )}
    </div>
  );
}

// References panel (S40: guias, pilares, e40_5)
interface ReferencesPanelProps {
  references: References | null | undefined;
}

function ReferencesPanel({ references }: ReferencesPanelProps) {
  if (!references) {
    return null;
  }

  const { guias, pilares, e40_5, ...otherRefs } = references;
  const hasGuias = guias && guias.length > 0;
  const hasPilares = pilares && pilares.length > 0;
  const hasE405 = e40_5 && e40_5.status;
  const hasOther = Object.keys(otherRefs).length > 0;

  if (!hasGuias && !hasPilares && !hasE405 && !hasOther) {
    return null;
  }

  return (
    <Section title="References (S40)">
      <div className="space-y-4 p-3 bg-slate-800/30 rounded-lg border border-slate-700">
        {/* Guias */}
        {hasGuias && <ReferenceList title="Guias" items={guias!} />}

        {/* Pilares */}
        {hasPilares && <ReferenceList title="Pilares" items={pilares!} />}

        {/* E40.5 */}
        {hasE405 && (
          <div className="space-y-1">
            <span className="text-xs text-slate-500">E40.5 Status</span>
            <div className="flex items-center gap-2">
              <E405Badge status={e40_5!.status} />
              {e40_5!.message && (
                <span className="text-xs text-slate-400">{e40_5!.message}</span>
              )}
            </div>
          </div>
        )}

        {/* Other references */}
        {hasOther && (
          <div className="space-y-1">
            <span className="text-xs text-slate-500">Outras Referências</span>
            <pre className="text-xs text-slate-400 bg-slate-900 p-2 rounded overflow-x-auto">
              {JSON.stringify(otherRefs, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </Section>
  );
}

// Empty state
function ProvenanceEmpty() {
  return (
    <div className="text-center py-8">
      <svg
        className="mx-auto h-10 w-10 text-slate-600"
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
      <p className="mt-3 text-sm text-slate-400">Sem proveniência disponível</p>
      <p className="text-xs text-slate-500">
        Este registro não possui informações de auditoria
      </p>
    </div>
  );
}

export function ProvenancePanel({
  provenance,
  showDetails = true,
  className,
}: ProvenancePanelProps) {
  const isValid = provenance !== null && provenance !== undefined && !!provenance.source;

  if (!provenance) {
    return (
      <div className={clsx('bg-slate-800/50 rounded-lg p-4', className)}>
        <ProvenanceEmpty />
      </div>
    );
  }

  return (
    <div className={clsx('bg-slate-800/50 rounded-lg p-4 space-y-4', className)}>
      {/* Header with validity badge */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-200">Proveniência</h3>
        <ProvenanceBadge isValid={isValid} />
      </div>

      {/* Core info */}
      <div className="grid grid-cols-2 gap-4">
        <Section title="Origem">
          <p className="text-sm text-slate-300 font-mono">{provenance.source}</p>
        </Section>

        <Section title="Timestamp">
          <p className="text-sm text-slate-300">
            {formatTimestamp(provenance.timestamp)}
          </p>
        </Section>
      </div>

      {/* Policy info */}
      {(provenance.policy_name || provenance.policy_version) && (
        <div className="grid grid-cols-2 gap-4">
          {provenance.policy_name && (
            <Section title="Policy">
              <p className="text-sm text-slate-300">{provenance.policy_name}</p>
            </Section>
          )}
          {provenance.policy_version && (
            <Section title="Versão">
              <p className="text-sm text-slate-300 font-mono">
                v{provenance.policy_version}
              </p>
            </Section>
          )}
        </div>
      )}

      {/* Actor */}
      {provenance.actor && (
        <Section title="Ator">
          <p className="text-sm text-slate-300 font-mono">{provenance.actor}</p>
        </Section>
      )}

      {/* Evidence references */}
      {showDetails && provenance.evidence_refs && provenance.evidence_refs.length > 0 && (
        <Section title="Referências de Evidência">
          <div className="space-y-1">
            {provenance.evidence_refs.map((ref, index) => (
              <div
                key={index}
                className="text-xs text-slate-400 font-mono bg-slate-900 px-2 py-1 rounded truncate"
                title={ref}
              >
                {ref}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* S40 References (guias, pilares, e40_5) */}
      {showDetails && provenance.references && (
        <ReferencesPanel references={provenance.references as References} />
      )}
    </div>
  );
}

// ===== Compact Provenance Indicator =====
interface ProvenanceIndicatorProps {
  provenance: ProvenanceInfo | null | undefined;
  onClick?: () => void;
  className?: string;
}

export function ProvenanceIndicator({
  provenance,
  onClick,
  className,
}: ProvenanceIndicatorProps) {
  const isValid = provenance !== null && provenance !== undefined && !!provenance.source;

  return (
    <button
      onClick={onClick}
      className={clsx(
        'flex items-center gap-2 px-3 py-2 rounded-lg transition-colors',
        isValid
          ? 'bg-emerald-500/10 hover:bg-emerald-500/20'
          : 'bg-red-500/10 hover:bg-red-500/20',
        className
      )}
    >
      <span
        className={clsx(
          'w-2 h-2 rounded-full',
          isValid ? 'bg-emerald-400' : 'bg-red-400'
        )}
      />
      <span className={clsx('text-sm', isValid ? 'text-emerald-400' : 'text-red-400')}>
        {isValid ? 'Proveniência válida' : 'Sem proveniência'}
      </span>
      {onClick && (
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
            d="M9 5l7 7-7 7"
          />
        </svg>
      )}
    </button>
  );
}
