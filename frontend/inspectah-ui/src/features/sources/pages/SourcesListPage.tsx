import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminContent, AdminHeader, Banner, Button, Input } from '@/ui/admin';
import { SourceForm, type SourceFormValues } from '../components/SourceForm';
import { SourcesTable } from '../components/SourcesTable';
import type { Source } from '../types/Source';
import { createSource, listSources } from '../api/sourcesApi';

export function SourcesListPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [sources, setSources] = useState<Source[]>([]);
  const [draft, setDraft] = useState<SourceFormValues>({
    slug: '',
    name: '',
    type: 'news_rss',
    category: 'general',
    state: 'PROPOSED',
    description: '',
    endpoint: '',
  });

  const loadSources = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listSources();
      setSources(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar fontes';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSources();
  }, [loadSources]);

  const filtered = useMemo(
    () =>
      sources.filter((source) => {
        const term = search.toLowerCase();
        return (
          source.name.toLowerCase().includes(term) ||
          source.type.toLowerCase().includes(term) ||
          (source.category || '').toLowerCase().includes(term)
        );
      }),
    [sources, search],
  );

  return (
    <div className="flex flex-col gap-6">
      <AdminHeader
        title="Fontes"
        subtitle="Cadastre, edite e acompanhe o estado operacional das fontes de informação."
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => loadSources()} disabled={loading}>
              {loading ? 'Atualizando...' : 'Atualizar'}
            </Button>
            <Button onClick={() => navigate('/admin/sources/new')}>Novo cadastro</Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_360px]">
        <AdminContent>
          {error && (
            <div className="mb-4">
              <Banner tone="danger" title="Falha ao carregar fontes" description={error} />
            </div>
          )}
          <div className="mb-4 flex flex-wrap gap-3">
            <Input
              placeholder="Filtrar por nome, tipo ou categoria"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="max-w-sm"
            />
          </div>
          <SourcesTable
            sources={filtered}
            onSelect={(source) => {
              navigate(`/admin/sources/${source.id}`);
            }}
          />
        </AdminContent>

        <div className="flex flex-col gap-4">
          <Banner tone="info" title="Cadastro rápido" description="Crie novas fontes com os campos essenciais e refine no detalhe depois." />
          <AdminContent padded>
            <SourceForm
              initialValues={draft}
              submitting={saving}
              onSubmit={(values) => {
                setSaving(true);
                setError(null);
                createSource(values)
                  .then((created) => {
                    setSources((current) => [created, ...current]);
                    setDraft((current) => ({ ...current, name: '', slug: '', description: '', endpoint: '' }));
                  })
                  .catch((err) => {
                    const message = err instanceof Error ? err.message : 'Erro ao salvar fonte';
                    setError(message);
                  })
                  .finally(() => setSaving(false));
              }}
            />
          </AdminContent>
        </div>
      </div>
    </div>
  );
}

export default SourcesListPage;
