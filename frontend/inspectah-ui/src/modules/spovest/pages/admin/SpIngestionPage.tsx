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

interface IngestionRun {
  id: string;
  sourceId: string;
  sourceName: string;
  sourceType: 'rss' | 'api' | 'scraper' | 'social';
  status: 'running' | 'completed' | 'failed' | 'queued';
  startedAt: string;
  completedAt: string | null;
  itemsProcessed: number;
  itemsFailed: number;
  duration: number | null;
}

const mockRuns: IngestionRun[] = [
  {
    id: '1',
    sourceId: 's1',
    sourceName: 'G1 Brasil',
    sourceType: 'rss',
    status: 'running',
    startedAt: '2024-01-15T10:30:00Z',
    completedAt: null,
    itemsProcessed: 45,
    itemsFailed: 0,
    duration: null,
  },
  {
    id: '2',
    sourceId: 's2',
    sourceName: 'Folha de SP',
    sourceType: 'scraper',
    status: 'completed',
    startedAt: '2024-01-15T10:25:00Z',
    completedAt: '2024-01-15T10:28:00Z',
    itemsProcessed: 120,
    itemsFailed: 2,
    duration: 180,
  },
  {
    id: '3',
    sourceId: 's3',
    sourceName: 'TSE API',
    sourceType: 'api',
    status: 'completed',
    startedAt: '2024-01-15T10:20:00Z',
    completedAt: '2024-01-15T10:22:00Z',
    itemsProcessed: 500,
    itemsFailed: 0,
    duration: 120,
  },
  {
    id: '4',
    sourceId: 's4',
    sourceName: 'Twitter Politics',
    sourceType: 'social',
    status: 'failed',
    startedAt: '2024-01-15T10:15:00Z',
    completedAt: '2024-01-15T10:16:00Z',
    itemsProcessed: 10,
    itemsFailed: 10,
    duration: 60,
  },
  {
    id: '5',
    sourceId: 's5',
    sourceName: 'UOL Noticias',
    sourceType: 'rss',
    status: 'queued',
    startedAt: '2024-01-15T10:35:00Z',
    completedAt: null,
    itemsProcessed: 0,
    itemsFailed: 0,
    duration: null,
  },
  {
    id: '6',
    sourceId: 's6',
    sourceName: 'Estadao',
    sourceType: 'scraper',
    status: 'completed',
    startedAt: '2024-01-15T10:10:00Z',
    completedAt: '2024-01-15T10:14:00Z',
    itemsProcessed: 85,
    itemsFailed: 1,
    duration: 240,
  },
];

const statusFilters = ['all', 'running', 'completed', 'failed', 'queued'];
const typeFilters = ['all', 'rss', 'api', 'scraper', 'social'];

