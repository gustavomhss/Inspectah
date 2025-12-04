import { useEffect, useMemo, useState } from 'react';
import type { AgentProfile } from '@/core/api/api-types';
import { useAgents } from '@/modules/agents/hooks/useAgents';
import type { AgentFlowConfigForm, AgentFlowStepForm, AgentRoleOption } from '../agentFlowsTypes';

const ALLOWED_PARAM_KEYS: Record<string, { label: string; type: 'text' | 'number' | 'boolean' | 'textarea' }> = {
  committee_id: { label: 'ID do comitê', type: 'text' },
  strict_mode: { label: 'Modo estrito', type: 'boolean' },
  threshold: { label: 'Limite de decisão', type: 'number' },
  max_depth: { label: 'Profundidade máx.', type: 'number' },
  notes: { label: 'Notas', type: 'textarea' },
  allow_retry: { label: 'Permitir retry', type: 'boolean' },
};

const ROLE_OPTIONS: AgentRoleOption[] = ['interpreter', 'classifier', 'analyst', 'debunker', 'decision_maker', 'librarian'];
const REQUIRED_ROLES: AgentRoleOption[] = ['interpreter', 'classifier', 'decision_maker'];

interface Props {
  initialFlow: AgentFlowConfigForm;
  onSave: (flow: AgentFlowConfigForm) => Promise<void>;
  saving: boolean;
  error: string | null;
  clearError: () => void;
}

