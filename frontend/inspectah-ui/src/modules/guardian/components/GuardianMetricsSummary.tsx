/**
 * GuardianMetricsSummary — S37
 *
 * Summary cards for Guardian metrics
 */

import type { GuardianMetrics } from '../types';

interface GuardianMetricsSummaryProps {
  metrics: GuardianMetrics;
}

interface MetricCardProps {
  label: string;
  value: number | string;
  subValue?: string;
  color?: string;
}

function MetricCard({ label, value, subValue, color = 'text-white' }: MetricCardProps) {
  return (
    <div className="rounded-lg bg-slate-800/50 p-4 border border-white/10">
      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
      {subValue && <p className="text-xs text-slate-500 mt-0.5">{subValue}</p>}
    </div>
  );
}

function GuardianMetricsSummary({ metrics }: GuardianMetricsSummaryProps) {
  const approvalRate =
    metrics.decisions_submitted > 0
      ? ((metrics.decisions_approved / metrics.decisions_submitted) * 100).toFixed(1)
      : '0.0';

  const timeoutRate =
    metrics.decisions_submitted > 0
      ? ((metrics.decisions_timed_out / metrics.decisions_submitted) * 100).toFixed(1)
      : '0.0';

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <MetricCard
        label="Total Decisões"
        value={metrics.decisions_submitted}
        subValue={`${metrics.pending_decisions} pendentes`}
      />
      <MetricCard
        label="Aprovadas"
        value={metrics.decisions_approved}
        subValue={`${approvalRate}% taxa`}
        color="text-green-400"
      />
      <MetricCard
        label="Rejeitadas"
        value={metrics.decisions_rejected}
        color="text-red-400"
      />
      <MetricCard
        label="Latência Média"
        value={`${metrics.avg_latency_ms.toFixed(0)}ms`}
        subValue={metrics.avg_latency_ms <= 20000 ? 'Dentro do SLA' : 'Acima do SLA'}
        color={metrics.avg_latency_ms <= 20000 ? 'text-green-400' : 'text-red-400'}
      />
      <MetricCard
        label="Aguardando Revisão"
        value={metrics.awaiting_review}
        color="text-amber-400"
      />
      <MetricCard
        label="Aguardando Quórum"
        value={metrics.awaiting_quorum}
        color="text-purple-400"
      />
      <MetricCard
        label="Timeout"
        value={metrics.decisions_timed_out}
        subValue={`${timeoutRate}% taxa`}
        color={parseFloat(timeoutRate) > 5 ? 'text-red-400' : 'text-slate-400'}
      />
      <MetricCard
        label="SLA Status"
        value={metrics.avg_latency_ms <= 20000 ? 'OK' : 'ALERTA'}
        subValue="Target: ≤20s P95"
        color={metrics.avg_latency_ms <= 20000 ? 'text-green-400' : 'text-red-400'}
      />
    </div>
  );
}

export default GuardianMetricsSummary;
