import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminSource } from '../../../core/api/api-types';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import { fetchSources } from '../api';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import SourcesTable from '../components/SourcesTable';

function AdminSourcesPage() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [sources, setSources] = useState<AdminSource[]>([]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'healthy' | 'degraded'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchSources(token || undefined);
      setSources(result);
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('admin.action_error', { page: 'sources', message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [token]);

  useEffect(() => {
    logEvent('admin.page_open', { page: 'sources' });
  }, [logEvent]);

  const filtered = useMemo(() => {
    if (statusFilter === 'all') return sources;
    return sources.filter((src) => src.status === statusFilter);
  }, [sources, statusFilter]);

  if (loading) {
    return <LoadingState label="Carregando fontes..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Fontes"
        subtitle="Lista consolidada de fontes do backend do Inspectah, com estado de saúde por origem."
      />
      <PageContainer>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-slate-200">
            <p className="font-semibold text-white">Filtrar por saúde</p>
            <p className="text-xs text-slate-300">Destaque fontes saudáveis ou em atenção.</p>
          </div>
          <select
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value as typeof statusFilter)}
          >
            <option value="all">Todas</option>
            <option value="healthy">Saudáveis</option>
            <option value="degraded">Em atenção</option>
          </select>
        </div>

        <div className="mt-4">
          {filtered.length === 0 ? (
            <EmptyState title="Nenhuma fonte" description="Aplique outros filtros ou verifique o backend de admin." />
          ) : (
            <SourcesTable sources={filtered} />
          )}
        </div>
      </PageContainer>
    </div>
  );
}

export default AdminSourcesPage;
