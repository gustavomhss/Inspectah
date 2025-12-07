import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { fetchSourceDetail } from '../../admin/api';
import type { AdminSource, IngestionMode } from '../../../core/api/api-types';
import PageHeader from '../../../shared/layout/PageHeader';
import PageContainer from '../../../shared/layout/PageContainer';
import LoadingState from '../../admin/components/LoadingState';
import ErrorState from '../../admin/components/ErrorState';
import Button from '../../../shared/components/Button';
import UiCard from '../../../shared/components/Card';
import { useIngestionRuns } from '../hooks/useIngestionRuns';
import { runIngestionNow, toggleIngestionMode } from '../api/ingestionApi';
import { useAuth } from '../../../app/providers/AuthProvider';
import Toast from '../../../shared/components/Toast';
import IngestionRunHistoryTable from '../components/IngestionRunHistoryTable';
import IngestionTimeline from '../components/IngestionTimeline';
import IngestionRunDetailModal from '../components/IngestionRunDetailModal';
import IngestionModeBadge from '../components/IngestionModeBadge';
import IngestionStatusBadge from '../components/IngestionStatusBadge';
import IngestionProgressBar from '../components/IngestionProgressBar';
import { HttpError } from '../../../core/api/http-client';

function IngestionSourceDetailPage() {
  const { sourceId = '' } = useParams<{ sourceId: string }>();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [source, setSource] = useState<AdminSource | null>(null);
  const [mode, setMode] = useState<IngestionMode>('MANUAL_ONLY');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<{ tone: 'success' | 'danger'; text: string } | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const isProvider = source?.slug === 'newsdata_br' || source?.id === 'newsdata_br';
  const metaProvider = (source?.meta as Record<string, unknown> | undefined)?.provider_id;
  const isDerived = Boolean(
    source &&
      !isProvider &&
      (source.provider_id === 'newsdata_br' || metaProvider === 'newsdata_br' || !source.ingestion_mode || source.ingestion_mode === 'DERIVED'),
  );
  const { runs, configMode, loading: runsLoading, error: runsError, reload: reloadRuns } = useIngestionRuns(sourceId, {
    enabled: source ? !isDerived : false,
  });
  const [progress, setProgress] = useState(0);
  const isOpsOnly = sourceId.includes('newsdata') || Boolean(isProvider);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const detail = await fetchSourceDetail(sourceId, token || undefined);
        setSource(detail);
        setMode(detail.ingestion_mode || 'MANUAL_ONLY');
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [sourceId, token]);

  useEffect(() => {
    if (configMode) {
      setMode(configMode);
    }
  }, [configMode]);

  const lastRun = useMemo(() => {
    if (!runs.length) return undefined;
    return [...runs].sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())[0];
  }, [runs]);

  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | null = null;
    if (!lastRun) {
      setProgress(0);
      return () => undefined;
    }
    if (lastRun.status === 'RUNNING') {
      const started = lastRun.started_at ? new Date(lastRun.started_at).getTime() : Date.now();
      const elapsedMs = Date.now() - started;
      const expectedMs = 60_000; // heurística: ingestões curtas
      const initial = Math.min(90, Math.max(15, 15 + (elapsedMs / expectedMs) * 70));
      setProgress(initial);
      timer = setInterval(() => {
        setProgress((prev) => Math.min(prev + 5, 90));
      }, 1500);
    } else {
      setProgress(100);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [lastRun]);

  const handleRunNow = async () => {
    setMessage(null);
    if (isDerived) {
      setMessage({ tone: 'danger', text: 'Fonte derivada do provedor (sem pipeline próprio).' });
      return;
    }
    try {
      await runIngestionNow(sourceId, token || undefined);
      setMessage({ tone: 'success', text: `Ingestão iniciada para ${source?.name || sourceId}.` });
      await reloadRuns();
    } catch (err) {
      const status = err instanceof HttpError ? err.status : undefined;
      const text =
        status === 409
          ? 'Já existe uma ingestão em andamento para esta fonte.'
          : status === 404
            ? 'Fonte ou ingestão não encontrada.'
            : status === 429
              ? 'Fonte externa limitou requisições (429). Aguarde e tente novamente.'
            : status && status >= 500
              ? 'Erro na fonte externa (5xx). Tente após alguns minutos.'
            : status && status >= 400
              ? 'Erro na fonte externa (4xx). Verifique limites ou credenciais.'
            : 'Não foi possível iniciar a ingestão.';
      setMessage({ tone: 'danger', text });
    }
  };

  const handleToggleMode = async (nextMode: IngestionMode) => {
    if (isOpsOnly || isDerived) {
      setMessage({ tone: 'danger', text: 'Modo fixo para newsdata_br (ops_only).' });
      return;
    }
    try {
      const config = await toggleIngestionMode(sourceId, nextMode, token || undefined);
      setMode(config.mode);
      setMessage({ tone: 'success', text: 'Modo de ingestão atualizado.' });
    } catch (err) {
      setMessage({ tone: 'danger', text: 'Erro ao alterar modo.' });
    }
  };

  if (loading) return <LoadingState label="Carregando ingestão..." />;
  if (error) return <ErrorState message={error} onRetry={() => navigate('/admin/ingestion')} />;
  if (!source) return null;

  const lastMeta = (lastRun?.meta as Record<string, unknown>) || {};
  const attemptCount = Array.isArray(lastMeta.attempts) ? lastMeta.attempts.length : undefined;
  const derivedDomains = Array.isArray(lastMeta.domains) ? (lastMeta.domains as string[]) : [];
  const canRetry = lastRun?.status && ['FAIL', 'PARTIAL_SUCCESS'].includes(lastRun.status);
  const summary: Array<{ label: string; value: string }> = [
    { label: 'Fonte', value: source.slug || source.id },
    { label: 'Status', value: lastRun?.status ?? '—' },
    { label: 'Itens processados', value: String(lastRun?.items_processed ?? '—') },
    { label: 'Requests', value: String(lastMeta.requests_count ?? attemptCount ?? '—') },
    { label: 'Size total', value: String(lastMeta.requested_size ?? '—') },
    { label: 'Size por requisição', value: String(lastMeta.per_request_size ?? '—') },
    { label: 'Throttle (s)', value: String(lastMeta.throttle_seconds ?? '—') },
    { label: 'Domínios', value: Array.isArray(lastMeta.domains) ? lastMeta.domains.join(', ') : String(lastMeta.domains ?? '—') },
    { label: 'Trigger', value: String(lastMeta.trigger_origin ?? 'admin_ui') },
  ];

  return (
    <div className="space-y-4">
      <PageHeader title={source.name || source.id} subtitle={`Ingestão / ${source.type}`}>
        <Link to="/admin/ingestion" className="text-sm font-semibold text-sky-200 hover:underline">
          ← Voltar
        </Link>
      </PageHeader>
      <PageContainer>
        <div className="space-y-4">
          {message ? <Toast tone={message.tone} title={message.text} /> : null}
          <UiCard>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="space-y-1">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Configuração</p>
                <div className="flex items-center gap-3 text-sm text-white">
                  <IngestionModeBadge mode={isDerived ? 'DERIVED' : mode} onToggle={isOpsOnly || isDerived ? undefined : handleToggleMode} />
                  <span className="text-xs text-slate-300">Estado: </span>
                  <IngestionStatusBadge status={lastRun?.status} showNever={!lastRun} />
                </div>
                <div className="text-xs text-slate-300">
                  Última ingestão: {lastRun?.finished_at ? new Date(lastRun.finished_at).toLocaleString() : isDerived ? 'Derivada (sem execuções)' : 'Nunca rodou'}
                </div>
                {isOpsOnly ? <p className="text-[11px] text-amber-200">newsdata_br é ops-only; modo fixo e histórico só leitura.</p> : null}
                {isDerived ? <p className="text-[11px] text-amber-200">Fonte derivada do provedor newsdata_br (sem pipeline individual).</p> : null}
              </div>
              <div className="flex flex-wrap items-center gap-2">
                {isDerived ? (
                  <span className="text-xs text-slate-400">Controlada pelo provedor newsdata_br</span>
                ) : canRetry ? (
                  <span className="text-xs text-amber-200">Histórico é só leitura; retry liberado para falha.</span>
                ) : (
                  <span className="text-xs text-slate-300">Histórico somente leitura.</span>
                )}
                <Button variant="primary" onClick={handleRunNow} disabled={isDerived}>
                  {isDerived ? 'Controlada pelo provedor' : canRetry ? 'Tentar novamente' : 'Rodar ingestão agora'}
                </Button>
              </div>
            </div>
            <div className="mt-3">
              <IngestionProgressBar status={lastRun?.status} progress={progress} lastRun={lastRun} />
            </div>
          </UiCard>
          {!isDerived ? (
            <UiCard>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Resumo do último run</p>
              <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-slate-100 lg:grid-cols-3">
                {summary.map((entry) => (
                  <div key={entry.label} className="rounded-md border border-white/5 bg-white/5 px-3 py-2">
                    <p className="text-[11px] uppercase tracking-wide text-slate-400">{entry.label}</p>
                    <p className="break-all text-white">{entry.value}</p>
                  </div>
                ))}
              </div>
              {lastRun?.error_message ? (
                <div className="mt-3 rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">
                  Erro do último run: {lastRun.error_message}
                </div>
              ) : null}
            </UiCard>
          ) : null}

          {!isDerived ? (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                {runsError ? <ErrorState message={runsError} onRetry={reloadRuns} /> : null}
                {runsLoading ? (
                  <LoadingState label="Carregando histórico..." />
                ) : (
                  <IngestionRunHistoryTable runs={runs} onSelectRun={(run) => setSelectedRunId(run.id)} />
                )}
              </div>
              <div className="lg:col-span-1">
                <IngestionTimeline runs={runs} onSelectRun={(run) => setSelectedRunId(run.id)} />
              </div>
            </div>
          ) : (
            <UiCard>
              <p className="text-sm text-slate-200">Histórico não disponível. Fonte derivada controlada pelo provedor newsdata_br.</p>
            </UiCard>
          )}
          {isProvider ? (
            <UiCard className="overflow-hidden">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Fontes derivadas (newsdata_br)</p>
              <p className="text-xs text-slate-300">
                Domínios capturados do provedor newsdata_br (somente leitura; controlados pelo provedor). Cada domínio representa uma fonte derivada.
              </p>
              {derivedDomains.length === 0 ? (
                <div className="mt-3 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-200">
                  Nenhuma derivada carregada neste run. Rode ingestão para popular a lista.
                </div>
              ) : (
                <div className="mt-3 overflow-x-auto">
                  <table className="min-w-full divide-y divide-white/5">
                    <thead className="bg-white/5 text-left text-[11px] uppercase tracking-[0.2em] text-slate-300">
                      <tr>
                        <th className="px-3 py-2">Domínio</th>
                        <th className="px-3 py-2">Origem</th>
                        <th className="px-3 py-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {derivedDomains.map((domain) => (
                        <tr key={domain} className="text-sm text-slate-100">
                          <td className="px-3 py-2">{domain}</td>
                          <td className="px-3 py-2 text-xs text-slate-300">Derivada do provedor newsdata_br</td>
                          <td className="px-3 py-2 text-xs text-slate-200">Somente leitura</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </UiCard>
          ) : null}
        </div>
      </PageContainer>
      <IngestionRunDetailModal
        run={runs.find((r) => r.id === selectedRunId) || null}
        open={Boolean(selectedRunId)}
        onClose={() => setSelectedRunId(null)}
      />
    </div>
  );
}

export default IngestionSourceDetailPage;
