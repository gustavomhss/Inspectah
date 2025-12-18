import { useState } from 'react';
import { Link } from 'react-router-dom';
import { clsx } from 'clsx';
import { SpCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpInput } from '../../components/ui/Input';
import { SpBadge } from '../../components/ui/Badge';
import {
  SpTable,
  SpTableHead,
  SpTableBody,
  SpTableRow,
  SpTableHeader,
  SpTableCell,
} from '../../components/ui/Table';

interface Source {
  id: string;
  slug: string;
  name: string;
  type: 'official' | 'scraper' | 'rss' | 'api';
  state: 'ACTIVE' | 'TESTING' | 'PROPOSED' | 'DISABLED_TEMP' | 'DISABLED_PERM';
  health: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
  lastRun: string;
  itemsCount: number;
  uptime: number;
}

const mockSources: Source[] = [
  {
    id: '1',
    slug: 'agencia-brasil',
    name: 'Agência Brasil',
    type: 'official',
    state: 'ACTIVE',
    health: 'HEALTHY',
    lastRun: '2024-01-15T10:30:00Z',
    itemsCount: 1234,
    uptime: 99.8,
  },
  {
    id: '2',
    slug: 'g1-politica',
    name: 'G1 Política',
    type: 'scraper',
    state: 'ACTIVE',
    health: 'DEGRADED',
    lastRun: '2024-01-15T09:15:00Z',
    itemsCount: 2456,
    uptime: 95.2,
  },
  {
    id: '3',
    slug: 'folha-sp',
    name: 'Folha de São Paulo',
    type: 'rss',
    state: 'ACTIVE',
    health: 'HEALTHY',
    lastRun: '2024-01-15T10:00:00Z',
    itemsCount: 3890,
    uptime: 99.5,
  },
  {
    id: '4',
    slug: 'twitter-feed',
    name: 'Twitter/X Feed',
    type: 'api',
    state: 'TESTING',
    health: 'UNHEALTHY',
    lastRun: '2024-01-14T18:00:00Z',
    itemsCount: 567,
    uptime: 72.3,
  },
  {
    id: '5',
    slug: 'tse-resultados',
    name: 'TSE Resultados',
    type: 'official',
    state: 'PROPOSED',
    health: 'HEALTHY',
    lastRun: '2024-01-10T12:00:00Z',
    itemsCount: 0,
    uptime: 100,
  },
  {
    id: '6',
    slug: 'estadao-economia',
    name: 'Estadão Economia',
    type: 'scraper',
    state: 'DISABLED_TEMP',
    health: 'UNHEALTHY',
    lastRun: '2024-01-12T08:00:00Z',
    itemsCount: 1789,
    uptime: 45.0,
  },
];

const typeFilters = ['all', 'official', 'scraper', 'rss', 'api'];
const stateFilters = ['all', 'ACTIVE', 'TESTING', 'PROPOSED', 'DISABLED_TEMP', 'DISABLED_PERM'];
const healthFilters = ['all', 'HEALTHY', 'DEGRADED', 'UNHEALTHY'];

