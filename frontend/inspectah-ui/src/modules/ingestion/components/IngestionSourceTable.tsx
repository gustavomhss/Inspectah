import type { IngestionSourceRow } from '../hooks/useIngestionSources';
import type { IngestionMode } from '../../../core/api/api-types';
import IngestionModeBadge from './IngestionModeBadge';
import IngestionStatusBadge from './IngestionStatusBadge';
import Button from '../../../shared/components/Button';
import { Link } from 'react-router-dom';

interface Props {
  rows: IngestionSourceRow[];
  onRun: (sourceId: string) => Promise<void>;
  onToggleMode: (sourceId: string, mode: IngestionMode) => Promise<void>;
  runningIds: Set<string>;
}

function IngestionSourceTable({ rows, onRun, onToggleMode, runningIds }: Props) {
  if (rows.length === 0) {
    return <p className="text-sm text-slate-200">Nenhuma fonte encontrada.</p>;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-white/5 bg-white/5 shadow-card">
      <table className="min-w-full divide-y divide-white/5">
        <thead className="bg-white/5">
          <tr className="text-left text-xs uppercase tracking-[0.2em] text-slate-300">
            <th className="px-4 py-3">Fonte</th>
            <th className="px-4 py-3">Tipo</th>
            <th className="px-4 py-3">Modo</th>
            <th className="px-4 py-3">Última ingestão</th>
            <th className="px-4 py-3">Estado</th>
            <th className="px-4 py-3">Saúde</th>
            <th className="px-4 py-3 text-right">Ações</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {rows.map(({ source, lastRun, health, mode }) => {
            const running = runningIds.has(source.id);
            const lastDate = lastRun?.finished_at || lastRun?.started_at;
            return (
              <tr key={source.id} className="text-sm text-slate-100 hover:bg-white/5">
                <td className="px-4 py-3">
                  <div className="font-semibold text-white">{source.name || source.id}</div>
                  <div className="text-xs text-slate-300">{source.id}</div>
                </td>
                <td className="px-4 py-3">{source.type}</td>
                <td className="px-4 py-3">
                  <IngestionModeBadge mode={mode} onToggle={async (next) => await onToggleMode(source.id, next)} />
                </td>
                <td className="px-4 py-3">{lastDate ? new Date(lastDate).toLocaleString() : 'Nunca rodou'}</td>
                <td className="px-4 py-3">
                  <IngestionStatusBadge status={lastRun?.status} showNever={!lastRun} />
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      health === 'OK'
                        ? 'bg-emerald-500/20 text-emerald-100 border border-emerald-400/40'
                        : health === 'Falhando'
                          ? 'bg-rose-500/20 text-rose-100 border border-rose-400/40'
                          : health === 'Em andamento'
                            ? 'bg-amber-500/20 text-amber-100 border border-amber-400/40'
                            : 'bg-slate-500/20 text-slate-100 border border-slate-400/40'
                    }`}
                  >
                    {health}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center justify-end gap-2">
                    <Link
                      to={`/admin/ingestion/sources/${encodeURIComponent(source.id)}`}
                      className="text-xs font-semibold text-sky-200 hover:underline"
                    >
                      Ver detalhes
                    </Link>
                    <Button
                      size="sm"
                      variant="primary"
                      disabled={running}
                      onClick={() => {
                        void onRun(source.id);
                      }}
                    >
                      {running ? 'Rodando...' : 'Rodar ingestão'}
                    </Button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default IngestionSourceTable;
