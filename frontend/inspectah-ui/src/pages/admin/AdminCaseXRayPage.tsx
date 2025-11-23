import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getAdminCaseXRay } from '../../api/admin';
import CaseXRayLayout from '../../components/admin/xray/CaseXRayLayout';
import EmptyState from '../../components/admin/EmptyState';
import ErrorState from '../../components/admin/ErrorState';
import LoadingState from '../../components/admin/LoadingState';
import type { AdminCaseXRay } from '../../types/admin';

function AdminCaseXRayPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const [xray, setXray] = useState<AdminCaseXRay | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getAdminCaseXRay(caseId);
      setXray(data);
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
    return <LoadingState label="Carregando raio-X do caso..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  if (!xray) {
    return <EmptyState title="Raio-X indisponível" description="Não encontramos o raio-X deste caso." />;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3 text-sm font-semibold text-sky-200">
          <Link to="/admin/cases" className="hover:underline">
            ← Voltar para Casos/Temas
          </Link>
          <span className="text-slate-400">/</span>
          <Link to={`/admin/cases/${xray.case_id}`} className="hover:underline">
            Detalhe do caso
          </Link>
        </div>
        <Link
          to={`/admin/cases/${xray.case_id}/timeline`}
          className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm font-semibold text-sky-200 hover:border-white/20"
        >
          Ver timeline →
        </Link>
      </div>
      <CaseXRayLayout xray={xray} />
    </div>
  );
}

export default AdminCaseXRayPage;
