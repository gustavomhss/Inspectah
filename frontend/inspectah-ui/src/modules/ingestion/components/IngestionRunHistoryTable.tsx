import type { IngestionRun } from '../../../core/api/api-types';
import IngestionStatusBadge from './IngestionStatusBadge';

interface Props {
  runs: IngestionRun[];
  onSelectRun?: (run: IngestionRun) => void;
}

function IngestionRunHistoryTable({ runs, onSelectRun }: Props) {
  if (!runs.length) {
    return <p className="text-sm text-slate-200">Nenhum histórico de ingestão para esta fonte.</p>;
  }
  return (
    <div className="overflow-hidden rounded-2xl border border-white/5 bg-white/5 shadow-card">
      <table className="min-w-full divide-y divide-white/5">
        <thead className="bg-white/5">
          <tr className="text-left text-xs uppercase tracking-[0.2em] text-slate-300">
            <th className="px-4 py-3">Run ID</th>
            <th className="px-4 py-3">Início</th>
            <th className="px-4 py-3">Fim</th>
            <th className="px-4 py-3">Duração</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3 text-right">Itens</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {runs.map((run) => {
            const start = run.started_at ? new Date(run.started_at) : null;
            const finish = run.finished_at ? new Date(run.finished_at) : null;
            const durationMs = start && finish ? finish.getTime() - start.getTime() : null;
            const durationLabel = durationMs !== null ? `${Math.max(durationMs / 1000, 0).toFixed(1)}s` : '—';
            return (
              <tr key={run.id} className="text-sm text-slate-100 hover:bg-white/5">
                <td className="px-4 py-3">
                  <button
                    type="button"
                    onClick={() => onSelectRun?.(run)}
                    className="font-semibold text-sky-200 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
                  >
                    {run.id}
                  </button>
                </td>
                <td className="px-4 py-3">{start ? start.toLocaleString() : '—'}</td>
                <td className="px-4 py-3">{finish ? finish.toLocaleString() : 'Em andamento'}</td>
                <td className="px-4 py-3">{durationLabel}</td>
                <td className="px-4 py-3">
                  <IngestionStatusBadge status={run.status} />
                </td>
                <td className="px-4 py-3 text-right">{run.items_processed ?? 0}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default IngestionRunHistoryTable;
