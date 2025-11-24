import { useCallback, useEffect, useMemo, useState } from 'react';
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
import Button from '../../../shared/components/Button';
import { Link } from 'react-router-dom';

function AdminSourcesPage() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [sources, setSources] = useState<AdminSource[]>([]);
  const [healthFilter, setHealthFilter] = useState<'all' | 'OK' | 'DEGRADED' | 'FAIL'>('all');
  const [stateFilter, setStateFilter] = useState<'all' | AdminSource['state']>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
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
  }, [token, logEvent]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    logEvent('admin.page_open', { page: 'sources' });
  }, [logEvent]);

  const filtered = useMemo(() => {
    return sources.filter((src) => {
      if (healthFilter !== 'all' && src.last_health_status !== healthFilter) return false;
      if (stateFilter !== 'all' && src.state !== stateFilter) return false;
      return true;
    });
  }, [sources, healthFilter, stateFilter]);

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
            <p className="font-semibold text-white">Filtros</p>
            <p className="text-xs text-slate-300">Saúde e estado das fontes.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <select
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={healthFilter}
              onChange={(event) => setHealthFilter(event.target.value as typeof healthFilter)}
            >
              <option value="all">Saúde: Todas</option>
              <option value="OK">Saudáveis</option>
              <option value="DEGRADED">Em atenção</option>
              <option value="FAIL">Falhando</option>
            </select>
            <select
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={stateFilter}
              onChange={(event) => setStateFilter(event.target.value as typeof stateFilter)}
              >
              <option value="all">Estado: Todos</option>
              <option value="PROPOSED">Proposta</option>
              <option value="TESTING">Em teste</option>
              <option value="ACTIVE">Ativa</option>
              <option value="UNDER_REVIEW">Em revisão</option>
              <option value="SUSPECT">Suspeita</option>
              <option value="DISABLED_TEMP">Desativada temp.</option>
              <option value="DISABLED_PERM">Desativada perm.</option>
            </select>
            <Link to="/admin/sources/new">
              <Button variant="primary">Nova fonte</Button>
            </Link>
          </div>
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
