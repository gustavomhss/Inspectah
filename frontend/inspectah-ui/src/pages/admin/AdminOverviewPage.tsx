import { useEffect, useState } from 'react';
import { fetchHealth } from '../../api/admin';
import HealthSummaryCards from '../../components/admin/HealthSummaryCards';
import ErrorState from '../../components/admin/ErrorState';
import LoadingState from '../../components/admin/LoadingState';
import type { AdminHealth } from '../../types/admin';

function AdminOverviewPage() {
  const [health, setHealth] = useState<AdminHealth | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchHealth();
      setHealth(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  if (loading) {
    return <LoadingState label="Carregando saúde operacional..." />;
  }

  if (error || !health) {
    return <ErrorState message={error || 'Health indisponível'} onRetry={load} />;
  }

  return (
    <div className="space-y-6">
      <HealthSummaryCards health={health} />
      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <h3 className="text-lg font-semibold text-white">Resumos rápidos</h3>
        <ul className="mt-3 space-y-2 text-sm text-slate-200">
          <li>Fontes saudáveis: {health.sources_healthy}</li>
          <li>Fontes em atenção: {health.sources_degraded}</li>
          <li>Casos estáveis: {health.cases_stable}</li>
          <li>Casos em atenção/contestação: {health.cases_attention}</li>
        </ul>
      </div>
    </div>
  );
}

export default AdminOverviewPage;
