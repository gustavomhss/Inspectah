import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminSourceDetail } from '../../../core/api/api-types';
import { fetchSourceDetail } from '../api';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import SourceStatusBadge from '../components/SourceStatusBadge';

function AdminSourceDetailPage() {
  const { sourceId } = useParams<{ sourceId: string }>();
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [source, setSource] = useState<AdminSourceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!sourceId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchSourceDetail(sourceId, token || undefined);
      setSource(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [sourceId, token]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (sourceId) {
      logEvent('admin.page_open', { page: 'source_detail', sourceId });
    }
  }, [logEvent, sourceId]);

  if (loading) {
    return <LoadingState label="Carregando detalhes da fonte..." />;
  }

  if (error || !source) {
    return <ErrorState message={error || 'Fonte não encontrada'} onRetry={load} />;
  }

  return (
    <div className="space-y-4">
      <Link to="/admin/sources" className="text-sm font-semibold text-sky-200 hover:underline">
        ← Voltar para Fontes
      </Link>
      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Fonte</p>
            <h3 className="text-2xl font-bold text-white">{source.name}</h3>
            <p className="text-sm text-slate-200">{source.info_type || source.type}</p>
            <p className="text-xs text-slate-400">{source.url_base}</p>
          </div>
          <SourceStatusBadge status={source.status} />
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <Stat label="Itens recentes" value={source.recent_items_count} />
          <Stat label="Última coleta" value={source.last_checked_at || '—'} />
          <Stat label="Último erro" value={source.last_error || 'Nenhum erro recente'} />
        </div>
      </div>

      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <h4 className="text-lg font-semibold text-white">Histórico curto</h4>
        <div className="mt-3 space-y-2">
          {source.history.length === 0 && <p className="text-sm text-slate-200">Sem histórico registrado.</p>}
          {source.history.map((entry, index) => (
            <div key={`${entry.checked_at}-${index}`} className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 px-3 py-2">
              <div>
                <p className="text-sm text-white">{entry.checked_at || 'Sem timestamp'}</p>
                {entry.error && <p className="text-xs text-rose-200">{entry.error}</p>}
              </div>
              <SourceStatusBadge status={entry.status} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-white/5 bg-white/5 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-300">{label}</p>
      <p className="mt-2 text-lg font-semibold text-white">{value}</p>
    </div>
  );
}

export default AdminSourceDetailPage;
