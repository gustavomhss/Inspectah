import { useParams, Link } from 'react-router-dom';
import { clsx } from 'clsx';
import { SpCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpBadge } from '../../components/ui/Badge';
import {
  SpTable,
  SpTableHead,
  SpTableBody,
  SpTableRow,
  SpTableHeader,
  SpTableCell,
} from '../../components/ui/Table';

interface IngestionHistory {
  id: string;
  timestamp: string;
  status: 'success' | 'partial' | 'failed';
  itemsProcessed: number;
  itemsFailed: number;
  duration: number;
}

const mockSource = {
  id: '1',
  name: 'G1 Brasil',
  type: 'rss' as const,
  url: 'https://g1.globo.com/rss/g1/',
  state: 'active' as const,
  healthScore: 98,
  lastIngestion: '2024-01-15T10:30:00Z',
  totalItems: 15420,
  createdAt: '2023-06-15T00:00:00Z',
  schedule: '*/15 * * * *',
  retryPolicy: { maxRetries: 3, backoffMs: 5000 },
  tags: ['news', 'brazil', 'mainstream'],
};

const mockHistory: IngestionHistory[] = [
  { id: '1', timestamp: '2024-01-15T10:30:00Z', status: 'success', itemsProcessed: 45, itemsFailed: 0, duration: 12 },
  { id: '2', timestamp: '2024-01-15T10:15:00Z', status: 'success', itemsProcessed: 38, itemsFailed: 0, duration: 10 },
  { id: '3', timestamp: '2024-01-15T10:00:00Z', status: 'partial', itemsProcessed: 42, itemsFailed: 3, duration: 15 },
  { id: '4', timestamp: '2024-01-15T09:45:00Z', status: 'success', itemsProcessed: 51, itemsFailed: 0, duration: 14 },
  { id: '5', timestamp: '2024-01-15T09:30:00Z', status: 'failed', itemsProcessed: 0, itemsFailed: 50, duration: 5 },
  { id: '6', timestamp: '2024-01-15T09:15:00Z', status: 'success', itemsProcessed: 47, itemsFailed: 0, duration: 11 },
];

const mockMetrics = {
  avgLatency: 12.5,
  successRate: 94.2,
  itemsToday: 423,
  itemsWeek: 2891,
};

export function SpSourceDetailPage() {
  const { sourceId } = useParams();

  const getTypeBadge = (type: typeof mockSource.type) => {
    const colors: Record<string, string> = {
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

  const getStateBadge = (state: typeof mockSource.state) => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      active: 'success',
      paused: 'warning',
      error: 'danger',
      disabled: 'default',
    };
    return <SpBadge variant={variants[state]} dot>{state.toUpperCase()}</SpBadge>;
  };

  const getStatusBadge = (status: IngestionHistory['status']) => {
    const config = {
      success: { variant: 'success' as const, label: 'SUCCESS' },
      partial: { variant: 'warning' as const, label: 'PARTIAL' },
      failed: { variant: 'danger' as const, label: 'FAILED' },
    };
    return <SpBadge variant={config[status].variant} size="sm">{config[status].label}</SpBadge>;
  };

  const getHealthColor = (score: number) => {
    if (score >= 90) return 'text-emerald-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Link to="/spovest/admin/sources" className="hover:text-white transition-colors">Sources</Link>
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span className="text-white">{mockSource.name}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-white">{mockSource.name}</h1>
            {getTypeBadge(mockSource.type)}
            {getStateBadge(mockSource.state)}
          </div>
          <p className="text-slate-400 font-mono text-sm">{mockSource.url}</p>
        </div>
        <div className="flex gap-2">
          <SpButton variant="outline">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Pause
          </SpButton>
          <SpButton variant="outline">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            Edit
          </SpButton>
          <SpButton>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Run Now
          </SpButton>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className={clsx('text-3xl font-bold', getHealthColor(mockSource.healthScore))}>
            {mockSource.healthScore}%
          </p>
          <p className="text-xs text-slate-400">Health Score</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-white">{mockMetrics.avgLatency}s</p>
          <p className="text-xs text-slate-400">Avg Latency</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-emerald-400">{mockMetrics.successRate}%</p>
          <p className="text-xs text-slate-400">Success Rate</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-violet-400">{mockMetrics.itemsToday}</p>
          <p className="text-xs text-slate-400">Items Today</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-cyan-400">{mockSource.totalItems.toLocaleString()}</p>
          <p className="text-xs text-slate-400">Total Items</p>
        </SpCard>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Ingestion History */}
        <div className="lg:col-span-2">
          <SpCard variant="bordered" padding="none">
            <div className="p-4 border-b border-slate-700/50">
              <h3 className="text-lg font-bold text-white">Ingestion History</h3>
            </div>
            <SpTable>
              <SpTableHead>
                <tr>
                  <SpTableHeader>Timestamp</SpTableHeader>
                  <SpTableHeader className="text-center">Status</SpTableHeader>
                  <SpTableHeader className="text-right">Processed</SpTableHeader>
                  <SpTableHeader className="text-right">Failed</SpTableHeader>
                  <SpTableHeader className="text-right">Duration</SpTableHeader>
                </tr>
              </SpTableHead>
              <SpTableBody>
                {mockHistory.map((run) => (
                  <SpTableRow key={run.id}>
                    <SpTableCell className="text-slate-300 text-sm">
                      {new Date(run.timestamp).toLocaleString()}
                    </SpTableCell>
                    <SpTableCell className="text-center">{getStatusBadge(run.status)}</SpTableCell>
                    <SpTableCell className="text-right font-medium text-white">
                      {run.itemsProcessed}
                    </SpTableCell>
                    <SpTableCell className="text-right">
                      <span className={run.itemsFailed > 0 ? 'text-red-400' : 'text-slate-500'}>
                        {run.itemsFailed}
                      </span>
                    </SpTableCell>
                    <SpTableCell className="text-right text-slate-300">
                      {run.duration}s
                    </SpTableCell>
                  </SpTableRow>
                ))}
              </SpTableBody>
            </SpTable>
          </SpCard>
        </div>

        {/* Configuration */}
        <div className="space-y-6">
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-slate-500">Schedule (Cron)</label>
                <p className="text-sm text-slate-300 font-mono bg-slate-800 px-2 py-1 rounded mt-1">
                  {mockSource.schedule}
                </p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Max Retries</label>
                <p className="text-sm text-slate-300">{mockSource.retryPolicy.maxRetries}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Backoff</label>
                <p className="text-sm text-slate-300">{mockSource.retryPolicy.backoffMs}ms</p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Created</label>
                <p className="text-sm text-slate-300">
                  {new Date(mockSource.createdAt).toLocaleDateString()}
                </p>
              </div>
            </div>
          </SpCard>

          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {mockSource.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 text-sm bg-slate-800 text-slate-300 rounded-full"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </SpCard>

          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className="text-sm">Force Refresh</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm">View Logs</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="text-sm">View Errors</span>
              </button>
            </div>
          </SpCard>
        </div>
      </div>
    </div>
  );
}
