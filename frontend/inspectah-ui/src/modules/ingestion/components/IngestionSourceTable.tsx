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
    <div className="rounded-2xl border border-white/5 bg-white/5 shadow-card">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/5">
          <thead className="bg-white/5">
            <tr className="text-left text-xs uppercase tracking-[0.2em] text-slate-300">
              <th className="px-4 py-3">Fonte</th>
              <th className="px-4 py-3">Tipo</th>
              <th className="px-4 py-3">Modo</th>
              <th className="px-4 py-3">Última ingestão</th>
              <th className="px-4 py-3">Estado</th>
              <th className="px-4 py-3">Saúde</th>
              <th className="px-4 py-3">Histórico</th>
              <th className="px-4 py-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {rows.map(({ source, lastRun, health, mode, isProvider, isDerived }) => {
              const key = source.slug || source.id;
              const isOpsOnly = key.includes('newsdata') || isProvider;
              const running = runningIds.has(key);
              const lastDate = lastRun?.finished_at || lastRun?.started_at;
              return (
                <tr key={key} className="text-sm text-slate-100 hover:bg-white/5">
                  <td className="px-4 py-3">
                    <div className="font-semibold text-white">{source.name || source.id}</div>
                    <div className="text-xs text-slate-300">{key}</div>
                  </td>
                <td className="px-4 py-3">{source.type}</td>
                <td className="px-4 py-3">
                  <IngestionModeBadge mode={mode} onToggle={isOpsOnly || isDerived ? undefined : async (next) => await onToggleMode(key, next)} />
                  {isOpsOnly ? <p className="text-[11px] text-slate-400">Modo fixo (ops_only)</p> : null}
                  {isDerived ? <p className="text-[11px] text-amber-200">Fonte derivada do provedor newsdata_br (só leitura)</p> : null}
                </td>
                  <td className="px-4 py-3">{lastDate ? new Date(lastDate).toLocaleString() : isDerived ? 'Derivada (sem execuções)' : 'Nunca rodou'}</td>
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
                    <Link className="text-xs font-semibold text-sky-200 hover:underline" to={`/admin/ingestion/sources/${key}`}>
                      {isDerived ? 'Ver detalhes (derivada)' : 'Ver histórico'}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        size="sm"
                        variant="primary"
                        disabled={running || isDerived}
                        onClick={() => {
                          void onRun(key);
                        }}
                      >
                        {isDerived ? 'Controlada' : running ? 'Rodando...' : 'Rodar ingestão'}
                      </Button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default IngestionSourceTable;
