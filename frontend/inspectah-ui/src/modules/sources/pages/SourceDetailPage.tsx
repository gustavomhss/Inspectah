/**
 * S38-FE-010c: SourceDetailPage
 */

import { useCallback, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Button from '../../../shared/components/Button';
import { useSourceDetail } from '../hooks/useSources';
import { useSourceDryRun } from '../hooks/useSourceDryRun';
import SourceMetrics from '../components/SourceMetrics';
import IngestionHistory from '../components/IngestionHistory';
import * as api from '../api/sourcesApi';

const stateLabels: Record<string, string> = {
  PROPOSED: 'Proposta',
  TESTING: 'Em Teste',
  ACTIVE: 'Ativa',
  UNDER_REVIEW: 'Em Revisao',
  SUSPECT: 'Suspeita',
  DISABLED_TEMP: 'Desativada Temp',
  DISABLED_PERM: 'Desativada Perm',
};

const healthLabels: Record<string, string> = {
  HEALTHY: 'Saudavel',
  DEGRADED: 'Degradado',
  UNHEALTHY: 'Falha',
  UNKNOWN: 'Desconhecido',
};

export default function SourceDetailPage() {
  const { sourceId } = useParams<{ sourceId: string }>();
  const navigate = useNavigate();
  const { token } = useAuth();
  const { source, loading, error, refresh } = useSourceDetail(sourceId || null);
  const { result: dryRunResult, loading: dryRunLoading, execute: executeDryRun } = useSourceDryRun();
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const handleTriggerIngestion = useCallback(async () => {
    if (!sourceId) return;
    setActionLoading('trigger');
    try {
      await api.triggerIngestion(sourceId, {}, token || undefined);
      await refresh();
    } catch (err) {
      console.error('Failed to trigger ingestion:', err);
    } finally {
      setActionLoading(null);
    }
  }, [sourceId, token, refresh]);

  const handleDryRun = useCallback(async () => {
    if (!sourceId) return;
    await executeDryRun(sourceId, { limit: 5 });
  }, [sourceId, executeDryRun]);

  const handleHealthCheck = useCallback(async () => {
    if (!sourceId) return;
    setActionLoading('health');
    try {
      await api.triggerHealthCheck(sourceId, token || undefined);
      await refresh();
    } catch (err) {
      console.error('Failed to trigger health check:', err);
    } finally {
      setActionLoading(null);
    }
  }, [sourceId, token, refresh]);

  const handleDelete = useCallback(async () => {
    if (!sourceId) return;
    if (!confirm('Tem certeza que deseja remover esta fonte?')) return;

    setActionLoading('delete');
    try {
      await api.deleteSource(sourceId, token || undefined);
      navigate('/admin/sources');
    } catch (err) {
      console.error('Failed to delete source:', err);
    } finally {
      setActionLoading(null);
    }
  }, [sourceId, token, navigate]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 w-48 rounded bg-white/10" />
        <div className="h-64 rounded-lg bg-white/10" />
      </div>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-6 text-center">
          <p className="text-red-400">{error}</p>
          <Link to="/admin/sources" className="mt-4 inline-block text-blue-400 hover:text-blue-300">
            Voltar para lista
          </Link>
        </div>
      </PageContainer>
    );
  }

  if (!source) {
    return (
      <PageContainer>
        <div className="text-center">
          <p className="text-slate-400">Fonte nao encontrada.</p>
          <Link to="/admin/sources" className="mt-4 inline-block text-blue-400 hover:text-blue-300">
            Voltar para lista
          </Link>
        </div>
      </PageContainer>
    );
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title={source.name}
        subtitle={source.description || source.url}
        backLink="/admin/sources"
      />

      <PageContainer>
        {/* Header Actions */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-blue-500/20 px-3 py-1 text-sm text-blue-300">
              {stateLabels[source.state] || source.state}
            </span>
            <span className="rounded-full bg-slate-500/20 px-3 py-1 text-sm text-slate-300">
              {healthLabels[source.last_health_status] || source.last_health_status}
            </span>
            <span className="text-sm text-slate-400">
              {source.enabled ? 'Habilitada' : 'Desabilitada'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              onClick={handleDryRun}
              disabled={dryRunLoading}
            >
              {dryRunLoading ? 'Testando...' : 'Dry-Run'}
            </Button>
            <Button
              variant="secondary"
              onClick={handleHealthCheck}
              disabled={actionLoading === 'health'}
            >
              {actionLoading === 'health' ? 'Verificando...' : 'Health Check'}
            </Button>
            <Button
              variant="primary"
              onClick={handleTriggerIngestion}
              disabled={actionLoading === 'trigger' || !source.enabled}
            >
              {actionLoading === 'trigger' ? 'Disparando...' : 'Ingerir Agora'}
            </Button>
            <Link to={`/admin/sources/${sourceId}/edit`}>
              <Button variant="secondary">Editar</Button>
            </Link>
            <Button
              variant="danger"
              onClick={handleDelete}
              disabled={actionLoading === 'delete'}
            >
              {actionLoading === 'delete' ? 'Removendo...' : 'Remover'}
            </Button>
          </div>
        </div>

        {/* Dry Run Result */}
        {dryRunResult && (
          <div className={`mt-4 rounded-lg border p-4 ${
            dryRunResult.success
              ? 'border-green-500/20 bg-green-500/10'
              : 'border-red-500/20 bg-red-500/10'
          }`}>
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-white">Resultado do Dry-Run</h4>
              <span className="text-sm text-slate-400">{dryRunResult.latency_ms.toFixed(0)}ms</span>
            </div>
            {dryRunResult.success ? (
              <p className="mt-2 text-sm text-green-400">
                Encontrados {dryRunResult.documents_found} documentos
              </p>
            ) : (
              <p className="mt-2 text-sm text-red-400">{dryRunResult.error_message}</p>
            )}
            {dryRunResult.sample_documents.length > 0 && (
              <pre className="mt-2 max-h-48 overflow-auto rounded bg-black/30 p-2 text-xs text-slate-300">
                {JSON.stringify(dryRunResult.sample_documents, null, 2)}
              </pre>
            )}
          </div>
        )}

        {/* Source Details */}
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-white/10 bg-white/5 p-4">
            <h3 className="font-semibold text-white">Configuracao</h3>
            <dl className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-400">Slug</dt>
                <dd className="text-white font-mono">{source.slug}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-400">Tipo</dt>
                <dd className="text-white">{source.source_type}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-400">Rate Limit</dt>
                <dd className="text-white">{source.rate_limit_rpm} req/min</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-400">URL</dt>
                <dd className="text-white truncate max-w-[200px]" title={source.url}>
                  {source.url}
                </dd>
              </div>
            </dl>
          </div>

          {source.health_stats && (
            <div className="rounded-lg border border-white/10 bg-white/5 p-4">
              <h3 className="font-semibold text-white">Saude</h3>
              <dl className="mt-3 space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-400">Uptime</dt>
                  <dd className="text-white">{source.health_stats.uptime_percent.toFixed(1)}%</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-400">Latencia Media</dt>
                  <dd className="text-white">{source.health_stats.avg_latency_ms.toFixed(0)}ms</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-400">Total Checks</dt>
                  <dd className="text-white">{source.health_stats.total_checks}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-400">Falhas</dt>
                  <dd className="text-white">{source.health_stats.total_failures}</dd>
                </div>
              </dl>
            </div>
          )}
        </div>

        {/* Metrics */}
        {sourceId && (
          <div className="mt-6">
            <SourceMetrics sourceId={sourceId} />
          </div>
        )}

        {/* Ingestion History */}
        {sourceId && (
          <div className="mt-6">
            <IngestionHistory sourceId={sourceId} limit={10} />
          </div>
        )}
      </PageContainer>
    </div>
  );
}
