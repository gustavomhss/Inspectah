import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AdminContent, AdminHeader, Banner, Button } from '@/ui/admin';
import { SourceForm, type SourceFormValues } from '../components/SourceForm';
import { SourceStatusBadge } from '../components/SourceStatusBadge';
import { SourceHealthBadge } from '../components/SourceHealthBadge';
import type { Source } from '../types/Source';
import {
  activateSource,
  archiveSource,
  createSource,
  deactivateSource,
  getSourceById,
  updateSource,
  pauseIngestion,
  resumeIngestion,
  triggerManualRun,
} from '../api/sourcesApi';

export function SourceEditPage() {
  const navigate = useNavigate();
  const { sourceId } = useParams();
  const isNew = !sourceId || sourceId === 'new';
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [source, setSource] = useState<Source | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    if (isNew) {
      setSource(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getSourceById(sourceId!)
      .then((data) => setSource(data))
      .catch((err) => {
        const message = err instanceof Error ? err.message : 'Erro ao carregar fonte';
        setError(message);
      })
      .finally(() => setLoading(false));
  }, [isNew, sourceId]);

  const initialValues = useMemo<SourceFormValues>(
    () => ({
      slug: source?.slug ?? '',
      name: source?.name ?? '',
      type: source?.type ?? 'news_rss',
      category: source?.category ?? 'general',
      description: source?.description ?? '',
      endpoint: source?.endpoint ?? source?.url_base ?? '',
      state: source?.state ?? 'PROPOSED',
      themes: source?.themes ?? [],
      info_types: source?.info_types ?? [],
      refresh_interval: source?.refresh_interval ?? 1440,
    }),
    [source],
  );

  const handleSubmit = (values: SourceFormValues) => {
    setSaving(true);
    setError(null);
    setFeedback(null);
    const action = isNew ? createSource(values) : updateSource(sourceId!, values);
    action
      .then((result) => {
        setSource(result);
        setFeedback(isNew ? 'Fonte criada com sucesso.' : 'Fonte atualizada com sucesso.');
        if (isNew) {
          navigate(`/admin/sources/${result.id}`);
        }
      })
      .catch((err) => {
        const message = err instanceof Error ? err.message : 'Erro ao salvar fonte';
        setError(message);
      })
      .finally(() => setSaving(false));
  };

  const handleChangeState = (action: 'activate' | 'deactivate' | 'archive') => {
    if (!sourceId || isNew) return;
    setSaving(true);
    setError(null);
    setFeedback(null);
    const promise =
      action === 'activate' ? activateSource(sourceId) : action === 'deactivate' ? deactivateSource(sourceId) : archiveSource(sourceId);
    promise
      .then((updated) => {
        setSource(updated);
        setFeedback('Estado atualizado com sucesso.');
      })
      .catch((err) => {
        const message = err instanceof Error ? err.message : 'Erro ao atualizar estado';
        setError(message);
      })
      .finally(() => setSaving(false));
  };

  const handleIngestionAction = (action: 'pause' | 'resume' | 'run') => {
    if (!sourceId || isNew) return;
    setSaving(true);
    setError(null);
    setFeedback(null);
    const promise =
      action === 'pause'
        ? pauseIngestion(sourceId)
        : action === 'resume'
          ? resumeIngestion(sourceId)
          : triggerManualRun(sourceId);
    promise
      .then((result) => {
        setFeedback(
          action === 'run'
            ? `Ingestão manual disparada. Status: ${result && typeof result === 'object' && 'status' in result ? result.status : 'desconhecido'}.`
            : action === 'pause'
              ? 'Ingestão pausada.'
              : 'Ingestão retomada.',
        );
      })
      .catch((err) => {
        const message = err instanceof Error ? err.message : 'Erro ao executar ação de ingestão';
        setError(message);
      })
      .finally(() => setSaving(false));
  };

  const header = (
    <AdminHeader
      title={isNew ? 'Nova fonte' : 'Fontes — Criação/Edição'}
      subtitle="Fluxos do Console de Fontes v2 apoiados no Design System Admin v1."
      actions={
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => navigate('/admin/sources')}>
            Voltar
          </Button>
          {!isNew && (
            <>
              {source?.state !== 'ACTIVE' && (
                <Button size="sm" onClick={() => handleChangeState('activate')} disabled={saving}>
                  Ativar
                </Button>
              )}
              {source?.state !== 'DISABLED_TEMP' && source?.state !== 'DISABLED_PERM' && (
                <Button size="sm" variant="secondary" onClick={() => handleChangeState('deactivate')} disabled={saving}>
                  Pausar
                </Button>
              )}
              {source?.state !== 'DISABLED_PERM' && (
                <Button size="sm" variant="ghost" onClick={() => handleChangeState('archive')} disabled={saving}>
                  Arquivar
                </Button>
              )}
              <Button size="sm" variant="secondary" onClick={() => handleIngestionAction('run')} disabled={saving}>
                Executar ingestão
              </Button>
              <Button size="sm" variant="ghost" onClick={() => handleIngestionAction('pause')} disabled={saving}>
                Pausar ingestão
              </Button>
              <Button size="sm" variant="secondary" onClick={() => handleIngestionAction('resume')} disabled={saving}>
                Retomar ingestão
              </Button>
            </>
          )}
        </div>
      }
    />
  );

  return (
    <div className="flex flex-col gap-6">
      {header}
      <AdminContent maxWidth={960}>
        <div className="mb-4">
          <Banner
            tone="info"
            title="Console de Fontes v2 — edição"
            description="Atualize dados da fonte, acompanhe estado operacional e mantenha o contrato alinhado ao backend."
          />
        </div>
        {error && <Banner tone="danger" title="Erro" description={error} />}
        {feedback && <Banner tone="success" title="Sucesso" description={feedback} />}
        {loading ? (
          <Banner tone="info" title="Carregando" description="Buscando dados da fonte..." />
        ) : (
          <>
            {!isNew && source && (
              <div className="mb-4 grid gap-3 rounded border border-slate-800 bg-slate-900/40 p-4 md:grid-cols-2">
                <div className="flex flex-col gap-2 text-sm text-slate-200">
                  <div className="flex items-center gap-3">
                    <SourceStatusBadge status={source.state} />
                    <SourceHealthBadge status={source.health_status || (source as Source & { last_health_status?: string }).last_health_status} />
                  </div>
                  <div className="text-xs text-slate-400">Última atualização: {source.updated_at || source.updatedAt || '—'}</div>
                  <div className="text-xs text-slate-300">
                    Saúde: {source.health_reason || 'Sem cálculo recente.'}
                  </div>
                </div>
                <div className="flex flex-col gap-1 text-xs text-slate-300">
                  <div>Último run: {source.last_run_status || '—'}</div>
                  <div>Fim do run: {source.last_run_finished_at || '—'}</div>
                  <div>Latência: {source.last_run_latency_ms ?? '—'} ms</div>
                  <div>Itens: {source.last_run_items ?? '—'}</div>
                  <div>Falhas consecutivas: {source.failure_streak ?? 0}</div>
                  <div>Itens recentes (janela curta): {source.recent_items_count ?? 0}</div>
                </div>
              </div>
            )}
            <SourceForm initialValues={initialValues} submitting={saving} onSubmit={handleSubmit} showStateField />
          </>
        )}
      </AdminContent>
    </div>
  );
}

export default SourceEditPage;
