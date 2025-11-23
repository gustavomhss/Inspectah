import { useEffect, useMemo, useState } from 'react';
import { fetchCases } from '../../api/admin';
import CasesTable from '../../components/admin/CasesTable';
import EmptyState from '../../components/admin/EmptyState';
import ErrorState from '../../components/admin/ErrorState';
import LoadingState from '../../components/admin/LoadingState';
import type { AdminCase } from '../../types/admin';

function AdminCasesPage() {
  const [cases, setCases] = useState<AdminCase[]>([]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'attention' | 'stable'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchCases();
      setCases(result);
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
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-white">Casos/Temas</h3>
          <p className="text-sm text-slate-200">Estados consolidados dos casos monitorados pelo Inspectah.</p>
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

      {filtered.length === 0 ? (
        <EmptyState title="Nenhum caso/tema" description="Sem casos que correspondam aos filtros atuais." />
      ) : (
        <CasesTable cases={filtered} />
      )}
    </div>
  );
}

export default AdminCasesPage;
