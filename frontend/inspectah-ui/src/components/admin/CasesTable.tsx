import { Link } from 'react-router-dom';
import type { AdminCase } from '../../types/admin';
import CaseStatusBadge from './CaseStatusBadge';
import RiskBadge from './RiskBadge';

interface Props {
  cases: AdminCase[];
}

function CasesTable({ cases }: Props) {
  if (cases.length === 0) {
    return <p className="text-sm text-slate-200">Nenhum caso/tema encontrado com os filtros atuais.</p>;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-white/5 bg-white/5 shadow-card">
      <table className="min-w-full divide-y divide-white/5">
        <thead className="bg-white/5">
          <tr className="text-left text-xs uppercase tracking-[0.2em] text-slate-300">
            <th className="px-4 py-3">Caso/Tema</th>
            <th className="px-4 py-3">Categoria</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Risco</th>
            <th className="px-4 py-3">Atualizado em</th>
            <th className="px-4 py-3">Diagnóstico</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {cases.map((item) => (
            <tr key={item.id} className="text-sm text-slate-100 hover:bg-white/5">
              <td className="px-4 py-3">
                <Link to={`/admin/cases/${item.id}`} className="font-semibold text-white hover:underline">
                  {item.title || item.id}
                </Link>
              </td>
              <td className="px-4 py-3 text-slate-200">{item.category || '—'}</td>
              <td className="px-4 py-3">
                <CaseStatusBadge status={item.status} />
              </td>
              <td className="px-4 py-3">
                <RiskBadge risk={item.risk} />
              </td>
              <td className="px-4 py-3 text-slate-200">{item.updated_at || '—'}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-2">
                  <Link
                    to={`/admin/cases/${item.id}/timeline`}
                    className="rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-xs font-semibold text-sky-200 hover:border-white/20"
                  >
                    Timeline
                  </Link>
                  <Link
                    to={`/admin/cases/${item.id}/xray`}
                    className="rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-xs font-semibold text-sky-200 hover:border-white/20"
                  >
                    Raio-X
                  </Link>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default CasesTable;
