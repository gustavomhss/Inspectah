import { useMemo, useState } from 'react';
import { AdminContent, Badge, Button } from '@/ui/admin';
import { runNewsdataIngest } from './api';
import { useRollout, useRolloutActions } from './hooks';
import type { Flow, NewsdataItem } from './types';

interface Props {
  flow: Flow;
  onUpdated?: (flow: Flow) => void;
}

export function FlowRolloutPanel({ flow, onUpdated }: Props) {
  const safeCrypto = typeof globalThis !== 'undefined' && globalThis.crypto ? globalThis.crypto : undefined;
  const safeNavigator = typeof globalThis !== 'undefined' && globalThis.navigator ? globalThis.navigator : undefined;
  const genOpId = () => {
    try {
      return safeCrypto?.randomUUID ? safeCrypto.randomUUID() : `op-${Date.now()}-${Math.random().toString(16).slice(2, 6)}`;
    } catch {
      return `op-${Date.now()}`;
    }
  };
  const { status, catalog, reload } = useRollout(flow.id);
  const { start, promote, rollback, saving, error, setError } = useRolloutActions(flow.id, onUpdated);
  const [mode, setMode] = useState('canary');
  const [percentual, setPercentual] = useState(flow.percentual_teste || 10);
  const allowedActors = ['ops_user', 'ops_admin', 'ops_ingest'];
  const [actor, setActor] = useState('ops_user');
  const [criteria, setCriteria] = useState<string>('{"slo_id":"slo_rollout"}');
  const [operationId, setOperationId] = useState(() => genOpId());
  const [newsItems, setNewsItems] = useState<NewsdataItem[]>([]);
  const [newsState, setNewsState] = useState<'idle' | 'loading' | 'success' | 'empty' | 'rate_limit' | 'timeout' | 'error'>('idle');
  const [newsError, setNewsError] = useState<string | null>(null);

  const catalogEntry = useMemo(() => catalog.find((c) => c.flow_id === flow.slug || c.flow_id === flow.id), [catalog, flow]);
  const alerts = status?.alerts || [];
  const sloStatus = status?.slo_status || [];
  const rolloutHash = status?.catalog_hash || catalogEntry?.hash || '—';
  const currentOpId = status?.operation_id || operationId;
  const hasDrift = alerts.includes('catalog_hash_drift');
  const hasActor = Boolean(actor);
  const ingestRole = 'ops_ingest';
  const canIngest = ingestRole === 'ops_ingest';

  const triggerNewsdata = async () => {
    setNewsState('loading');
    setNewsError(null);
    try {
      const run = await runNewsdataIngest();
      const items = run.meta?.items_sample || [];
      setNewsItems(items);
      if (!run.items_processed || run.items_processed === 0) {
        setNewsState('empty');
      } else {
        setNewsState('success');
      }
    } catch (err) {
      const message = (err as Error).message || 'Erro na ingestão';
      setNewsError(message);
      if (message.includes('429')) {
        setNewsState('rate_limit');
      } else if (message.toLowerCase().includes('timeout')) {
        setNewsState('timeout');
      } else {
        setNewsState('error');
      }
    }
  };

  return (
    <AdminContent>
      <div className="space-y-4 text-slate-50">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xl font-bold text-white">Rollout governado</h4>
            <p className="text-sm text-slate-200">Promova versões de fluxo com hash assinado, SLO e rollback seguro.</p>
          </div>
          <div className="flex items-center gap-2">
          <Badge tone={hasDrift ? 'danger' : 'info'}>{hasDrift ? 'Drift de catálogo' : 'Catalog hash'}: {rolloutHash?.toString().slice(0, 12)}</Badge>
          <Badge tone="neutral">Op ID: {currentOpId}</Badge>
          <Button
            size="xs"
            variant="primary"
            onClick={() => safeNavigator?.clipboard?.writeText?.(currentOpId || '')}
            className="bg-sky-600 text-white hover:bg-sky-700"
          >
            Copiar op_id
          </Button>
        </div>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-sm text-slate-100">
          <p className="font-semibold text-white">Guia rápido (o que é e como usar)</p>
          <ul className="mt-2 space-y-1 text-sm leading-snug">
            <li><strong>Rollout</strong>: move o fluxo de teste para produção em modo canário (percentual) com SLO/alertas. Usa o hash do catálogo assinado.</li>
            <li><strong>Modo</strong>: “canary” libera para uma fração (Percentual). “test” deixa só em ambiente de teste.</li>
            <li><strong>Actor</strong>: quem está operando (ops_user/ops_admin/ops_ingest). Obrigatório para auditoria.</li>
            <li><strong>Critério</strong>: JSON de SLO/policy (ex: {"{ \"slo_id\": \"slo_rollout\" }"}). Usado para decidir promote/rollback.</li>
            <li><strong>Iniciar rollout</strong>: cria operação com op_id + hash atual. “Promover” fixa a versão ativa. “Rollback” volta para a anterior.</li>
            <li><strong>Ingestão newsdata</strong>: CTA ops_only que dispara o pipeline real para gerar métricas e validar o fluxo.</li>
          </ul>
        </div>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="space-y-2">
          {error && (
            <div className="rounded border border-rose-500/50 bg-rose-900/40 p-3 text-sm text-rose-100" role="alert">
              {typeof error === 'string' ? error : 'Erro na operação'}
              <Button size="xs" variant="ghost" className="ml-2 text-slate-100" onClick={() => setError(null)}>
                Limpar
              </Button>
            </div>
          )}
          {alerts.length > 0 && (
            <div className="rounded border border-amber-400/60 bg-amber-900/30 p-3 text-sm text-amber-100">
              Alertas: {alerts.join(', ')}
            </div>
          )}
          {sloStatus.length > 0 && (
            <div className="rounded border border-emerald-400/60 bg-emerald-900/30 p-3 text-sm text-emerald-100">
              SLOs: {sloStatus.map((s) => `${s.slo_id}:${s.status}`).join(', ')}
            </div>
          )}
        </div>
        <div className="md:col-span-2 grid gap-3 md:grid-cols-3">
          <div className="rounded border border-slate-700 bg-slate-800 p-3">
            <p className="text-sm text-slate-200">Modo</p>
            <p className="text-lg font-semibold text-white">{status?.rollout_mode || 'idle'}</p>
            <p className="text-xs text-slate-300">Estado: {status?.rollout_state || '—'}</p>
            <p className="text-[11px] text-slate-400">Op ID: {currentOpId}</p>
          </div>
          <div className="rounded border border-slate-700 bg-slate-800 p-3">
            <p className="text-sm text-slate-200">Versões</p>
            <p className="text-xs text-slate-300">Ativa: {status?.active_version_id || flow.active_version_id || '—'}</p>
            <p className="text-xs text-slate-300">Teste: {status?.test_version_id || flow.test_version_id || '—'}</p>
          </div>
          <div className="rounded border border-slate-700 bg-slate-800 p-3">
            <p className="text-sm text-slate-200">Catálogo</p>
            <p className="text-xs text-slate-300 break-all">Hash: {rolloutHash}</p>
            <p className="text-xs text-slate-300">Assinatura: {status?.catalog_signature || catalogEntry?.signature || '—'}</p>
          </div>
        </div>
      </div>

      <div className="mt-3 space-y-2">
        <div className="flex flex-wrap gap-2 items-center">
          <label className="text-sm text-slate-100" htmlFor="rollout-mode">
            Modo:
          </label>
          <select
            id="rollout-mode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="border border-slate-600 bg-slate-800 text-slate-50 rounded px-2 py-1 text-sm"
          >
            <option value="canary">canary</option>
            <option value="test">test</option>
          </select>
          <label className="text-sm text-slate-100" htmlFor="rollout-percentual">
            Percentual:
          </label>
          <input
            id="rollout-percentual"
            type="number"
            min={1}
            max={100}
            value={percentual}
            onChange={(e) => setPercentual(Number(e.target.value))}
            className="border border-slate-600 bg-slate-800 text-slate-50 rounded px-2 py-1 text-sm w-20"
          />
          <label className="text-sm text-slate-100" htmlFor="rollout-actor">
            Actor:
          </label>
          <select
            id="rollout-actor"
            value={actor}
            onChange={(e) => setActor(e.target.value)}
            className="border border-slate-600 bg-slate-800 text-slate-50 rounded px-2 py-1 text-sm"
          >
            {allowedActors.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
          {!hasActor && <span className="text-xs text-rose-600">Actor obrigatório</span>}
          <label className="text-sm text-slate-100" htmlFor="rollout-criteria">
            Critério (JSON):
          </label>
          <input
            id="rollout-criteria"
            type="text"
            value={criteria}
            onChange={(e) => setCriteria(e.target.value)}
            className="border border-slate-600 bg-slate-800 text-slate-50 rounded px-2 py-1 text-sm w-64"
          />
          <Button
            size="sm"
            onClick={() => {
              let parsed: Record<string, unknown> | undefined;
              try {
                parsed = JSON.parse(criteria || '{}');
              } catch (e) {
                setError('Critério inválido (JSON esperado)');
                return;
              }
              const opId = safeCrypto?.randomUUID ? safeCrypto.randomUUID() : `op-${Date.now()}`;
              setOperationId(opId);
              start({ mode, test_percentual: percentual, actor, criteria: parsed, operation_id: opId, catalog_hash: rolloutHash?.toString() || '' });
              void reload();
            }}
            disabled={saving || !hasActor || !rolloutHash}
            variant="primary"
            className="bg-emerald-600 text-white hover:bg-emerald-700"
          >
            {saving ? 'Iniciando...' : 'Iniciar rollout'}
          </Button>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="secondary"
            className="bg-slate-700 text-slate-50 hover:bg-slate-600"
            onClick={() => {
              const opId = safeCrypto?.randomUUID ? safeCrypto.randomUUID() : `op-${Date.now()}`;
              setOperationId(opId);
              void promote({ actor, operation_id: opId, catalog_hash: rolloutHash?.toString() || '' });
              void reload();
            }}
            disabled={saving || !hasActor || !rolloutHash}
          >
            Promover
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => {
              const opId = safeCrypto?.randomUUID ? safeCrypto.randomUUID() : `op-${Date.now()}`;
              setOperationId(opId);
              void rollback(flow.flow_version_id, { actor, operation_id: opId, catalog_hash: rolloutHash?.toString() || '' });
              void reload();
            }}
            disabled={saving || !hasActor || !rolloutHash}
            className="bg-slate-700 text-slate-50 hover:bg-slate-600"
          >
            Rollback
          </Button>
          <Button size="sm" variant="ghost" onClick={() => void reload()} disabled={saving} className="text-slate-100">
            Atualizar status
          </Button>
        </div>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-sky-700 bg-slate-800 p-3">
          <div className="flex items-center justify-between mb-2">
            <div>
              <p className="text-sm font-semibold text-white">Ingestão newsdata.io (ops_only)</p>
              <p className="text-xs text-slate-200">Throttling/backoff 1/2/4s + jitter, size=50, domains BR. CTA exige role ops_ingest.</p>
            </div>
            <Button
              size="sm"
              variant="primary"
              className="bg-sky-500 text-white hover:bg-sky-600"
              disabled={!canIngest || newsState === 'loading'}
              onClick={() => void triggerNewsdata()}
            >
              {newsState === 'loading' ? 'Buscando...' : 'Rodar ingestão'}
            </Button>
          </div>
          {newsError && (
            <div className="rounded border border-rose-500/50 bg-rose-900/40 p-2 text-sm text-rose-100" role="alert">
              {newsError}
            </div>
          )}
          {newsState === 'rate_limit' && <p className="text-xs text-amber-200">Fonte externa limitou (429). Retry com backoff aplicado.</p>}
          {newsState === 'timeout' && <p className="text-xs text-amber-200">Timeout na fonte externa. Verifique conectividade.</p>}
          {newsState === 'empty' && <p className="text-xs text-slate-200">Nenhum artigo recebido da fonte (empty feed).</p>}
          {newsState === 'success' && newsItems.length === 0 && <p className="text-xs text-slate-200">Ingestão concluída sem itens.</p>}
          {newsItems.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-slate-100">Amostra de artigos reais (hash inclui id/title/link/pubDate/source/category/desc):</p>
              <ul className="divide-y divide-slate-700 rounded border border-slate-700 bg-slate-900">
                {newsItems.map((item) => (
                  <li key={`${item.id}-${item.pubDate}`} className="p-2">
                    <p className="text-sm font-semibold text-white">{item.title}</p>
                    <p className="text-xs text-slate-200">Fonte: {item.source_id} | Publicado: {item.pubDate}</p>
                    <p className="text-[11px] text-slate-300 break-words">{item.link}</p>
                    {item.description && <p className="text-[11px] text-slate-400">{item.description.slice(0, 160)}…</p>}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <p className="text-[11px] text-slate-300 mt-2">Backoff 1/2/4s com jitter, throttling ≤60 rpm. Role ops_ingest aplicada no header.</p>
        </div>
        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-3 flex flex-col gap-3">
          <div>
            <p className="text-sm font-semibold text-white">Configurar rollout</p>
            <p className="text-xs text-slate-300">Defina modo, percentual, actor e critério antes de iniciar/promover/rollback.</p>
          </div>
          <div className="mt-1 space-y-2 rounded border border-slate-700 bg-slate-900/70 p-3">
            <div className="flex flex-wrap gap-2 items-center">
              <label className="text-sm text-slate-100" htmlFor="rollout-mode">
                Modo:
              </label>
              <select
                id="rollout-mode"
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="border border-slate-600 bg-slate-800 text-slate-50 rounded px-2 py-1 text-sm"
              >
                <option value="canary">canary</option>
                <option value="test">test</option>
              </select>
              <label className="text-sm text-slate-100" htmlFor="rollout-percentual">
                Percentual:
              </label>
              <input
                id="rollout-percentual"
                type="number"
                min={1}
                max={100}
                value={percentual}
                onChange={(e) => setPercentual(Number(e.target.value))}
                className="border border-slate-600 bg-slate-800 text-slate-50 rounded px-2 py-1 text-sm w-20"
              />
              <label className="text-sm text-slate-100" htmlFor="rollout-actor">
                Actor:
              </label>
              <select
                id="rollout-actor"
                value={actor}
                onChange={(e) => setActor(e.target.value)}
                className="border border-slate-600 bg-slate-800 text-slate-50 rounded px-2 py-1 text-sm"
              >
                {allowedActors.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
              {!hasActor && <span className="text-xs text-rose-300">Actor obrigatório</span>}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <label className="text-sm text-slate-100" htmlFor="rollout-criteria">
                Critério (JSON):
              </label>
              <input
                id="rollout-criteria"
                type="text"
                value={criteria}
                onChange={(e) => setCriteria(e.target.value)}
                className="border border-slate-600 bg-slate-800 text-slate-50 rounded px-2 py-1 text-sm w-full md:w-72"
              />
              <Button
                size="sm"
                onClick={() => {
                  let parsed: Record<string, unknown> | undefined;
                  try {
                    parsed = JSON.parse(criteria || '{}');
                  } catch (e) {
                    setError('Critério inválido (JSON esperado)');
                    return;
                  }
                  const opId = safeCrypto?.randomUUID ? safeCrypto.randomUUID() : `op-${Date.now()}`;
                  setOperationId(opId);
                  start({ mode, test_percentual: percentual, actor, criteria: parsed, operation_id: opId, catalog_hash: rolloutHash?.toString() || '' });
                  void reload();
                }}
                disabled={saving || !hasActor || !rolloutHash}
                variant="primary"
                className="bg-emerald-600 text-white hover:bg-emerald-700"
              >
                {saving ? 'Iniciando...' : 'Iniciar rollout'}
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                variant="secondary"
                className="bg-slate-700 text-slate-50 hover:bg-slate-600"
                onClick={() => {
                  const opId = safeCrypto?.randomUUID ? safeCrypto.randomUUID() : `op-${Date.now()}`;
                  setOperationId(opId);
                  void promote({ actor, operation_id: opId, catalog_hash: rolloutHash?.toString() || '' });
                  void reload();
                }}
                disabled={saving || !hasActor || !rolloutHash}
              >
                Promover
              </Button>
              <Button
                size="sm"
                variant="secondary"
                className="bg-slate-700 text-slate-50 hover:bg-slate-600"
                onClick={() => {
                  const opId = safeCrypto?.randomUUID ? safeCrypto.randomUUID() : `op-${Date.now()}`;
                  setOperationId(opId);
                  void rollback(flow.flow_version_id, { actor, operation_id: opId, catalog_hash: rolloutHash?.toString() || '' });
                  void reload();
                }}
                disabled={saving || !hasActor || !rolloutHash}
              >
                Rollback
              </Button>
              <Button size="sm" variant="ghost" onClick={() => void reload()} disabled={saving} className="text-slate-100">
                Atualizar status
              </Button>
            </div>
          </div>
        </div>
      </div>
      </div>
    </AdminContent>
  );
}
