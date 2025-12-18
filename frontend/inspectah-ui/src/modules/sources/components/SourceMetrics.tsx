/**
 * S38-FE-011: SourceMetrics Component
 */

import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import type { SourceMetrics as SourceMetricsType } from '../types';
import * as api from '../api/sourcesApi';

interface SourceMetricsProps {
  sourceId: string;
}

type Period = '1h' | '24h' | '7d';

export default function SourceMetrics({ sourceId }: SourceMetricsProps) {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState<SourceMetricsType | null>(null);
  const [period, setPeriod] = useState<Period>('24h');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getSourceMetrics(sourceId, period, token || undefined);
      setMetrics(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [sourceId, period, token]);

  useEffect(() => {
    void fetchMetrics();
  }, [fetchMetrics]);

  if (loading) {
    return (
      <div className="animate-pulse rounded-lg border border-white/10 bg-white/5 p-4">
        <div className="h-4 w-24 rounded bg-white/10" />
        <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-16 rounded bg-white/10" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
        <p className="text-sm text-red-400">Erro ao carregar metricas: {error}</p>
      </div>
    );
  }

  if (!metrics) {
    return null;
  }

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Metricas</h3>
        <div className="flex items-center gap-1 rounded-lg border border-white/10 bg-white/5 p-1">
          {(['1h', '24h', '7d'] as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`rounded px-3 py-1 text-sm transition-colors ${
                period === p
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricCard
          label="Documentos"
          value={metrics.total_documents.toLocaleString()}
          subtitle={`${metrics.documents_per_hour.toFixed(1)}/hora`}
        />
        <MetricCard
          label="Latencia Media"
          value={`${metrics.avg_latency_ms.toFixed(0)}ms`}
          subtitle={metrics.avg_latency_ms < 200 ? 'Bom' : metrics.avg_latency_ms < 500 ? 'Regular' : 'Lento'}
          valueColor={metrics.avg_latency_ms < 200 ? 'text-green-400' : metrics.avg_latency_ms < 500 ? 'text-yellow-400' : 'text-red-400'}
        />
        <MetricCard
          label="Taxa de Sucesso"
          value={`${(metrics.success_rate * 100).toFixed(1)}%`}
          subtitle={`${metrics.error_count} erros`}
          valueColor={metrics.success_rate > 0.95 ? 'text-green-400' : metrics.success_rate > 0.8 ? 'text-yellow-400' : 'text-red-400'}
        />
        <MetricCard
          label="Ultima Ingestao"
          value={metrics.last_ingestion ? formatRelativeTime(metrics.last_ingestion) : 'Nunca'}
          subtitle={metrics.last_ingestion ? new Date(metrics.last_ingestion).toLocaleString('pt-BR') : ''}
        />
      </div>
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  subtitle?: string;
  valueColor?: string;
}

function MetricCard({ label, value, subtitle, valueColor = 'text-white' }: MetricCardProps) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-3">
      <p className="text-xs text-slate-400">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${valueColor}`}>{value}</p>
      {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
}

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Agora';
  if (diffMins < 60) return `${diffMins}min atras`;
  if (diffHours < 24) return `${diffHours}h atras`;
  return `${diffDays}d atras`;
}
