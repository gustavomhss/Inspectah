import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import { createSource } from '../api';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Input from '../../../shared/components/Input';
import Button from '../../../shared/components/Button';
import ErrorMessage from '../../../shared/components/ErrorMessage';

const DEFAULT_FORM = {
  slug: '',
  name: '',
  type: 'news_rss',
  category: 'official',
  endpoint: '',
  description: '',
  themes: '',
  info_types: '',
};

function AdminSourceFormPage() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const navigate = useNavigate();
  const [form, setForm] = useState(DEFAULT_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const payload = {
        ...form,
        themes: form.themes ? form.themes.split(',').map((v) => v.trim()) : [],
        info_types: form.info_types ? form.info_types.split(',').map((v) => v.trim()) : [],
        protocol: 'https',
        format: form.type === 'news_rss' ? 'rss' : 'json',
        auth_type: 'none',
        auth_config: {},
        request_params: {},
        headers: {},
        frequency: 'daily',
        timeout_ms: 5000,
        retry_policy: {},
        parsing_config: {},
        redundancy_group: null,
        redundancy_role: null,
        meta: {},
        created_by: 'admin-ui',
      };
      const created = await createSource(payload, token || undefined);
      logEvent('admin.page_open', { page: 'source_created', id: created.id });
      navigate(`/admin/sources/${created.id}`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageContainer>
      <PageHeader title="Nova fonte" subtitle="Cadastre uma fonte do Console de Fontes." />
      <form className="space-y-4" onSubmit={handleSubmit}>
        {error && <ErrorMessage message={error} />}
        <div className="grid gap-4 md:grid-cols-2">
          <Input label="Slug" value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} required />
          <Input label="Nome" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <Input
            label="Tipo"
            value={form.type}
            onChange={(e) => setForm({ ...form, type: e.target.value })}
            placeholder="news_rss, weather_api, sports_api..."
            required
          />
          <Input
            label="Categoria"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            placeholder="official, monitoring..."
            required
          />
          <Input
            label="Endpoint / URL base"
            value={form.endpoint}
            onChange={(e) => setForm({ ...form, endpoint: e.target.value })}
            required
          />
          <Input
            label="Temas (separados por vírgula)"
            value={form.themes}
            onChange={(e) => setForm({ ...form, themes: e.target.value })}
          />
          <Input
            label="Info types (separados por vírgula)"
            value={form.info_types}
            onChange={(e) => setForm({ ...form, info_types: e.target.value })}
          />
          <Input label="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Salvando...' : 'Criar fonte'}
        </Button>
      </form>
    </PageContainer>
  );
}

export default AdminSourceFormPage;

