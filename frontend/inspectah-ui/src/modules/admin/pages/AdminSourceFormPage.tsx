import { FormEvent, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import { createSource } from '../api';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Input from '../../../shared/components/Input';
import Button from '../../../shared/components/Button';
import ErrorMessage from '../../../shared/components/ErrorMessage';

const SOURCE_TYPES = [
  { value: 'news_rss', label: 'Notícias (RSS/Atom)' },
  { value: 'sports_api', label: 'API de Esportes' },
  { value: 'weather_api', label: 'API de Clima' },
];

const THEMES_BY_TYPE: Record<string, string[]> = {
  news_rss: ['política', 'governo', 'economia'],
  sports_api: ['esportes', 'campeonatos', 'resultados'],
  weather_api: ['clima', 'alertas', 'meteorologia'],
};

const INFOTYPES_BY_TYPE: Record<string, string[]> = {
  news_rss: ['news', 'headlines'],
  sports_api: ['sports', 'placares', 'estatisticas'],
  weather_api: ['weather', 'alertas_clima'],
};

const DEFAULT_FORM = {
  slug: '',
  name: '',
  type: SOURCE_TYPES[0].value,
  category: 'official',
  endpoint: '',
  description: '',
  themes: [] as string[],
  info_types: [] as string[],
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
        themes: form.themes,
        info_types: form.info_types.length ? form.info_types : INFOTYPES_BY_TYPE[form.type] || [],
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

  const availableThemes = useMemo(() => THEMES_BY_TYPE[form.type] || [], [form.type]);
  const availableInfoTypes = useMemo(() => INFOTYPES_BY_TYPE[form.type] || [], [form.type]);

  return (
    <PageContainer>
      <PageHeader title="Nova fonte" subtitle="Cadastre uma fonte do Console de Fontes." />
      <form className="space-y-4" onSubmit={handleSubmit}>
        {error && <ErrorMessage message={error} />}
        <div className="grid gap-4 md:grid-cols-2">
          <Input
            label="Slug *"
            helperText="Identificador interno curto, sem espaços. Ex.: fonte-noticias-br"
            value={form.slug}
            onChange={(e) => setForm({ ...form, slug: e.target.value })}
            required
          />
          <Input
            label="Nome *"
            helperText="Nome legível da fonte no console. Ex.: Portal X - Política"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <div className="space-y-1">
            <label className="text-sm font-semibold text-white" htmlFor="source-type">
              Tipo * <span className="text-xs text-slate-300 block">Escolha um dos tipos suportados na Fase 1.</span>
            </label>
            <select
              id="source-type"
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value as typeof form.type, themes: [], info_types: [] })}
              required
            >
              {SOURCE_TYPES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <Input
            label="Categoria *"
            helperText="Categoria geral (ex.: official, monitoring)."
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            required
          />
          <Input
            label="Endpoint / URL base *"
            helperText="Endereço usado para consultar esta fonte (URL de RSS/API)."
            value={form.endpoint}
            onChange={(e) => setForm({ ...form, endpoint: e.target.value })}
            required
          />
          <div className="space-y-1">
            <label className="text-sm font-semibold text-white" htmlFor="source-themes">
              Temas * <span className="text-xs text-slate-300 block">Selecione os temas cobertos pela fonte.</span>
            </label>
            <select
              id="source-themes"
              multiple
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={form.themes}
              onChange={(e) =>
                setForm({
                  ...form,
                  themes: Array.from(e.target.selectedOptions).map((opt) => opt.value),
                })
              }
              required
            >
              {availableThemes.map((theme) => (
                <option key={theme} value={theme}>
                  {theme}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-sm font-semibold text-white" htmlFor="source-info-types">
              Info types <span className="text-xs text-slate-300 block">Tipos de informação fornecidos (opcional, selecione um ou mais).</span>
            </label>
            <select
              id="source-info-types"
              multiple
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={form.info_types}
              onChange={(e) =>
                setForm({
                  ...form,
                  info_types: Array.from(e.target.selectedOptions).map((opt) => opt.value),
                })
              }
            >
              {availableInfoTypes.map((info) => (
                <option key={info} value={info}>
                  {info}
                </option>
              ))}
            </select>
          </div>
          <Input
            label="Descrição"
            helperText="Descrição livre para admins lembrarem o propósito da fonte."
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </div>
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Salvando...' : 'Criar fonte'}
        </Button>
      </form>
    </PageContainer>
  );
}

export default AdminSourceFormPage;
