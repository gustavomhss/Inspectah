import { FormEvent, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import { createSource } from '../api';
import type { CopilotoAction } from '../api/copilotoClient';
import CopilotoWidget from '../components/CopilotoWidget';
import { useCopilotoAgent } from '../hooks/useCopilotoAgent';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Input from '../../../shared/components/Input';
import Button from '../../../shared/components/Button';
import ErrorMessage from '../../../shared/components/ErrorMessage';

const SOURCE_TYPES = [
  { value: 'news_rss', label: 'Notícias (RSS/Atom)' },
  { value: 'sports_api', label: 'API de Esportes' },
  { value: 'weather_api', label: 'API de Clima' },
  { value: 'data_api', label: 'API de dados' },
  { value: 'official_open', label: 'Fonte oficial aberta' },
];

const THEMES_BY_TYPE: Record<string, string[]> = {
  news_rss: ['política', 'governo', 'economia'],
  sports_api: ['esportes', 'campeonatos', 'resultados'],
  weather_api: ['clima', 'alertas', 'meteorologia'],
  data_api: ['economia', 'estatisticas', 'dados'],
  official_open: ['economia', 'estatisticas', 'governo'],
};

const INFOTYPES_BY_TYPE: Record<string, string[]> = {
  news_rss: ['news', 'headlines'],
  sports_api: ['sports', 'placares', 'estatisticas'],
  weather_api: ['weather', 'alertas_clima'],
  data_api: ['data', 'statistics'],
  official_open: ['statistics', 'government_data'],
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
  refresh_interval: 1440,
};

function AdminSourceFormPage() {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const navigate = useNavigate();
  const [form, setForm] = useState(DEFAULT_FORM);
  const [suggestedFields, setSuggestedFields] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copilotoInteracted, setCopilotoInteracted] = useState(false);
  const { messages, attachedFiles, loading: copilotoLoading, error: copilotoError, sendUserMessage, startNewChat, attachFile, agentMode, setAgentMode } =
    useCopilotoAgent();

  const availableThemes = useMemo(() => THEMES_BY_TYPE[form.type] || [], [form.type]);
  const availableInfoTypes = useMemo(() => INFOTYPES_BY_TYPE[form.type] || [], [form.type]);
  const highlightClass = (field: string) => (suggestedFields.includes(field) ? 'border-sky-400 shadow shadow-sky-500/30' : '');

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

  const applyCopilotoActions = (actions: CopilotoAction[]) => {
    if (!actions?.length) return;
    setForm((prev) => {
      const updated = { ...prev };
      let changed = false;
      const newSuggested = new Set(suggestedFields);
      actions.forEach((action) => {
        const atype = action.type?.toUpperCase();
        if ((atype === 'MARK_SUGGESTED' || atype === 'SUGGEST_FIELD' || action.type === 'mark_suggested') && action.field) {
          newSuggested.add(action.field);
        }
        if ((atype === 'CLEAR_FIELD' || action.type === 'clear_field') && action.field) {
          if (action.field in updated) {
            if (Array.isArray((updated as Record<string, unknown>)[action.field])) {
              (updated as Record<string, unknown>)[action.field] = [];
            } else {
              (updated as Record<string, unknown>)[action.field] = '';
            }
            changed = true;
          }
          newSuggested.delete(action.field);
        }
        if ((atype === 'SET_FIELD' || action.type === 'set_field') && action.field) {
          const value = action.value;
          if (action.field === 'type' && typeof value === 'string') {
            const valid = SOURCE_TYPES.find((opt) => opt.value === value);
            if (valid) {
              updated.type = value;
              updated.themes = [];
              updated.info_types = [];
              changed = true;
            }
          } else if (action.field === 'themes' && Array.isArray(value)) {
            const allowed = THEMES_BY_TYPE[updated.type] || [];
            const filtered = value.filter((item): item is string => typeof item === 'string' && allowed.includes(item));
            if (filtered.length) {
              updated.themes = filtered;
              changed = true;
            }
          } else if (action.field === 'info_types' && Array.isArray(value)) {
            const allowed = INFOTYPES_BY_TYPE[updated.type] || [];
            const filtered = value.filter((item): item is string => typeof item === 'string' && allowed.includes(item));
            if (filtered.length) {
              updated.info_types = filtered;
              changed = true;
            }
          } else if (action.field === 'refresh_interval' && typeof value === 'number') {
            updated.refresh_interval = value;
            changed = true;
          } else if (action.field in updated && typeof value === 'string') {
            (updated as Record<string, unknown>)[action.field] = value;
            changed = true;
          }
        }
        if (atype === 'FOCUS_FIELD' && action.field) {
          newSuggested.add(action.field);
        }
      });
      setSuggestedFields(Array.from(newSuggested));
      if (changed) setCopilotoInteracted(true);
      return changed ? updated : prev;
    });
  };

  const handleCopilotoSend = async (message: string) => {
    const actions = await sendUserMessage(message, form);
    applyCopilotoActions(actions);
    if (!actions.length) {
      setCopilotoInteracted(true);
    }
  };

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
            className={highlightClass('slug')}
          />
          <Input
            label="Nome *"
            helperText="Nome legível da fonte no console. Ex.: Portal X - Política"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
            className={highlightClass('name')}
          />
          <div className="space-y-1">
            <label className="text-sm font-semibold text-white" htmlFor="source-type">
              Tipo * <span className="text-xs text-slate-300 block">Tipos suportados, incluindo oficial aberta.</span>
            </label>
            <select
              id="source-type"
              className={`w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white ${highlightClass('type')}`}
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
            className={highlightClass('category')}
          />
          <div className="space-y-1">
            <label className="text-sm font-semibold text-white" htmlFor="refresh-interval">
              Refresh interval (min) *
              <span className="text-xs text-slate-300 block">Frequência desejada de atualização.</span>
            </label>
            <input
              id="refresh-interval"
              type="number"
              min={15}
              className={`w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white ${highlightClass('refresh_interval')}`}
              value={form.refresh_interval}
              onChange={(e) => setForm({ ...form, refresh_interval: Number(e.target.value) })}
              required
            />
          </div>
          <Input
            label="Endpoint / URL base *"
            helperText="Endereço usado para consultar esta fonte (URL de RSS/API)."
            value={form.endpoint}
            onChange={(e) => setForm({ ...form, endpoint: e.target.value })}
            required
            className={highlightClass('endpoint')}
          />
          <div className="space-y-1">
            <label className="text-sm font-semibold text-white" htmlFor="source-themes">
              Temas * <span className="text-xs text-slate-300 block">Selecione os temas cobertos pela fonte.</span>
            </label>
            <select
              id="source-themes"
              multiple
              className={`w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white ${highlightClass('themes')}`}
              value={form.themes}
              onChange={(e) => setForm({ ...form, themes: Array.from(e.target.selectedOptions).map((opt) => opt.value) })}
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
            <label className="text-sm font-semibold text-white" htmlFor="source-info">
              Info types * <span className="text-xs text-slate-300 block">Selecione os tipos de informação.</span>
            </label>
            <select
              id="source-info"
              multiple
              className={`w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white ${highlightClass('info_types')}`}
              value={form.info_types}
              onChange={(e) => setForm({ ...form, info_types: Array.from(e.target.selectedOptions).map((opt) => opt.value) })}
              required
            >
              {availableInfoTypes.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>
          <div className="md:col-span-2">
            <Input
              label="Descrição"
              helperText="Descrição breve da fonte (obrigatória para oficial aberta)."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className={highlightClass('description')}
            />
          </div>
        </div>

        <div className="flex items-center justify-between gap-3">
          <div className="text-sm text-slate-200">
            <p className="font-semibold text-white">Copiloto de Fontes</p>
            <p className="text-xs text-slate-300">Use o Copiloto ao menos uma vez antes de salvar.</p>
          </div>
          <label className="flex items-center gap-2 text-xs text-slate-200">
            <input type="checkbox" checked={agentMode} onChange={(e) => setAgentMode(e.target.checked)} />
            modo agente
          </label>
          <Button type="submit" variant="primary" disabled={submitting || !copilotoInteracted}>
            {submitting ? 'Salvando...' : 'Criar fonte'}
          </Button>
        </div>
      </form>
      <CopilotoWidget
        messages={messages}
        attachedFiles={attachedFiles}
        loading={copilotoLoading}
        error={copilotoError || undefined}
        onSend={handleCopilotoSend}
        onNewChat={startNewChat}
        onAttach={attachFile}
        agentMode={agentMode}
        onToggleAgentMode={setAgentMode}
        autoOpen
      />
    </PageContainer>
  );
}

export default AdminSourceFormPage;
