import { Link } from 'react-router-dom';
import type { AdminSource } from '../../../core/api/api-types';
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
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Última coleta</th>
            <th className="px-4 py-3">Itens recentes</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {sources.map((source) => (
            <tr key={source.id} className="text-sm text-slate-100 hover:bg-white/5">
              <td className="px-4 py-3">
                <Link to={`/admin/sources/${source.id}`} className="font-semibold text-white hover:underline">
                  {source.name || source.id}
                </Link>
                <div className="text-xs text-slate-300">{source.info_type || 'tipo não informado'}</div>
              </td>
              <td className="px-4 py-3">{source.type}</td>
              <td className="px-4 py-3">
                <SourceStatusBadge status={source.status} />
              </td>
              <td className="px-4 py-3 text-slate-200">{source.last_checked_at || '—'}</td>
              <td className="px-4 py-3">{source.recent_items_count ?? 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SourcesTable;
