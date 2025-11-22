import EmptyState from './EmptyState';
import ErrorState from './ErrorState';
import EvidenceList from './EvidenceList';
import ResponseSummary from './ResponseSummary';
import RiskBadge from './RiskBadge';
import type { ConsultationStatus } from '../../types/inspectah';

interface ResultContainerProps {
  status: ConsultationStatus;
  onRetry?: () => void;
}

function LoadingState() {
  return (
    <div
      className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card"
      role="status"
      aria-busy="true"
      aria-live="polite"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex flex-col gap-2">
          <div className="h-4 w-40 animate-pulse rounded bg-white/10" />
          <div className="h-6 w-72 animate-pulse rounded bg-white/10" />
        </div>
        <div className="h-8 w-28 animate-pulse rounded-full bg-white/10" />
      </div>
      <div className="mt-6 space-y-3">
        <div className="h-4 w-full animate-pulse rounded bg-white/10" />
        <div className="h-4 w-11/12 animate-pulse rounded bg-white/10" />
        <div className="h-4 w-10/12 animate-pulse rounded bg-white/10" />
      </div>
    </div>
  );
}

function ResultContainer({ status, onRetry }: ResultContainerProps) {
  if (status.kind === 'idle') {
    return <EmptyState />;
  }

  if (status.kind === 'submitting') {
    return <LoadingState />;
  }

  if (status.kind === 'error') {
    return <ErrorState message={status.message} onRetry={onRetry} />;
  }

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card" aria-live="assertive">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Resposta consolidada</p>
            <ResponseSummary answer={status.result.answer} riskFlags={status.result.riskFlags} generatedAt={status.result.generatedAt} />
          </div>
          <RiskBadge riskLevel={status.result.riskLevel} riskScore={status.result.riskScore} />
        </div>
      </div>
      <EvidenceList evidences={status.result.evidences} />
    </div>
  );
}

export default ResultContainer;
