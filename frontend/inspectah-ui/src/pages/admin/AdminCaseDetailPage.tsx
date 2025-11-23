import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { fetchCaseDetail } from '../../api/admin';
import CaseStatusBadge from '../../components/admin/CaseStatusBadge';
import ErrorState from '../../components/admin/ErrorState';
import LoadingState from '../../components/admin/LoadingState';
import RiskBadge from '../../components/admin/RiskBadge';
import type { AdminCaseDetail } from '../../types/admin';

function AdminCaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const [entry, setEntry] = useState<AdminCaseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchCaseDetail(caseId);
      setEntry(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return <LoadingState label="Carregando caso/tema..." />;
  }

  if (error || !entry) {
    return <ErrorState message={error || 'Caso não encontrado'} onRetry={load} />;
  }

  return (
    <div className="space-y-4">
      <Link to="/admin/cases" className="text-sm font-semibold text-sky-200 hover:underline">
        ← Voltar para Casos/Temas
      </Link>
      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Caso/Tema</p>
            <h3 className="text-2xl font-bold text-white">{entry.title}</h3>
            <p className="text-sm text-slate-200">{entry.category}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <CaseStatusBadge status={entry.status} />
            <RiskBadge risk={entry.risk} />
            <Link
              to={`/admin/cases/${entry.id}/timeline`}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-sky-200 hover:border-white/20"
            >
              Ver timeline
            </Link>
            <Link
              to={`/admin/cases/${entry.id}/xray`}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-sky-200 hover:border-white/20"
            >
              Ver raio-X
            </Link>
          </div>
        </div>
        <p className="mt-3 text-sm text-slate-200">{entry.description || 'Sem descrição disponível.'}</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Stat label="Atualizado em" value={entry.updated_at || '—'} />
          <Stat label="Fontes principais" value={entry.key_sources.join(', ') || '—'} />
        </div>
      </div>

      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <h4 className="text-lg font-semibold text-white">Principais evidências</h4>
        <div className="mt-3 space-y-2">
          {entry.top_evidence.length === 0 && <p className="text-sm text-slate-200">Nenhuma evidência agregada.</p>}
          {entry.top_evidence.map((ev, index) => (
            <div key={index} className="rounded-lg border border-white/5 bg-white/5 p-3 text-sm text-slate-100">
              <pre className="whitespace-pre-wrap break-words text-xs text-slate-200">{JSON.stringify(ev, null, 2)}</pre>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/5 bg-white/5 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-300">{label}</p>
      <p className="mt-2 text-lg font-semibold text-white">{value}</p>
    </div>
  );
}

export default AdminCaseDetailPage;
