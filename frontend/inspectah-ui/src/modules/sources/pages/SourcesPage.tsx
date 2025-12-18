/**
 * S38-FE-010: SourcesPage - Console Fontes v1
 */

import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Button from '../../../shared/components/Button';
import { useSources } from '../hooks/useSources';
import SourceCard from '../components/SourceCard';
import * as api from '../api/sourcesApi';

type SourceTypeFilter = 'all' | 'official' | 'scraper' | 'rss' | 'api';
type StateFilter = 'all' | 'ACTIVE' | 'TESTING' | 'PROPOSED' | 'DISABLED_TEMP' | 'DISABLED_PERM';
type HealthFilter = 'all' | 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';

export default function SourcesPage() {
  const { token } = useAuth();
  const [typeFilter, setTypeFilter] = useState<SourceTypeFilter>('all');
  const [stateFilter, setStateFilter] = useState<StateFilter>('all');
  const [healthFilter, setHealthFilter] = useState<HealthFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [triggeringId, setTriggeringId] = useState<string | null>(null);

  const { sources, loading, error, refresh } = useSources({
    source_type: typeFilter !== 'all' ? typeFilter : undefined,
    state: stateFilter !== 'all' ? stateFilter : undefined,
    q: searchQuery || undefined,
  });

  const filteredSources = sources.filter((source) => {
    if (healthFilter !== 'all' && source.last_health_status !== healthFilter) {
      return false;
    }
    return true;
  });

  const handleTriggerIngestion = useCallback(
    async (sourceId: string) => {
      setTriggeringId(sourceId);
      try {
        await api.triggerIngestion(sourceId, {}, token || undefined);
        await refresh();
      } catch (err) {
        console.error('Failed to trigger ingestion:', err);
      } finally {
        setTriggeringId(null);
      }
    },
    [token, refresh]
  );

  const handleHealthCheck = useCallback(
    async (sourceId: string) => {
      try {
        await api.triggerHealthCheck(sourceId, token || undefined);
        await refresh();
      } catch (err) {
        console.error('Failed to trigger health check:', err);
      }
    },
    [token, refresh]
  );

  return (
    <div className="space-y-4">
      <PageHeader
        title="Console de Fontes"
        subtitle="Gerencie fontes de dados, scrapers e integradores oficiais."
      />

      <PageContainer>
        {/* Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="text"
              placeholder="Buscar por nome..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
            />

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as SourceTypeFilter)}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
            >
              <option value="all">Tipo: Todos</option>
              <option value="official">Oficial</option>
              <option value="scraper">Scraper</option>
              <option value="rss">RSS</option>
              <option value="api">API</option>
            </select>

            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value as StateFilter)}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
            >
              <option value="all">Estado: Todos</option>
              <option value="ACTIVE">Ativa</option>
              <option value="TESTING">Em Teste</option>
              <option value="PROPOSED">Proposta</option>
              <option value="DISABLED_TEMP">Desativada Temp</option>
              <option value="DISABLED_PERM">Desativada Perm</option>
            </select>

            <select
              value={healthFilter}
              onChange={(e) => setHealthFilter(e.target.value as HealthFilter)}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
            >
              <option value="all">Saude: Todas</option>
              <option value="HEALTHY">Saudavel</option>
              <option value="DEGRADED">Degradado</option>
              <option value="UNHEALTHY">Falha</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => void refresh()}
              disabled={loading}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white hover:bg-white/10 disabled:opacity-50"
            >
              {loading ? 'Atualizando...' : 'Atualizar'}
            </button>
            <Link to="/admin/sources/new">
              <Button variant="primary">Nova Fonte</Button>
            </Link>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="mt-4 rounded-lg border border-red-500/20 bg-red-500/10 p-4">
            <p className="text-sm text-red-400">{error}</p>
            <button
              onClick={() => void refresh()}
              className="mt-2 text-sm text-blue-400 hover:text-blue-300"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && sources.length === 0 && (
          <div className="mt-4 space-y-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-24 animate-pulse rounded-lg border border-white/10 bg-white/5"
              />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredSources.length === 0 && (
          <div className="mt-8 text-center">
            <p className="text-slate-400">Nenhuma fonte encontrada.</p>
            <Link to="/admin/sources/new" className="mt-2 inline-block text-blue-400 hover:text-blue-300">
              Criar nova fonte
            </Link>
          </div>
        )}

        {/* Sources List */}
        <div className="mt-4 space-y-3">
          {filteredSources.map((source) => (
            <SourceCard
              key={source.id}
              source={source}
              onTriggerIngestion={
                triggeringId === source.id ? undefined : handleTriggerIngestion
              }
              onHealthCheck={handleHealthCheck}
            />
          ))}
        </div>

        {/* Summary */}
        {filteredSources.length > 0 && (
          <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-4 text-sm text-slate-400">
            <span>
              {filteredSources.length} fonte{filteredSources.length !== 1 ? 's' : ''}
              {sources.length !== filteredSources.length && ` (de ${sources.length} total)`}
            </span>
            <span>
              {filteredSources.filter((s) => s.last_health_status === 'HEALTHY').length} saudaveis,{' '}
              {filteredSources.filter((s) => s.last_health_status === 'DEGRADED').length} degradadas,{' '}
              {filteredSources.filter((s) => s.last_health_status === 'UNHEALTHY').length} falhando
            </span>
          </div>
        )}
      </PageContainer>
    </div>
  );
}
