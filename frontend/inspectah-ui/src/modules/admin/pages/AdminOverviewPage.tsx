import { useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminHealth } from '../../../core/api/api-types';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import { fetchHealth } from '../api';
import ErrorState from '../components/ErrorState';
import HealthSummaryCards from '../components/HealthSummaryCards';
import LoadingState from '../components/LoadingState';

function AdminOverviewPage() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [health, setHealth] = useState<AdminHealth | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchHealth(token || undefined);
      setHealth(result);
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('admin.action_error', { page: 'dashboard', message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [token]);

  useEffect(() => {
    logEvent('admin.page_open', { page: 'dashboard' });
  }, [logEvent]);

  if (loading) {
    return <LoadingState label="Carregando saúde operacional..." />;
  }

  if (error || !health) {
    return <ErrorState message={error || 'Health indisponível'} onRetry={load} />;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Visão geral do Admin"
        subtitle="Saúde do sistema, fontes e casos em um único painel."
      />
      <PageContainer>
        <HealthSummaryCards health={health} />
      </PageContainer>
      <PageContainer>
        <h3 className="text-lg font-semibold text-white">Resumos rápidos</h3>
        <ul className="mt-3 space-y-2 text-sm text-slate-200">
          <li>Fontes saudáveis: {health.sources_healthy}</li>
          <li>Fontes em atenção: {health.sources_degraded}</li>
          <li>Casos estáveis: {health.cases_stable}</li>
          <li>Casos em atenção/contestação: {health.cases_attention}</li>
        </ul>
      </PageContainer>
    </div>
  );
}

export default AdminOverviewPage;
