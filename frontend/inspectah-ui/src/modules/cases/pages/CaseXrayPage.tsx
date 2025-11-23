import { useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import EmptyState from '../../admin/components/EmptyState';
import ErrorState from '../../admin/components/ErrorState';
import LoadingState from '../../admin/components/LoadingState';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import CaseXRayLayout from '../components/xray/CaseXRayLayout';
import { useCaseXray } from '../hooks/useCaseXray';

function CaseXrayPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const { xray, load, loading, error } = useCaseXray(caseId);

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
      <PageHeader
        title={`Raio-X do caso ${xray.case_id}`}
        subtitle="Detalhe profundo com debunker, comitês, âncoras e evidências do caso."
        actions={
          <Link
            to={`/admin/cases/${xray.case_id}/timeline`}
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm font-semibold text-sky-200 hover:border-white/20"
          >
            Ver timeline →
          </Link>
        }
      />
      <PageContainer>
        <div className="flex flex-wrap items-center gap-3 text-sm font-semibold text-sky-200">
          <Link to="/admin/cases" className="hover:underline">
            ← Voltar para Casos/Temas
          </Link>
          <span className="text-slate-400">/</span>
          <Link to={`/admin/cases/${xray.case_id}`} className="hover:underline">
            Detalhe do caso
          </Link>
        </div>
        <div className="mt-4">
          <CaseXRayLayout xray={xray} />
        </div>
      </PageContainer>
    </div>
  );
}

export default CaseXrayPage;
