import { Link } from 'react-router-dom';
import type { AdminSource, AdminSourceHealthStatus } from '../../../core/api/api-types';
import SourceStatusBadge from './SourceStatusBadge';

interface Props {
  sources: AdminSource[];
}

function SourcesTable({ sources }: Props) {
  if (sources.length === 0) {
    return <p className="text-sm text-slate-200">Nenhuma fonte encontrada com os filtros atuais.</p>;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-white/5 bg-white/5 shadow-card">
      <table className="min-w-full divide-y divide-white/5">
        <thead className="bg-white/5">
          <tr className="text-left text-xs uppercase tracking-[0.2em] text-slate-300">
            <th className="px-4 py-3">Fonte</th>
            <th className="px-4 py-3">Tipo</th>
            <th className="px-4 py-3">Refresh (min)</th>
            <th className="px-4 py-3">Estado</th>
            <th className="px-4 py-3">Saúde</th>
            <th className="px-4 py-3">Último health-check</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {sources.map((source) => {
            const healthStatus: AdminSourceHealthStatus = source.last_health_status ?? 'unknown';
            return (
            <tr key={source.id} className="text-sm text-slate-100 hover:bg-white/5">
              <td className="px-4 py-3">
                <Link to={`/admin/sources/${source.id}`} className="font-semibold text-white hover:underline">
                  {source.name || source.id}
                </Link>
                <div className="text-xs text-slate-300">{(source.info_types || []).join(', ') || 'tipo não informado'}</div>
              </td>
              <td className="px-4 py-3">{source.type}</td>
              <td className="px-4 py-3">{source.refresh_interval ?? '—'}</td>
              <td className="px-4 py-3">
                <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white">{source.state}</span>
              </td>
              <td className="px-4 py-3">
                <SourceStatusBadge status={healthStatus} />
              </td>
              <td className="px-4 py-3 text-slate-200">{source.last_health_at || '—'}</td>
            </tr>
          );
        })}
        </tbody>
      </table>
    </div>
  );
}

export default SourcesTable;
