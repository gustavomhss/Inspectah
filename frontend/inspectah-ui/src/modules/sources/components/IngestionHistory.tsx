/**
 * S38-FE-012: IngestionHistory Component
 */

import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import type { IngestionRun } from '../types';
import * as api from '../api/sourcesApi';

interface IngestionHistoryProps {
  sourceId: string;
  limit?: number;
}

const statusColors: Record<string, string> = {
  COMPLETED: 'bg-green-500',
  RUNNING: 'bg-blue-500',
  PENDING: 'bg-yellow-500',
  FAILED: 'bg-red-500',
};

const statusLabels: Record<string, string> = {
  COMPLETED: 'Concluido',
  RUNNING: 'Executando',
  PENDING: 'Pendente',
  FAILED: 'Falhou',
};

const triggerLabels: Record<string, string> = {
  MANUAL: 'Manual',
  SCHEDULED: 'Agendado',
  WEBHOOK: 'Webhook',
};

export default function IngestionHistory({ sourceId, limit = 10 }: IngestionHistoryProps) {
  const { token } = useAuth();
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({ limit, offset: 0, total: 0 });

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getIngestionHistory(
        sourceId,
        { limit: pagination.limit, offset: pagination.offset },
        token || undefined
      );
      setRuns(result.runs);
      setPagination(result.pagination);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [sourceId, pagination.limit, pagination.offset, token]);

  useEffect(() => {
    void fetchHistory();
  }, [fetchHistory]);

  if (loading && runs.length === 0) {
    return (
      <div className="animate-pulse rounded-lg border border-white/10 bg-white/5 p-4">
        <div className="h-4 w-32 rounded bg-white/10" />
        <div className="mt-4 space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 rounded bg-white/10" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
        <p className="text-sm text-red-400">Erro ao carregar historico: {error}</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Historico de Ingestao</h3>
        <button
          onClick={() => void fetchHistory()}
          className="text-sm text-blue-400 hover:text-blue-300"
          disabled={loading}
        >
          {loading ? 'Atualizando...' : 'Atualizar'}
        </button>
      </div>

      {runs.length === 0 ? (
        <p className="mt-4 text-sm text-slate-400">Nenhuma ingestao registrada.</p>
      ) : (
        <>
          <div className="mt-4 space-y-2">
            {runs.map((run) => (
              <IngestionRunItem key={run.run_id} run={run} />
            ))}
          </div>

          {pagination.total > pagination.limit && (
            <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-4">
              <span className="text-sm text-slate-400">
                Mostrando {runs.length} de {pagination.total}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPagination((p) => ({ ...p, offset: Math.max(0, p.offset - p.limit) }))}
                  disabled={pagination.offset === 0}
                  className="rounded px-3 py-1 text-sm text-slate-400 hover:text-white disabled:opacity-50"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setPagination((p) => ({ ...p, offset: p.offset + p.limit }))}
                  disabled={pagination.offset + pagination.limit >= pagination.total}
                  className="rounded px-3 py-1 text-sm text-slate-400 hover:text-white disabled:opacity-50"
                >
                  Proximo
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

interface IngestionRunItemProps {
  run: IngestionRun;
}

function IngestionRunItem({ run }: IngestionRunItemProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-white/10 bg-white/5 p-3">
      <div className="flex items-center gap-3">
        <span className={`h-2 w-2 rounded-full ${statusColors[run.status] || 'bg-gray-500'}`} />
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-white">
              {statusLabels[run.status] || run.status}
            </span>
            <span className="text-xs text-slate-500">
              {triggerLabels[run.trigger] || run.trigger}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>{new Date(run.started_at).toLocaleString('pt-BR')}</span>
            {run.duration_seconds && (
              <span>({formatDuration(run.duration_seconds)})</span>
            )}
          </div>
        </div>
      </div>

      <div className="text-right">
        <p className="text-sm font-medium text-white">
          {run.documents_processed.toLocaleString()} docs
        </p>
        {run.error_message && (
          <p className="text-xs text-red-400 max-w-[200px] truncate" title={run.error_message}>
            {run.error_message}
          </p>
        )}
      </div>
    </div>
  );
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}m ${secs}s`;
}