export default function AgentFlowEditor({ initialFlow, onSave, saving, error, clearError }: Props) {
  const [form, setForm] = useState<AgentFlowConfigForm>(initialFlow);
  const [errors, setErrors] = useState<string[]>([]);
  const domainId = 'domain-key-input';
  const nameId = 'flow-name-input';
  const descId = 'flow-desc-input';
  const reasonId = 'flow-reason-input';
  const { agents, loading: loadingAgents, error: agentsError, reload: reloadAgents } = useAgents();

  useEffect(() => {
    setForm(initialFlow);
    setErrors([]);
    clearError();
  }, [initialFlow, clearError]);

  const agentOptions = useMemo(
    () =>
      (agents || []).map((a) => ({
        id: a.id,
        label: a.name,
        role: a.role,
      })),
    [agents],
  );

  const canSave = useMemo(() => form.domain_key.trim().length > 0 && form.steps.length > 0, [form]);

  const validateForm = (): string[] => {
    const validationErrors: string[] = [];
    REQUIRED_ROLES.forEach((role) => {
      if (!form.steps.some((s) => s.agent_role === role)) {
        validationErrors.push(`Inclua um passo com o papel ${role}`);
      }
    });
    form.steps.forEach((step) => {
      const params = (step.params || {}) as Record<string, unknown>;
      if (!params.agent_id) {
        validationErrors.push(`Selecione um agente real para o passo #${step.position}`);
      }
    });
    if (form.domain_key.trim().length === 0) {
      validationErrors.push('Informe o domínio do fluxo');
    }
    return validationErrors;
  };

  const handleAddStep = () => {
    const nextPosition = form.steps.length + 1;
    const step: AgentFlowStepForm = {
      position: nextPosition,
      agent_role: 'interpreter',
      params: {},
      required: true,
      can_fail_soft: false,
    };
    setForm((prev) => ({ ...prev, steps: [...prev.steps, step] }));
  };

  const handleRemoveStep = (position: number) => {
    const filtered = form.steps.filter((s) => s.position !== position);
    setForm((prev) => ({ ...prev, steps: renumber(filtered) }));
  };

  const handleMove = (position: number, direction: -1 | 1) => {
    const idx = form.steps.findIndex((s) => s.position === position);
    const targetIdx = idx + direction;
    if (targetIdx < 0 || targetIdx >= form.steps.length) return;
    const next = [...form.steps];
    const tmp = next[idx];
    next[idx] = next[targetIdx];
    next[targetIdx] = tmp;
    setForm((prev) => ({ ...prev, steps: renumber(next) }));
  };

  const updateStep = (position: number, patch: Partial<AgentFlowStepForm>) => {
    const next = form.steps.map((s) => (s.position === position ? { ...s, ...patch } : s));
    setForm((prev) => ({ ...prev, steps: next }));
  };

  const updateParams = (position: number, key: string, value: unknown) => {
    const step = form.steps.find((s) => s.position === position);
    if (!step) return;
    const params = { ...(step.params || {}) };
    if (value === '' || value === null || value === undefined) {
      delete params[key];
    } else {
      params[key] = value;
    }
    updateStep(position, { params });
  };

  const handleAgentSelect = (step: AgentFlowStepForm, agentId: string) => {
    const agent = (agents || []).find((a) => a.id === agentId);
    const params = { ...(step.params || {}) };
    params.agent_id = agentId || undefined;
    params.agent_label = agent?.name || undefined;
    updateStep(step.position, { params });
  };

  const warnMissingDecision = useMemo(
    () => !form.steps.some((s) => s.agent_role === 'decision_maker'),
    [form.steps],
  );

  const handleSubmit = async () => {
    clearError();
    const validationErrors = validateForm();
    setErrors(validationErrors);
    if (validationErrors.length > 0) return;
    try {
      await onSave({ ...form, steps: renumber(form.steps) });
    } catch (err) {
      const msg = (err as Error).message;
      setErrors(msg ? [msg] : ['Falha ao salvar fluxo']);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Editor</p>
          <h3 className="text-lg font-semibold text-white">{form.id ? 'Editar fluxo' : 'Novo fluxo'}</h3>
          <p className="text-xs text-slate-300">
            Configure um fluxo linear de agentes para um domínio. Decision Maker sempre finaliza a cadeia.
          </p>
        </div>
        <button
          type="button"
          disabled={!canSave || saving}
          onClick={() => void handleSubmit()}
          className="rounded-full bg-emerald-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-300 disabled:cursor-not-allowed disabled:bg-emerald-800/60"
        >
          {saving ? 'Salvando...' : 'Salvar fluxo'}
        </button>
      </div>

      {(errors.length > 0 || error || agentsError) && (
        <div className="rounded-xl border border-amber-400/40 bg-amber-400/10 p-3 text-sm text-amber-100">
          <p className="font-semibold">Correções necessárias:</p>
          <ul className="list-disc pl-5">
            {(errors.length ? errors : error?.split(';') || [])
              .concat(agentsError ? [`Falha ao carregar agentes: ${agentsError}`] : [])
              .map((msg, idx) => (
                <li key={idx}>{msg}</li>
              ))}
          </ul>
        </div>
      )}

      {warnMissingDecision ? (
        <div className="rounded-xl border border-sky-400/30 bg-sky-400/10 p-3 text-xs text-sky-100">
          Adicione um passo com agente Decision Maker para manter a rastreabilidade e encerramento do fluxo.
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-semibold text-white" htmlFor={domainId}>
            Domínio
          </label>
          <p className="text-xs text-slate-400">Qual tipo de entrada este fluxo atende (ex.: noticia_texto, cases).</p>
          <input
            id={domainId}
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
            value={form.domain_key}
            onChange={(e) => setForm((prev) => ({ ...prev, domain_key: e.target.value }))}
            placeholder="ex: politics_news"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-semibold text-white" htmlFor={nameId}>
            Nome do fluxo
          </label>
          <p className="text-xs text-slate-400">Título amigável para operadores encontrarem na lista.</p>
          <input
            id={nameId}
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
            value={form.name || ''}
            onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
            placeholder="Fluxo padrão"
          />
        </div>
        <div className="space-y-2 sm:col-span-2">
          <label className="text-sm font-semibold text-white" htmlFor={descId}>
            Descrição
          </label>
          <p className="text-xs text-slate-400">Explique objetivo, topologia (committee/router) e particularidades.</p>
          <textarea
            id={descId}
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
            value={form.description || ''}
            onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
            rows={2}
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-semibold text-white" htmlFor={reasonId}>
            Motivo da alteração
          </label>
          <p className="text-xs text-slate-400">Justificativa auditável (ex.: ativar teste A/B, trocar agente com falha).</p>
          <input
            id={reasonId}
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
            value={form.change_reason || ''}
            onChange={(e) => setForm((prev) => ({ ...prev, change_reason: e.target.value }))}
            placeholder="Contexto para auditoria"
          />
        </div>
        <div className="flex items-center gap-3">
          <input
            id="is_active"
            type="checkbox"
            checked={form.is_active ?? true}
            onChange={(e) => setForm((prev) => ({ ...prev, is_active: e.target.checked }))}
            className="h-4 w-4 rounded border-white/20 bg-white/5 text-sky-500 focus:ring-sky-400"
          />
          <label htmlFor="is_active" className="text-sm text-white">
            Fluxo ativo para este domínio
          </label>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Passos</p>
            <h4 className="text-base font-semibold text-white">Sequência linear</h4>
            <p className="text-xs text-slate-300">
              Use ao menos interpreter, classifier e decision_maker. Committee/router cabem no params do classifier.
            </p>
          </div>
          <div className="flex items-center gap-2">
            {loadingAgents ? <span className="text-xs text-slate-300">Carregando agentes...</span> : null}
            <button
              type="button"
              onClick={() => void reloadAgents()}
              className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
            >
              Recarregar agentes
            </button>
            <button
              type="button"
              onClick={handleAddStep}
              className="rounded-full bg-white/10 px-3 py-1 text-sm font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
            >
              Adicionar passo
            </button>
          </div>
        </div>
        {form.steps.length === 0 ? (
          <div className="rounded-xl border border-white/5 bg-white/5 p-3 text-sm text-slate-200">
            Nenhum passo configurado. Adicione passos na ordem desejada.
          </div>
        ) : (
          <div className="space-y-3">
            {form.steps.map((step) => (
              <div
                key={step.position}
                className="rounded-xl border border-white/10 bg-white/5 p-3 shadow-sm transition hover:border-white/20"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-sm text-slate-200">
                    <span className="rounded-full bg-white/10 px-2 py-1 text-xs font-semibold text-white">
                      #{step.position}
                    </span>
                    <select
                      className="rounded-lg border border-white/10 bg-slate-900 px-2 py-1 text-sm text-white focus:border-sky-400"
                      value={step.agent_role}
                      onChange={(e) => updateStep(step.position, { agent_role: e.target.value as AgentRoleOption })}
                    >
                      {ROLE_OPTIONS.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                    <label className="flex items-center gap-1 text-xs text-slate-200">
                      <input
                        type="checkbox"
                        checked={step.required ?? true}
                        onChange={(e) => updateStep(step.position, { required: e.target.checked })}
                      />
                      Obrigatório
                    </label>
                    <label className="flex items-center gap-1 text-xs text-slate-200">
                      <input
                        type="checkbox"
                        checked={step.can_fail_soft ?? false}
                        onChange={(e) => updateStep(step.position, { can_fail_soft: e.target.checked })}
                      />
                      Fail soft
                    </label>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleMove(step.position, -1)}
                      className="rounded-lg bg-white/10 px-2 py-1 text-xs text-white hover:bg-white/20"
                    >
                      ↑
                    </button>
                    <button
                      type="button"
                      onClick={() => handleMove(step.position, 1)}
                      className="rounded-lg bg-white/10 px-2 py-1 text-xs text-white hover:bg-white/20"
                    >
                      ↓
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemoveStep(step.position)}
                      className="rounded-lg bg-red-500/20 px-2 py-1 text-xs text-red-100 hover:bg-red-500/30"
                    >
                      Remover
                    </button>
                  </div>
                </div>

                <AgentSelector
                  step={step}
                  options={agentOptions}
                  loading={loadingAgents}
                  onChange={(agentId) => handleAgentSelect(step, agentId)}
                />

                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  <div className="sm:col-span-2 text-xs text-slate-300">
                    Parâmetros opcionais por etapa. Use committee_id para comitês, threshold para decisão/roteamento e
                    allow_retry/fail soft para fluxos tolerantes.
                  </div>
                  {Object.entries(ALLOWED_PARAM_KEYS).map(([key, meta]) => {
                    const controlId = `${key}-${step.position}`;
                    return (
                      <div key={key} className="space-y-1">
                        <label className="text-xs font-semibold text-slate-200" htmlFor={controlId}>
                          {meta.label}
                        </label>
                        {renderParamInput(step, key, meta.type, controlId, updateParams)}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function AgentSelector({
  step,
  options,
  loading,
  onChange,
}: {
  step: AgentFlowStepForm;
  options: Array<{ id: string; label: string; role: AgentProfile['role'] }>;
  loading: boolean;
  onChange: (agentId: string) => void;
}) {
  const params = (step.params || {}) as Record<string, unknown>;
  const selected = (params.agent_id as string) || '';
  const matchesRole = options.filter((opt) => opt.role === step.agent_role);
  const selectId = `agent-select-${step.position}`;
  return (
    <div className="mt-3 space-y-1">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-200" htmlFor={selectId}>
          Agente vinculado
        </label>
        {loading ? <span className="text-[11px] text-slate-400">Carregando...</span> : null}
      </div>
      <select
        className="w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-400"
        value={selected}
        id={selectId}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Selecione um agente com papel {step.agent_role}</option>
        {matchesRole.map((opt) => (
          <option key={opt.id} value={opt.id}>
            {opt.label} ({opt.role})
          </option>
        ))}
      </select>
      {matchesRole.length === 0 && !loading ? (
        <p className="text-xs text-amber-200">Nenhum agente com esse papel encontrado. Cadastre ou ajuste o papel.</p>
      ) : null}
      {params.agent_label ? (
        <p className="text-[11px] text-slate-300">
          Selecionado: {params.agent_label} {params.agent_id ? `(${params.agent_id})` : ''}
        </p>
      ) : null}
    </div>
  );
}

function renderParamInput(
  step: AgentFlowStepForm,
  key: string,
  type: 'text' | 'number' | 'boolean' | 'textarea',
  controlId: string,
  onChange: (position: number, key: string, value: unknown) => void,
) {
  const value = (step.params || {})[key];
  if (type === 'boolean') {
    return (
      <label className="flex items-center gap-2 text-sm text-slate-200" htmlFor={controlId}>
        <input
          type="checkbox"
          checked={Boolean(value)}
          id={controlId}
          onChange={(e) => onChange(step.position, key, e.target.checked)}
          className="h-4 w-4 rounded border-white/20 bg-white/5 text-sky-500 focus:ring-sky-400"
        />
        Ativar
      </label>
    );
  }
  if (type === 'textarea') {
    return (
      <textarea
        rows={2}
        className="w-full rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-sm text-white focus:border-sky-400"
        value={(value as string) || ''}
        id={controlId}
        onChange={(e) => onChange(step.position, key, e.target.value)}
      />
    );
  }
  return (
    <input
      type={type === 'number' ? 'number' : 'text'}
      className="w-full rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-sm text-white focus:border-sky-400"
      value={value === undefined || value === null ? '' : String(value)}
      id={controlId}
      onChange={(e) => onChange(step.position, key, type === 'number' ? Number(e.target.value) : e.target.value)}
      placeholder="—"
    />
  );
}

function renumber(steps: AgentFlowStepForm[]): AgentFlowStepForm[] {
  return steps.map((s, idx) => ({ ...s, position: idx + 1 }));
}
