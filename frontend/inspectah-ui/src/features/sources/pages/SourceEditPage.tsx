import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AdminContent, AdminHeader, AdminShell, AdminSidebar, Banner, Button } from '@/ui/admin';
import { SourceForm, type SourceFormValues } from '../components/SourceForm';
import { SourceStatusBadge } from '../components/SourceStatusBadge';
import type { Source } from '../types/Source';
import { activateSource, archiveSource, createSource, deactivateSource, getSourceById, updateSource } from '../api/sourcesApi';

const sidebarNav = [
  { label: 'Fontes', to: '/admin/sources', active: true },
  { label: 'Ingestão', to: '/admin/ingestion' },
  { label: 'Debunker', to: '/admin/debunker' },
];

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
            </>
          )}
        </div>
      }
    />
  );

  return (
    <AdminShell sidebar={<AdminSidebar title="Consoles" navItems={sidebarNav} />} header={header}>
      <AdminContent maxWidth={960}>
        <div className="mb-4">
          <Banner
            tone="info"
            title="Console de Fontes v2 — edição"
            description="Atualize dados de fonte, acompanhe estado operacional e mantenha o contrato alinhado ao backend."
          />
        </div>
        {error && <Banner tone="danger" title="Erro" description={error} />}
        {feedback && <Banner tone="success" title="Sucesso" description={feedback} />}
        {loading ? (
          <Banner tone="info" title="Carregando" description="Buscando dados da fonte..." />
        ) : (
          <>
            {!isNew && source && (
              <div className="mb-4 flex items-center gap-3 text-sm text-slate-200">
                <SourceStatusBadge status={source.state} />
                <span className="text-xs text-slate-400">Última atualização: {source.updated_at || source.updatedAt || '—'}</span>
              </div>
            )}
            <SourceForm initialValues={initialValues} submitting={saving} onSubmit={handleSubmit} showStateField />
          </>
        )}
      </AdminContent>
    </AdminShell>
  );
}

export default SourceEditPage;