export function SpSourcesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [stateFilter, setStateFilter] = useState('all');
  const [healthFilter, setHealthFilter] = useState('all');

  const filteredSources = mockSources.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.slug.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === 'all' || s.type === typeFilter;
    const matchesState = stateFilter === 'all' || s.state === stateFilter;
    const matchesHealth = healthFilter === 'all' || s.health === healthFilter;
    return matchesSearch && matchesType && matchesState && matchesHealth;
  });

  const getHealthBadge = (health: Source['health']) => {
    const variants: Record<Source['health'], 'success' | 'warning' | 'danger'> = {
      HEALTHY: 'success',
      DEGRADED: 'warning',
      UNHEALTHY: 'danger',
    };
    return <SpBadge variant={variants[health]} dot size="sm">{health.toLowerCase()}</SpBadge>;
  };

  const getStateBadge = (state: Source['state']) => {
    const variants: Record<Source['state'], 'success' | 'warning' | 'danger' | 'info' | 'default'> = {
      ACTIVE: 'success',
      TESTING: 'info',
      PROPOSED: 'warning',
      DISABLED_TEMP: 'danger',
      DISABLED_PERM: 'default',
    };
    return <SpBadge variant={variants[state]} size="sm">{state.toLowerCase().replace('_', ' ')}</SpBadge>;
  };

  const getTypeBadge = (type: Source['type']) => {
    return <SpBadge variant="primary" size="sm">{type}</SpBadge>;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Sources</h1>
          <p className="text-slate-400">Manage data sources and ingestion</p>
        </div>
        <SpButton>
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Source
        </SpButton>
      </div>

      {/* Filters */}
      <SpCard variant="bordered" padding="sm">
        <div className="space-y-4">
          {/* Search */}
          <SpInput
            placeholder="Search sources..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />

          {/* Filter Rows */}
          <div className="flex flex-wrap gap-4">
            {/* Type Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Type:</span>
              <div className="flex gap-1">
                {typeFilters.map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setTypeFilter(filter)}
                    className={clsx(
                      'px-2 py-1 text-xs font-medium rounded transition-colors',
                      typeFilter === filter
                        ? 'bg-violet-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    )}
                  >
                    {filter}
                  </button>
                ))}
              </div>
            </div>

            {/* Health Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Health:</span>
              <div className="flex gap-1">
                {healthFilters.map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setHealthFilter(filter)}
                    className={clsx(
                      'px-2 py-1 text-xs font-medium rounded transition-colors',
                      healthFilter === filter
                        ? 'bg-violet-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    )}
                  >
                    {filter.toLowerCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* State Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">State:</span>
              <div className="flex gap-1 flex-wrap">
                {stateFilters.map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setStateFilter(filter)}
                    className={clsx(
                      'px-2 py-1 text-xs font-medium rounded transition-colors',
                      stateFilter === filter
                        ? 'bg-violet-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    )}
                  >
                    {filter.toLowerCase().replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </SpCard>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-white">{mockSources.length}</p>
          <p className="text-xs text-slate-400">Total Sources</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-emerald-400">
            {mockSources.filter((s) => s.health === 'HEALTHY').length}
          </p>
          <p className="text-xs text-slate-400">Healthy</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-yellow-400">
            {mockSources.filter((s) => s.health === 'DEGRADED').length}
          </p>
          <p className="text-xs text-slate-400">Degraded</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-red-400">
            {mockSources.filter((s) => s.health === 'UNHEALTHY').length}
          </p>
          <p className="text-xs text-slate-400">Unhealthy</p>
        </SpCard>
      </div>

      {/* Table */}
      <SpTable>
        <SpTableHead>
          <tr>
            <SpTableHeader>Source</SpTableHeader>
            <SpTableHeader>Type</SpTableHeader>
            <SpTableHeader className="text-center">State</SpTableHeader>
            <SpTableHeader className="text-center">Health</SpTableHeader>
            <SpTableHeader className="text-right">Items</SpTableHeader>
            <SpTableHeader className="text-right">Uptime</SpTableHeader>
            <SpTableHeader className="text-right">Last Run</SpTableHeader>
            <SpTableHeader className="w-32">&nbsp;</SpTableHeader>
          </tr>
        </SpTableHead>
        <SpTableBody>
          {filteredSources.map((source) => (
            <SpTableRow key={source.id}>
              <SpTableCell>
                <div>
                  <Link
                    to={`/spovest/admin/sources/${source.id}`}
                    className="font-medium text-white hover:text-violet-400 transition-colors"
                  >
                    {source.name}
                  </Link>
                  <p className="text-xs text-slate-500">{source.slug}</p>
                </div>
              </SpTableCell>
              <SpTableCell>{getTypeBadge(source.type)}</SpTableCell>
              <SpTableCell className="text-center">{getStateBadge(source.state)}</SpTableCell>
              <SpTableCell className="text-center">{getHealthBadge(source.health)}</SpTableCell>
              <SpTableCell className="text-right font-medium text-white">
                {source.itemsCount.toLocaleString()}
              </SpTableCell>
              <SpTableCell className="text-right">
                <span className={clsx(
                  source.uptime >= 99 ? 'text-emerald-400' :
                  source.uptime >= 90 ? 'text-yellow-400' : 'text-red-400'
                )}>
                  {source.uptime.toFixed(1)}%
                </span>
              </SpTableCell>
              <SpTableCell className="text-right text-slate-400">
                {new Date(source.lastRun).toLocaleString()}
              </SpTableCell>
              <SpTableCell>
                <div className="flex items-center justify-end gap-1">
                  <SpButton variant="ghost" size="sm" title="Run ingestion">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </SpButton>
                  <SpButton variant="ghost" size="sm" title="Health check">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </SpButton>
                  <Link to={`/spovest/admin/sources/${source.id}`}>
                    <SpButton variant="ghost" size="sm" title="View details">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </SpButton>
                  </Link>
                </div>
              </SpTableCell>
            </SpTableRow>
          ))}
        </SpTableBody>
      </SpTable>

      {filteredSources.length === 0 && (
        <SpCard variant="bordered" className="text-center py-12">
          <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9" />
          </svg>
          <h3 className="text-lg font-semibold text-white mb-2">No sources found</h3>
          <p className="text-slate-400">Try adjusting your filters</p>
        </SpCard>
      )}

      {/* Summary Footer */}
      <div className="text-sm text-slate-400 text-center">
        Showing {filteredSources.length} of {mockSources.length} sources |
        Healthy: {mockSources.filter(s => s.health === 'HEALTHY').length} |
        Active: {mockSources.filter(s => s.state === 'ACTIVE').length}
      </div>
    </div>
  );
}
