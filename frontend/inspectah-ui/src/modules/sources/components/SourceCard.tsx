/**
 * S38-FE-010: SourceCard Component
 */

import { Link } from 'react-router-dom';
import type { Source, HealthStatus, SourceState } from '../types';

interface SourceCardProps {
  source: Source;
  onTriggerIngestion?: (sourceId: string) => void;
  onHealthCheck?: (sourceId: string) => void;
}

const healthColors: Record<HealthStatus, string> = {
  HEALTHY: 'bg-green-500',
  DEGRADED: 'bg-yellow-500',
  UNHEALTHY: 'bg-red-500',
  UNKNOWN: 'bg-gray-500',
};

const healthLabels: Record<HealthStatus, string> = {
  HEALTHY: 'Saudavel',
  DEGRADED: 'Degradado',
  UNHEALTHY: 'Falha',
  UNKNOWN: 'Desconhecido',
};

const stateColors: Record<SourceState, string> = {
  PROPOSED: 'bg-blue-500/20 text-blue-300',
  TESTING: 'bg-purple-500/20 text-purple-300',
  ACTIVE: 'bg-green-500/20 text-green-300',
  UNDER_REVIEW: 'bg-yellow-500/20 text-yellow-300',
  SUSPECT: 'bg-orange-500/20 text-orange-300',
  DISABLED_TEMP: 'bg-gray-500/20 text-gray-300',
  DISABLED_PERM: 'bg-red-500/20 text-red-300',
};

const stateLabels: Record<SourceState, string> = {
  PROPOSED: 'Proposta',
  TESTING: 'Em Teste',
  ACTIVE: 'Ativa',
  UNDER_REVIEW: 'Em Revisao',
  SUSPECT: 'Suspeita',
  DISABLED_TEMP: 'Desativada Temp',
  DISABLED_PERM: 'Desativada Perm',
};

const typeLabels: Record<string, string> = {
  official: 'Oficial',
  scraper: 'Scraper',
  rss: 'RSS',
  api: 'API',
};

export default function SourceCard({ source, onTriggerIngestion, onHealthCheck }: SourceCardProps) {
  const healthStatus = source.last_health_status || 'UNKNOWN';

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4 transition-colors hover:bg-white/10">
      <div className="flex items-start justify-between gap-4">
        {/* Info */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <Link
              to={`/admin/sources/${source.id}`}
              className="truncate text-lg font-semibold text-white hover:text-blue-400"
            >
              {source.name}
            </Link>
            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs ${stateColors[source.state]}`}>
              {stateLabels[source.state]}
            </span>
          </div>

          <div className="mt-1 flex items-center gap-3 text-sm text-slate-400">
            <span className="inline-flex items-center gap-1">
              <span className={`h-2 w-2 rounded-full ${healthColors[healthStatus]}`} />
              {healthLabels[healthStatus]}
            </span>
            <span>{typeLabels[source.source_type] || source.source_type}</span>
            <span className="truncate max-w-[200px]" title={source.url}>
              {source.url}
            </span>
          </div>

          {source.description && (
            <p className="mt-2 text-sm text-slate-300 line-clamp-2">{source.description}</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {onHealthCheck && (
            <button
              onClick={() => onHealthCheck(source.id)}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white hover:bg-white/10"
              title="Verificar saude"
            >
              Health
            </button>
          )}
          {onTriggerIngestion && source.enabled && (
            <button
              onClick={() => onTriggerIngestion(source.id)}
              className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
              title="Disparar ingestao"
            >
              Ingerir
            </button>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-3 flex items-center justify-between border-t border-white/10 pt-3 text-xs text-slate-500">
        <span>Rate limit: {source.rate_limit_rpm} req/min</span>
        <span>
          Atualizado: {new Date(source.updated_at).toLocaleDateString('pt-BR')}
        </span>
      </div>
    </div>
  );
}
