import { useMemo, useState } from 'react';
import { AdminContent, Badge, Button } from '@/ui/admin';
import { useRollout, useRolloutActions } from './hooks';
import type { Flow } from './types';

interface Props {
  flow: Flow;
  onUpdated?: (flow: Flow) => void;
}

export function FlowRolloutPanel({ flow, onUpdated }: Props) {
  const { status, catalog } = useRollout(flow.id);
  const { start, promote, rollback, saving, error, setError } = useRolloutActions(flow.id, onUpdated);
  const [mode, setMode] = useState('canary');
  const [percentual, setPercentual] = useState(flow.percentual_teste || 10);
  const allowedActors = ['ops_user', 'ops_admin'];
  const [actor, setActor] = useState('ops_user');
  const [criteria, setCriteria] = useState<string>('{"slo_id":"slo_rollout"}');

  const catalogEntry = useMemo(() => catalog.find((c) => c.flow_id === flow.slug || c.flow_id === flow.id), [catalog, flow]);
  const alerts = status?.alerts || [];
  const sloStatus = status?.slo_status || [];

  return (
    <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-base font-semibold text-slate-900">Rollout governado</h4>
        {catalogEntry && <Badge tone="info">catalog hash: {catalogEntry.hash?.slice(0, 8) || '—'}</Badge>}
      </div>
      {error && (
        <div className="rounded border border-rose-200 bg-rose-50 p-2 text-sm text-rose-800 mb-2" role="alert">
          {error}
          <Button size="xs" variant="ghost" className="ml-2" onClick={() => setError(null)}>
            Limpar
          </Button>
        </div>
      )}
      {alerts.length > 0 && (
        <div className="rounded border border-amber-200 bg-amber-50 p-2 text-sm text-amber-800 mb-2">
          Alertas: {alerts.join(', ')}
        </div>
      )}
      {sloStatus.length > 0 && (
        <div className="rounded border border-emerald-200 bg-emerald-50 p-2 text-sm text-emerald-800 mb-2">
          SLOs: {sloStatus.map((s) => `${s.slo_id}:${s.status}`).join(', ')}
        </div>
      )}
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded border border-slate-200 p-3">
          <p className="text-sm text-slate-600">Modo</p>
          <p className="text-lg font-semibold text-slate-900">{status?.rollout_mode || 'idle'}</p>
          <p className="text-xs text-slate-500">Estado: {status?.rollout_state || '—'}</p>
        </div>
        <div className="rounded border border-slate-200 p-3">
          <p className="text-sm text-slate-600">Versões</p>
          <p className="text-xs text-slate-500">Ativa: {status?.active_version_id || flow.active_version_id || '—'}</p>
          <p className="text-xs text-slate-500">Teste: {status?.test_version_id || flow.test_version_id || '—'}</p>
        </div>
        <div className="rounded border border-slate-200 p-3">
          <p className="text-sm text-slate-600">Catálogo</p>
          <p className="text-xs text-slate-500">Hash: {status?.catalog_hash || catalogEntry?.hash || '—'}</p>
          <p className="text-xs text-slate-500">Assinatura: {status?.catalog_signature || catalogEntry?.signature || '—'}</p>
        </div>
      </div>

      <div className="mt-3 space-y-2">
        <div className="flex flex-wrap gap-2 items-center">
          <label className="text-sm text-slate-700" htmlFor="rollout-mode">
            Modo:
          </label>
          <select
            id="rollout-mode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="border border-slate-200 rounded px-2 py-1 text-sm"
          >
            <option value="canary">canary</option>
            <option value="test">test</option>
          </select>
          <label className="text-sm text-slate-700" htmlFor="rollout-percentual">
            Percentual:
          </label>
          <input
            id="rollout-percentual"
            type="number"
            min={1}
            max={100}
            value={percentual}
            onChange={(e) => setPercentual(Number(e.target.value))}
            className="border border-slate-200 rounded px-2 py-1 text-sm w-20"
          />
          <label className="text-sm text-slate-700" htmlFor="rollout-actor">
            Actor:
          </label>
          <select
            id="rollout-actor"
            value={actor}
            onChange={(e) => setActor(e.target.value)}
            className="border border-slate-200 rounded px-2 py-1 text-sm"
          >
            {allowedActors.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
          <label className="text-sm text-slate-700" htmlFor="rollout-criteria">
            Critério (JSON):
          </label>
          <input
            id="rollout-criteria"
            type="text"
            value={criteria}
            onChange={(e) => setCriteria(e.target.value)}
            className="border border-slate-200 rounded px-2 py-1 text-sm w-64"
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
              start({ mode, test_percentual: percentual, actor, criteria: parsed });
            }}
            disabled={saving}
            variant="primary"
          >
            {saving ? 'Iniciando...' : 'Iniciar rollout'}
          </Button>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button size="sm" variant="secondary" onClick={() => promote({ actor })} disabled={saving}>
            Promover
          </Button>
          <Button size="sm" variant="secondary" onClick={() => rollback(flow.flow_version_id, { actor })} disabled={saving}>
            Rollback
          </Button>
        </div>
      </div>
    </AdminContent>
  );
}
