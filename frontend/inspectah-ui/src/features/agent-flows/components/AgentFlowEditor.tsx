import { useEffect, useMemo, useState } from 'react';
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

  useEffect(() => {
    setForm(initialFlow);
    setErrors([]);
    clearError();
  }, [initialFlow, clearError]);

  const canSave = useMemo(() => form.domain_key.trim().length > 0 && form.steps.length > 0, [form]);

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

  const warnMissingDecision = useMemo(
    () => !form.steps.some((s) => s.agent_role === 'decision_maker'),
    [form.steps],
  );

  const handleSubmit = async () => {
    clearError();
    setErrors([]);
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

      {(errors.length > 0 || error) && (
        <div className="rounded-xl border border-amber-400/40 bg-amber-400/10 p-3 text-sm text-amber-100">
          <p className="font-semibold">Correções necessárias:</p>
          <ul className="list-disc pl-5">
            {(errors.length ? errors : error?.split(';') || []).map((msg, idx) => (
              <li key={idx}>{msg}</li>
            ))}
          </ul>
        </div>
      )}

      {warnMissingDecision ? (
        <div className="rounded-xl border border-sky-400/30 bg-sky-400/10 p-3 text-xs text-sky-100">
          Adicione um passo com agente Decision Maker para manter a rastreabilidade do fluxo.
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-semibold text-white" htmlFor={domainId}>
            Domínio
          </label>
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
          </div>
          <button
            type="button"
            onClick={handleAddStep}
            className="rounded-full bg-white/10 px-3 py-1 text-sm font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
          >
            Adicionar passo
          </button>
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
                <div className="mt-3 grid gap-3 sm:grid-cols-2">
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
