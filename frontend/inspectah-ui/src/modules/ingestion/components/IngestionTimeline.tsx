import type { IngestionRun } from '../../../core/api/api-types';
import IngestionStatusBadge from './IngestionStatusBadge';

interface Props {
  runs: IngestionRun[];
  onSelectRun?: (run: IngestionRun) => void;
}

function IngestionTimeline({ runs, onSelectRun }: Props) {
  if (!runs.length) return null;
  const sorted = [...runs].sort((a, b) => new Date(a.started_at).getTime() - new Date(b.started_at).getTime());
  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">Timeline</p>
      <div className="mt-3 flex items-center gap-2 overflow-x-auto pb-2">
        {sorted.map((run) => (
          <button
            key={run.id}
            type="button"
            aria-label={`Run ${run.id}`}
            onClick={() => onSelectRun?.(run)}
            className="flex min-w-[120px] flex-col items-center gap-2 rounded-xl border border-white/5 bg-white/5 px-3 py-2 text-xs text-white hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
          >
            <span className="font-semibold">{new Date(run.started_at).toLocaleDateString()}</span>
            <IngestionStatusBadge status={run.status} />
          </button>
        ))}
      </div>
    </div>
  );
}

export default IngestionTimeline;
