import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminSourceDetail } from '../../../core/api/api-types';
import { fetchHealthchecks, fetchSourceDetail, triggerSourceHealthcheck } from '../api';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import SourceStatusBadge from '../components/SourceStatusBadge';

function AdminSourceDetailPage() {
  const { sourceId } = useParams<{ sourceId: string }>();
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [source, setSource] = useState<AdminSourceDetail | null>(null);
  const [healthchecks, setHealthchecks] = useState<AdminSourceDetail['healthchecks']>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hcRunning, setHcRunning] = useState(false);

  const load = useCallback(async () => {
    if (!sourceId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchSourceDetail(sourceId, token || undefined);
      setSource(result);
      const hc = await fetchHealthchecks(sourceId, token || undefined);
      setHealthchecks(hc);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [sourceId, token]);

  const handleHealthcheck = async () => {
    if (!sourceId) return;
    setHcRunning(true);
    try {
      await triggerSourceHealthcheck(sourceId, token || undefined);
      await load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setHcRunning(false);
    }
  };

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
      <div className="flex items-center justify-between">
        <Link to="/admin/sources" className="text-sm font-semibold text-sky-200 hover:underline">
          ← Voltar para Fontes
        </Link>
        <button
          className="rounded-lg bg-white/10 px-3 py-2 text-sm font-semibold text-white hover:bg-white/20"
          onClick={handleHealthcheck}
          disabled={hcRunning}
        >
          {hcRunning ? 'Rodando health-check...' : 'Rodar health-check'}
        </button>
      </div>
      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Fonte</p>
            <h3 className="text-2xl font-bold text-white">{source.name}</h3>
            <p className="text-sm text-slate-200">{source.info_type || source.type}</p>
            <p className="text-xs text-slate-400">{source.url_base}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white">{source.state}</span>
            <SourceStatusBadge status={(source.last_health_status || 'unknown') as any} />
          </div>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <Stat label="Último health-check" value={source.last_health_at || '—'} />
          <Stat label="Erro recente" value={source.last_health_error || 'Nenhum erro recente'} />
          <Stat label="Temas" value={(source.themes || []).join(', ') || '—'} />
        </div>
      </div>

      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <h4 className="text-lg font-semibold text-white">Histórico de estados</h4>
        <div className="mt-3 space-y-2">
          {(!source.state_history || source.state_history.length === 0) && (
            <p className="text-sm text-slate-200">Sem histórico registrado.</p>
          )}
          {(source.state_history || []).map((entry, index) => (
            <div key={`${entry.created_at}-${index}`} className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 px-3 py-2">
              <div>
                <p className="text-sm text-white">
                  {entry.to_state} · {entry.reason || 'sem motivo'}
                </p>
                <p className="text-xs text-slate-300">{entry.created_at || 'Sem timestamp'}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <h4 className="text-lg font-semibold text-white">Health-checks</h4>
        <div className="mt-3 space-y-2">
          {(healthchecks || []).length === 0 && <p className="text-sm text-slate-200">Nenhum health-check registrado.</p>}
          {(healthchecks || []).map((entry, index) => (
            <div key={`${entry.checked_at}-${index}`} className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 px-3 py-2">
              <div>
                <p className="text-sm text-white">
                  {entry.status} · {entry.error || 'OK'}
                </p>
                <p className="text-xs text-slate-300">{entry.checked_at || 'Sem timestamp'}</p>
              </div>
              <SourceStatusBadge status={(entry.status || 'unknown') as any} />
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
