import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminCase } from '../../../core/api/api-types';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import { fetchCases } from '../api';
import CasesTable from '../components/CasesTable';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';

function AdminCasesPage() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [cases, setCases] = useState<AdminCase[]>([]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'attention' | 'stable'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchCases(token || undefined);
      setCases(result);
    } catch (err) {
      const message = (err as Error).message;
      setError(message);
      logEvent('admin.action_error', { page: 'cases', message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [token]);

  useEffect(() => {
    logEvent('admin.page_open', { page: 'cases' });
  }, [logEvent]);

  const filtered = useMemo(() => {
    if (statusFilter === 'all') return cases;
    if (statusFilter === 'stable') {
      return cases.filter((c) => (c.status || '').toLowerCase() === 'estavel');
    }
    return cases.filter((c) => (c.status || '').toLowerCase() !== 'estavel');
  }, [cases, statusFilter]);

  if (loading) {
    return <LoadingState label="Carregando casos/temas..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Casos/Temas"
        subtitle="Estados consolidados dos casos monitorados pelo Inspectah, com links para timeline e raio-X."
      />
      <PageContainer>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-slate-200">
            <p className="font-semibold text-white">Filtrar por estado</p>
            <p className="text-xs text-slate-300">Use para destacar casos estáveis ou em atenção.</p>
          </div>
          <select
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value as typeof statusFilter)}
          >
            <option value="all">Todos</option>
            <option value="stable">Estáveis</option>
            <option value="attention">Em atenção/contestação</option>
          </select>
        </div>

        <div className="mt-4">
          {filtered.length === 0 ? (
            <EmptyState title="Nenhum caso/tema" description="Sem casos que correspondam aos filtros atuais." />
          ) : (
            <CasesTable cases={filtered} />
          )}
        </div>
      </PageContainer>
    </div>
  );
}

export default AdminCasesPage;
