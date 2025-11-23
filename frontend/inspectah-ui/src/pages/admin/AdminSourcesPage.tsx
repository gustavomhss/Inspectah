import { useEffect, useMemo, useState } from 'react';
import { fetchSources } from '../../api/admin';
import EmptyState from '../../components/admin/EmptyState';
import ErrorState from '../../components/admin/ErrorState';
import LoadingState from '../../components/admin/LoadingState';
import SourcesTable from '../../components/admin/SourcesTable';
import type { AdminSource } from '../../types/admin';

function AdminSourcesPage() {
  const [sources, setSources] = useState<AdminSource[]>([]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'healthy' | 'degraded'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchSources();
      setSources(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

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
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-white">Fontes</h3>
          <p className="text-sm text-slate-200">Lista consolidada a partir do backend do Inspectah.</p>
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

      {filtered.length === 0 ? (
        <EmptyState title="Nenhuma fonte" description="Aplique outros filtros ou verifique o backend de admin." />
      ) : (
        <SourcesTable sources={filtered} />
      )}
    </div>
  );
}

export default AdminSourcesPage;
