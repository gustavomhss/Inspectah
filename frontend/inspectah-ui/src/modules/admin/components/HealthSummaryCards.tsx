import type { AdminHealth } from '../../../core/api/api-types';
import StatusBadge from './StatusBadge';

interface Props {
  health: AdminHealth;
}

function HealthCard({ title, value, status, detail }: { title: string; value: number; status: 'ok' | 'warn'; detail?: string }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-300">{title}</p>
        <StatusBadge status={status} label={status === 'ok' ? 'Saudável' : 'Atenção'} />
      </div>
      <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
      {detail && <p className="mt-1 text-sm text-slate-200">{detail}</p>}
    </div>
  );
}

function HealthSummaryCards({ health }: Props) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <HealthCard
        title="Fontes ativas"
        value={health.sources_total}
        status={health.sources_degraded > 0 ? 'warn' : 'ok'}
        detail={`${health.sources_healthy} saudáveis · ${health.sources_degraded} em atenção`}
      />
      <HealthCard
        title="Casos/Temas"
        value={health.cases_total}
        status={health.cases_attention > 0 ? 'warn' : 'ok'}
        detail={`${health.cases_stable} estáveis · ${health.cases_attention} em atenção/contestação`}
      />
      <div className="rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Integrações</p>
        <div className="mt-3 space-y-2">
          {Object.entries(health.integrations || {}).map(([name, status]) => (
            <div key={name} className="flex items-center justify-between text-sm text-slate-100">
              <span className="capitalize">{name.replace('_', ' ')}</span>
              <StatusBadge status={status === 'ok' ? 'ok' : 'warn'} label={status === 'ok' ? 'OK' : 'Atenção'} />
            </div>
          ))}
          {Object.keys(health.integrations || {}).length === 0 && (
            <p className="text-sm text-slate-200">Sem integrações declaradas</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default HealthSummaryCards;