export function SpIngestionPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  const filteredRuns = mockRuns.filter((run) => {
    const matchesSearch = run.sourceName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || run.status === statusFilter;
    const matchesType = typeFilter === 'all' || run.sourceType === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusBadge = (status: IngestionRun['status']) => {
    const variants: Record<IngestionRun['status'], 'success' | 'warning' | 'danger' | 'default'> = {
      running: 'warning',
      completed: 'success',
      failed: 'danger',
      queued: 'default',
    };
    return <SpBadge variant={variants[status]} dot size="sm">{status}</SpBadge>;
  };

  const getTypeBadge = (type: IngestionRun['sourceType']) => {
    const colors: Record<IngestionRun['sourceType'], string> = {
      rss: 'bg-orange-400/10 text-orange-400',
      api: 'bg-cyan-400/10 text-cyan-400',
      scraper: 'bg-violet-400/10 text-violet-400',
      social: 'bg-pink-400/10 text-pink-400',
    };
    return (
      <span className={clsx('px-2 py-1 text-xs font-medium rounded-full uppercase', colors[type])}>
        {type}
      </span>
    );
  };

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return '-';
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const runningCount = mockRuns.filter((r) => r.status === 'running').length;
  const completedToday = mockRuns.filter((r) => r.status === 'completed').length;
  const failedToday = mockRuns.filter((r) => r.status === 'failed').length;
  const totalItems = mockRuns.reduce((sum, r) => sum + r.itemsProcessed, 0);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Ingestion Monitor</h1>
          <p className="text-slate-400">Track and manage data ingestion runs</p>
        </div>
        <div className="flex gap-2">
          <SpButton variant="outline">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </SpButton>
          <SpButton>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Run All
          </SpButton>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <SpCard variant="bordered" padding="sm" className="text-center">
          <div className="flex items-center justify-center gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
            <p className="text-2xl font-bold text-yellow-400">{runningCount}</p>
          </div>
          <p className="text-xs text-slate-400">Running Now</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-emerald-400">{completedToday}</p>
          <p className="text-xs text-slate-400">Completed Today</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-red-400">{failedToday}</p>
          <p className="text-xs text-slate-400">Failed Today</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-violet-400">{totalItems.toLocaleString()}</p>
          <p className="text-xs text-slate-400">Items Processed</p>
        </SpCard>
      </div>

      {/* Filters */}
      <SpCard variant="bordered" padding="sm">
        <div className="space-y-4">
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

          <div className="flex flex-wrap gap-4">
            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Status:</span>
              <div className="flex gap-1">
                {statusFilters.map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setStatusFilter(filter)}
                    className={clsx(
                      'px-2 py-1 text-xs font-medium rounded transition-colors',
                      statusFilter === filter
                        ? 'bg-violet-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    )}
                  >
                    {filter}
                  </button>
                ))}
              </div>
            </div>

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
          </div>
        </div>
      </SpCard>

      {/* Table */}
      <SpTable>
        <SpTableHead>
          <tr>
            <SpTableHeader>Source</SpTableHeader>
            <SpTableHeader>Type</SpTableHeader>
            <SpTableHeader className="text-center">Status</SpTableHeader>
            <SpTableHeader>Started</SpTableHeader>
            <SpTableHeader className="text-right">Items</SpTableHeader>
            <SpTableHeader className="text-right">Failed</SpTableHeader>
            <SpTableHeader className="text-right">Duration</SpTableHeader>
            <SpTableHeader className="w-20">&nbsp;</SpTableHeader>
          </tr>
        </SpTableHead>
        <SpTableBody>
          {filteredRuns.map((run) => (
            <SpTableRow key={run.id}>
              <SpTableCell>
                <Link
                  to={`/spovest/admin/sources/${run.sourceId}`}
                  className="font-medium text-white hover:text-violet-400 transition-colors"
                >
                  {run.sourceName}
                </Link>
              </SpTableCell>
              <SpTableCell>{getTypeBadge(run.sourceType)}</SpTableCell>
              <SpTableCell className="text-center">{getStatusBadge(run.status)}</SpTableCell>
              <SpTableCell className="text-slate-300 text-sm">
                {new Date(run.startedAt).toLocaleTimeString()}
              </SpTableCell>
              <SpTableCell className="text-right font-medium text-white">
                {run.itemsProcessed.toLocaleString()}
              </SpTableCell>
              <SpTableCell className="text-right">
                <span className={run.itemsFailed > 0 ? 'text-red-400' : 'text-slate-500'}>
                  {run.itemsFailed}
                </span>
              </SpTableCell>
              <SpTableCell className="text-right text-slate-300">
                {formatDuration(run.duration)}
              </SpTableCell>
              <SpTableCell>
                <div className="flex gap-1">
                  {run.status === 'running' && (
                    <SpButton variant="ghost" size="sm">
                      <svg className="w-4 h-4 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </SpButton>
                  )}
                  {run.status === 'failed' && (
                    <SpButton variant="ghost" size="sm">
                      <svg className="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </SpButton>
                  )}
                  <Link to={`/spovest/admin/ingestion/${run.id}`}>
                    <SpButton variant="ghost" size="sm">
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

      {filteredRuns.length === 0 && (
        <SpCard variant="bordered" className="text-center py-12">
          <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
          </svg>
          <h3 className="text-lg font-semibold text-white mb-2">No runs found</h3>
          <p className="text-slate-400">Try adjusting your filters</p>
        </SpCard>
      )}
    </div>
  );
}
