import { useParams, Link } from 'react-router-dom';
import { clsx } from 'clsx';
import { SpCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpBadge } from '../../components/ui/Badge';

interface PerformanceMetric {
  date: string;
  analysesCount: number;
  avgLatency: number;
  successRate: number;
}

const mockAgent = {
  id: '1',
  name: 'Debunker-Primary',
  role: 'debunker' as const,
  layer: 'debunk' as const,
  status: 'active' as const,
  model: 'gpt-4-turbo',
  version: '4.0.0',
  description: 'Primary debunker agent for fact-checking claims. Specializes in political and economic content verification.',
  systemPrompt: 'You are a fact-checking agent specializing in Brazilian political and economic news...',
  temperature: 0.3,
  maxTokens: 4096,
  analysesCount: 5621,
  avgLatency: 2100,
  successRate: 97.5,
  lastActive: '2024-01-15T10:25:00Z',
  createdAt: '2023-09-01T00:00:00Z',
};

const mockMetrics: PerformanceMetric[] = [
  { date: '2024-01-15', analysesCount: 245, avgLatency: 2100, successRate: 98.2 },
  { date: '2024-01-14', analysesCount: 312, avgLatency: 1950, successRate: 97.8 },
  { date: '2024-01-13', analysesCount: 189, avgLatency: 2200, successRate: 96.5 },
  { date: '2024-01-12', analysesCount: 278, avgLatency: 2050, successRate: 97.9 },
  { date: '2024-01-11', analysesCount: 301, avgLatency: 1980, successRate: 98.1 },
];

const mockRecentAnalyses = [
  { id: '1', claim: 'Governo anuncia novo programa social', verdict: 'true', confidence: 0.95, timestamp: '2024-01-15T10:20:00Z' },
  { id: '2', claim: 'Inflacao vai subir 10% em marco', verdict: 'false', confidence: 0.98, timestamp: '2024-01-15T10:15:00Z' },
  { id: '3', claim: 'Nova lei de transito em vigor', verdict: 'misleading', confidence: 0.87, timestamp: '2024-01-15T10:10:00Z' },
  { id: '4', claim: 'Banco Central muda taxa Selic', verdict: 'true', confidence: 0.92, timestamp: '2024-01-15T10:05:00Z' },
];

export function SpAgentDetailPage() {
  const { agentId } = useParams();

  const getStatusBadge = (status: typeof mockAgent.status) => {
    const variants: Record<string, 'success' | 'warning' | 'default'> = {
      active: 'success',
      paused: 'warning',
      deprecated: 'default',
    };
    return <SpBadge variant={variants[status]} dot>{status.toUpperCase()}</SpBadge>;
  };

  const getLayerBadge = (layer: typeof mockAgent.layer) => {
    const colors: Record<string, string> = {
      interpretation: 'bg-cyan-400/10 text-cyan-400',
      classification: 'bg-violet-400/10 text-violet-400',
      debunk: 'bg-orange-400/10 text-orange-400',
    };
    return (
      <span className={clsx('px-2 py-1 text-xs font-medium rounded-full', colors[layer])}>
        {layer}
      </span>
    );
  };

  const getRoleBadge = (role: typeof mockAgent.role) => {
    return <SpBadge variant="primary" size="sm">{role.replace('_', ' ')}</SpBadge>;
  };

  const getVerdictBadge = (verdict: string) => {
    const config: Record<string, { variant: 'success' | 'danger' | 'warning'; label: string }> = {
      true: { variant: 'success', label: 'TRUE' },
      false: { variant: 'danger', label: 'FALSE' },
      misleading: { variant: 'warning', label: 'MISLEADING' },
    };
    return <SpBadge variant={config[verdict].variant} size="sm">{config[verdict].label}</SpBadge>;
  };

  const getLatencyColor = (latency: number) => {
    if (latency < 1500) return 'text-emerald-400';
    if (latency < 2500) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Link to="/spovest/admin/agents" className="hover:text-white transition-colors">Agents</Link>
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span className="text-white">{mockAgent.name}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-white">{mockAgent.name}</h1>
            {getStatusBadge(mockAgent.status)}
          </div>
          <div className="flex items-center gap-2">
            {getLayerBadge(mockAgent.layer)}
            {getRoleBadge(mockAgent.role)}
            <span className="text-slate-400 text-sm">v{mockAgent.version}</span>
          </div>
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Test
          </SpButton>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-white">{mockAgent.analysesCount.toLocaleString()}</p>
          <p className="text-xs text-slate-400">Total Analyses</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className={clsx('text-2xl font-bold', getLatencyColor(mockAgent.avgLatency))}>
            {mockAgent.avgLatency}ms
          </p>
          <p className="text-xs text-slate-400">Avg Latency</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-emerald-400">{mockAgent.successRate}%</p>
          <p className="text-xs text-slate-400">Success Rate</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-lg font-bold text-violet-400">{mockAgent.model}</p>
          <p className="text-xs text-slate-400">Model</p>
        </SpCard>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Performance */}
        <div className="lg:col-span-2 space-y-6">
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Performance (Last 5 Days)</h3>
            <div className="space-y-3">
              {mockMetrics.map((metric) => (
                <div key={metric.date} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <span className="text-sm text-slate-300">{new Date(metric.date).toLocaleDateString()}</span>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-sm font-medium text-white">{metric.analysesCount}</p>
                      <p className="text-xs text-slate-500">analyses</p>
                    </div>
                    <div className="text-right">
                      <p className={clsx('text-sm font-medium', getLatencyColor(metric.avgLatency))}>
                        {metric.avgLatency}ms
                      </p>
                      <p className="text-xs text-slate-500">latency</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-emerald-400">{metric.successRate}%</p>
                      <p className="text-xs text-slate-500">success</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </SpCard>

          {/* Recent Analyses */}
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Recent Analyses</h3>
            <div className="space-y-3">
              {mockRecentAnalyses.map((analysis) => (
                <div key={analysis.id} className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <p className="text-sm text-white">{analysis.claim}</p>
                    {getVerdictBadge(analysis.verdict)}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <span>Confidence: {Math.round(analysis.confidence * 100)}%</span>
                    <span>{new Date(analysis.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
            <SpButton variant="outline" size="sm" className="w-full mt-4">
              View All Analyses
            </SpButton>
          </SpCard>
        </div>

        {/* Configuration */}
        <div className="space-y-6">
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Description</h3>
            <p className="text-sm text-slate-300">{mockAgent.description}</p>
          </SpCard>

          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-slate-500">Model</label>
                <p className="text-sm text-slate-300 font-mono bg-slate-800 px-2 py-1 rounded mt-1">
                  {mockAgent.model}
                </p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Temperature</label>
                <p className="text-sm text-slate-300">{mockAgent.temperature}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Max Tokens</label>
                <p className="text-sm text-slate-300">{mockAgent.maxTokens.toLocaleString()}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Version</label>
                <p className="text-sm text-slate-300">{mockAgent.version}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Created</label>
                <p className="text-sm text-slate-300">
                  {new Date(mockAgent.createdAt).toLocaleDateString()}
                </p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Last Active</label>
                <p className="text-sm text-slate-300">
                  {new Date(mockAgent.lastActive).toLocaleString()}
                </p>
              </div>
            </div>
          </SpCard>

          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm">View Logs</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                <span className="text-sm">View Prompt</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm">View History</span>
              </button>
            </div>
          </SpCard>
        </div>
      </div>
    </div>
  );
}
