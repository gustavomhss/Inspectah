import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { fetchSourceDetail } from '../../admin/api';
import type { AdminSource, IngestionMode } from '../../../core/api/api-types';
import PageHeader from '../../../shared/layout/PageHeader';
import PageContainer from '../../../shared/layout/PageContainer';
import LoadingState from '../../admin/components/LoadingState';
import ErrorState from '../../admin/components/ErrorState';
import Button from '../../../shared/components/Button';
import Card from '../../../shared/components/Card';
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
  const { runs, configMode, loading: runsLoading, error: runsError, reload: reloadRuns } = useIngestionRuns(sourceId);
  const [progress, setProgress] = useState(0);

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
            : 'Não foi possível iniciar a ingestão.';
      setMessage({ tone: 'danger', text });
    }
  };

  const handleToggleMode = async (nextMode: IngestionMode) => {
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
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="space-y-1">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Configuração</p>
                <div className="flex items-center gap-3 text-sm text-white">
                  <IngestionModeBadge mode={mode} onToggle={handleToggleMode} />
                  <span className="text-xs text-slate-300">Estado: </span>
                  <IngestionStatusBadge status={lastRun?.status} showNever={!lastRun} />
                </div>
                <div className="text-xs text-slate-300">
                  Última ingestão: {lastRun?.finished_at ? new Date(lastRun.finished_at).toLocaleString() : 'Nunca rodou'}
                </div>
              </div>
              <Button variant="primary" onClick={handleRunNow}>
                Rodar ingestão agora
              </Button>
            </div>
            <div className="mt-3">
              <IngestionProgressBar status={lastRun?.status} progress={progress} lastRun={lastRun} />
            </div>
          </Card>

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
