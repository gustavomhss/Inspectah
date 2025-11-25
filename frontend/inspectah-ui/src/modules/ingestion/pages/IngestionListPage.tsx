import { useMemo, useState } from 'react';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import LoadingState from '../../admin/components/LoadingState';
import ErrorState from '../../admin/components/ErrorState';
import Button from '../../../shared/components/Button';
import type { IngestionMode } from '../../../core/api/api-types';
import { useIngestionSources } from '../hooks/useIngestionSources';
import IngestionFiltersBar from '../components/IngestionFiltersBar';
import IngestionSourceTable from '../components/IngestionSourceTable';
import Toast from '../../../shared/components/Toast';
import { HttpError } from '../../../core/api/http-client';

function IngestionListPage() {
  const { rows, loading, error, reload, runNow, changeMode } = useIngestionSources();
  const [typeFilter, setTypeFilter] = useState<'all' | string>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'SUCCESS' | 'FAIL' | 'RUNNING' | 'NEVER'>('all');
  const [search, setSearch] = useState('');
  const [message, setMessage] = useState<{ tone: 'success' | 'danger'; text: string } | null>(null);
  const [runningIds, setRunningIds] = useState<Set<string>>(new Set());

  const types = useMemo(() => rows.map((r) => r.source.type), [rows]);

  const filtered = useMemo(() => {
    return rows.filter((row) => {
      if (typeFilter !== 'all' && row.source.type !== typeFilter) return false;
      if (search && !row.source.name?.toLowerCase().includes(search.toLowerCase())) return false;
      if (statusFilter === 'SUCCESS' && row.lastRun?.status !== 'SUCCESS') return false;
      if (statusFilter === 'FAIL' && row.lastRun?.status !== 'FAIL') return false;
      if (statusFilter === 'RUNNING' && row.lastRun?.status !== 'RUNNING') return false;
      if (statusFilter === 'NEVER' && row.lastRun) return false;
      return true;
    });
  }, [rows, typeFilter, search, statusFilter]);

  const handleRun = async (sourceId: string) => {
    setRunningIds((prev) => new Set(prev).add(sourceId));
    setMessage(null);
    try {
      await runNow(sourceId);
      setMessage({ tone: 'success', text: `Ingestão iniciada para ${sourceId}.` });
    } catch (err) {
      const status = err instanceof HttpError ? err.status : undefined;
      const base =
        status === 409
          ? 'Já existe uma ingestão em andamento para esta fonte.'
          : status === 404
            ? 'Fonte ou ingestão não encontrada.'
            : 'Não foi possível iniciar a ingestão. Tente novamente.';
      setMessage({ tone: 'danger', text: base });
    } finally {
      setRunningIds((prev) => {
        const next = new Set(prev);
        next.delete(sourceId);
        return next;
      });
    }
  };

  const handleToggleMode = async (sourceId: string, mode: IngestionMode) => {
    setMessage(null);
    try {
      await changeMode(sourceId, mode);
      setMessage({ tone: 'success', text: 'Modo de ingestão atualizado.' });
    } catch (err) {
      const status = err instanceof HttpError ? err.status : undefined;
      const base =
        status === 409
          ? 'Configuração incompatível para a fonte.'
          : status === 404
            ? 'Fonte não encontrada.'
            : 'Não foi possível alterar o modo.';
      setMessage({ tone: 'danger', text: base });
    }
  };

  if (loading) return <LoadingState label="Carregando ingestão..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;

  return (
    <div className="space-y-4">
      <PageHeader title="Ingestão" subtitle="Status de ingestão por fonte" />
      <PageContainer>
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <IngestionFiltersBar
              types={types}
              selectedType={typeFilter}
              onTypeChange={setTypeFilter}
              statusFilter={statusFilter}
              onStatusChange={setStatusFilter}
              search={search}
              onSearchChange={setSearch}
            />
            <Button variant="ghost" onClick={() => reload()}>
              Atualizar
            </Button>
          </div>
          {message ? <Toast tone={message.tone} title={message.text} /> : null}
          <IngestionSourceTable rows={filtered} onRun={handleRun} onToggleMode={handleToggleMode} runningIds={runningIds} />
        </div>
      </PageContainer>
    </div>
  );
}

export default IngestionListPage;
