import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AdminSourceDetail, AdminSourceHealthStatus } from '../../../core/api/api-types';
import { changeSourceStatus, fetchHealthchecks, fetchSourceDetail, triggerSourceHealthcheck, updateSource } from '../api';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import SourceStatusBadge from '../components/SourceStatusBadge';
import Input from '../../../shared/components/Input';
import Button from '../../../shared/components/Button';
import ErrorMessage from '../../../shared/components/ErrorMessage';
import CopilotoWidget from '../components/CopilotoWidget';
import { useCopilotoAgent } from '../hooks/useCopilotoAgent';
import type { CopilotoAction } from '../api/copilotoClient';

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

function AdminSourceDetailPage() {
  const { sourceId } = useParams<{ sourceId: string }>();
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [source, setSource] = useState<AdminSourceDetail | null>(null);
  const [healthchecks, setHealthchecks] = useState<AdminSourceDetail['healthchecks']>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [hcRunning, setHcRunning] = useState(false);
  const [form, setForm] = useState<Record<string, unknown>>({});
  const [pendingStatusPlan, setPendingStatusPlan] = useState<{ from_state: string; to_state: string; reason?: string } | null>(null);
  const { messages, attachedFiles, loading: copilotoLoading, error: copilotoError, sendUserMessage, startNewChat, attachFile, agentMode, setAgentMode } =
    useCopilotoAgent(sourceId);

  const load = useCallback(async () => {
    if (!sourceId) return;
    setLoading(true);
    setLoadError(null);
    try {
      const result = await fetchSourceDetail(sourceId, token || undefined);
      setSource(result);
      setForm({
        ...result,
        endpoint: result.endpoint || result.url_base || '',
        themes: result.themes || [],
        info_types: result.info_types || [],
        refresh_interval: result.refresh_interval ?? 1440,
        source_id: result.id,
      });
      const hc = await fetchHealthchecks(sourceId, token || undefined);
      setHealthchecks(hc);
    } catch (err) {
      setLoadError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [sourceId, token]);

  const handleHealthcheck = async () => {
    if (!sourceId) return;
    setHcRunning(true);
    setActionError(null);
    try {
      await triggerSourceHealthcheck(sourceId, token || undefined);
      await load();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setHcRunning(false);
    }
  };

  const applyActions = (actions: CopilotoAction[]) => {
    if (!actions?.length) return;
    setForm((prev) => {
      const updated = { ...prev };
      actions.forEach((action) => {
        const atype = (action.type || '').toUpperCase();
        if ((atype === 'SET_FIELD' || action.type === 'set_field') && action.field) {
          if (action.field === 'themes' && Array.isArray(action.value)) {
            updated.themes = action.value;
          } else if (action.field === 'info_types' && Array.isArray(action.value)) {
            updated.info_types = action.value;
          } else if (action.field === 'refresh_interval' && typeof action.value === 'number') {
            updated.refresh_interval = action.value;
          } else if (action.field === 'type' && typeof action.value === 'string') {
            updated.type = action.value;
          } else if (action.field === 'category' && typeof action.value === 'string') {
            updated.category = action.value;
          } else {
            (updated as Record<string, unknown>)[action.field] = action.value as unknown;
          }
        }
        if ((atype === 'PROPOSE_UPDATE' || action.type === 'propose_update') && action.changes) {
          action.changes.forEach((change) => {
            updated[change.field] = change.to;
          });
        }
        if ((atype === 'PLAN_STATUS' || action.type === 'plan_status_change') && action.plan) {
          setPendingStatusPlan(action.plan);
        }
        if (atype === 'FOCUS_FIELD' && action.field) {
          // apenas marcar como sugerido/focado
        }
      });
      return updated;
    });
  };

  const handleCopilotoSend = async (message: string) => {
    const actions = await sendUserMessage(message, form);
    applyActions(actions);
  };

  const handleSave = async () => {
    if (!sourceId) return;
    setActionError(null);
    try {
      const payload = {
        name: form.name || source?.name,
        description: form.description ?? source?.description ?? '',
        endpoint: form.endpoint || source?.endpoint || source?.url_base,
        themes: (form.themes as string[]) || source?.themes || [],
        info_types: (form.info_types as string[]) || source?.info_types || [],
        refresh_interval: form.refresh_interval ?? source?.refresh_interval ?? 1440,
        type: (form.type as string) || source?.type,
        category: (form.category as string) || source?.category,
        updated_by: 'admin-ui',
      };
      await updateSource(sourceId, payload, token || undefined);
      await load();
    } catch (err) {
      setActionError((err as Error).message);
    }
  };

  const handleApplyStatus = async () => {
    if (!sourceId || !pendingStatusPlan) return;
    setActionError(null);
    try {
      await changeSourceStatus(sourceId, pendingStatusPlan.to_state as AdminSourceDetail['state'], pendingStatusPlan.reason || 'Solicitado via Copiloto', token || undefined);
      setPendingStatusPlan(null);
      await load();
    } catch (err) {
      setActionError((err as Error).message);
    }
  };
  const handleStatusAction = async (target: AdminSourceDetail['state']) => {
    if (!sourceId) return;
    setActionError(null);
    try {
      await changeSourceStatus(sourceId, target, 'Ajuste manual via UI', token || undefined);
      await load();
    } catch (err) {
      setActionError((err as Error).message);
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

  const availableThemes = useMemo(() => THEMES_BY_TYPE[(form.type as string) || ''] || [], [form.type]);
  const availableInfoTypes = useMemo(() => INFOTYPES_BY_TYPE[(form.type as string) || ''] || [], [form.type]);

  if (loading) {
    return <LoadingState label="Carregando detalhes da fonte..." />;
  }

  if (loadError || !source) {
    return <ErrorState message={loadError || 'Fonte não encontrada'} onRetry={load} />;
  }

  const healthStatus: AdminSourceHealthStatus = source.last_health_status ?? 'unknown';

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Link to="/admin/sources" className="text-sm font-semibold text-sky-200 hover:underline">
          ← Voltar para Fontes
        </Link>
        <div className="flex gap-2">
          <button
            className="rounded-lg bg-white/10 px-3 py-2 text-sm font-semibold text-white hover:bg-white/20"
            onClick={handleHealthcheck}
            disabled={hcRunning}
          >
            {hcRunning ? 'Rodando health-check...' : 'Rodar health-check'}
          </button>
          <Button variant="primary" onClick={handleSave}>
            Salvar alterações
          </Button>
        </div>
      </div>
      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card space-y-4">
        {actionError ? <ErrorMessage message={actionError} /> : null}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Fonte</p>
            <h3 className="text-2xl font-bold text-white">{source.name}</h3>
            <p className="text-sm text-slate-200">{(source.info_types || []).join(', ') || source.type}</p>
            <p className="text-xs text-slate-400">{source.endpoint || source.url_base}</p>
          </div>
        <div className="flex flex-col items-end gap-2">
          <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white">{source.state}</span>
          <SourceStatusBadge status={healthStatus} />
          <div className="flex flex-wrap gap-2 text-xs">
            <Button variant="secondary" onClick={() => handleStatusAction('ACTIVE')} disabled={source.state === 'ACTIVE'}>
              Aprovar/Ativar
            </Button>
            <Button variant="secondary" onClick={() => handleStatusAction('DISABLED_TEMP')} disabled={source.state === 'DISABLED_TEMP'}>
              Suspender
            </Button>
            <Button variant="secondary" onClick={() => handleStatusAction('DISABLED_PERM')} disabled={source.state === 'DISABLED_PERM'}>
              Desativar
            </Button>
          </div>
        </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <Input
            label="Endpoint / URL base"
            value={(form.endpoint as string) || ''}
            onChange={(e) => setForm({ ...form, endpoint: e.target.value })}
          />
          <Input
            label="Refresh interval (min)"
            value={String(form.refresh_interval ?? '')}
            onChange={(e) => setForm({ ...form, refresh_interval: Number(e.target.value) })}
          />
          <div className="space-y-1">
            <label className="text-sm font-semibold text-white" htmlFor="detail-themes">
              Temas
            </label>
            <select
              id="detail-themes"
              multiple
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={(form.themes as string[]) || []}
              onChange={(e) => setForm({ ...form, themes: Array.from(e.target.selectedOptions).map((opt) => opt.value) })}
            >
              {availableThemes.map((theme) => (
                <option key={theme} value={theme}>
                  {theme}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-sm font-semibold text-white" htmlFor="detail-info">
              Info types
            </label>
            <select
              id="detail-info"
              multiple
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={(form.info_types as string[]) || []}
              onChange={(e) => setForm({ ...form, info_types: Array.from(e.target.selectedOptions).map((opt) => opt.value) })}
            >
              {availableInfoTypes.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {pendingStatusPlan ? (
        <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-white">
          <p className="text-sm font-semibold">Plano de status do Copiloto</p>
          <p className="text-xs text-slate-300">
            {pendingStatusPlan.from_state} → {pendingStatusPlan.to_state} · {pendingStatusPlan.reason || 'Sem motivo'}
          </p>
          <div className="mt-2 flex gap-2">
            <Button variant="primary" onClick={handleApplyStatus}>
              Aplicar status
            </Button>
            <Button variant="ghost" onClick={() => setPendingStatusPlan(null)}>
              Ignorar
            </Button>
          </div>
        </div>
      ) : null}

      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <h4 className="text-lg font-semibold text-white">Histórico de estados</h4>
        <div className="mt-3 space-y-2">
          {(!source.state_history || source.state_history.length === 0) && <p className="text-sm text-slate-200">Sem histórico registrado.</p>}
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
          {(healthchecks || []).map((entry, index) => {
            const entryStatus: AdminSourceHealthStatus = entry.status ?? 'unknown';
            return (
              <div key={`${entry.checked_at}-${index}`} className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 px-3 py-2">
                <div>
                  <p className="text-sm text-white">
                    {entry.status} · {entry.error || 'OK'}
                  </p>
                  <p className="text-xs text-slate-300">{entry.checked_at || 'Sem timestamp'}</p>
                </div>
                <SourceStatusBadge status={entryStatus} />
              </div>
            );
          })}
        </div>
      </div>

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
      />
    </div>
  );
}

export default AdminSourceDetailPage;
