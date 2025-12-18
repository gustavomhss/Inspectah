import { Link } from 'react-router-dom';
import { SpCard, SpStatCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpBadge } from '../../components/ui/Badge';

// Mock data - em produção viria da API
const mockHealthData = {
  sources: {
    healthy: 45,
    degraded: 3,
    unhealthy: 2,
    total: 50,
  },
  cases: {
    stable: 120,
    attention: 8,
    critical: 2,
    total: 130,
  },
  agents: {
    active: 12,
    paused: 2,
    total: 14,
  },
  ingestion: {
    running: 3,
    completed: 47,
    failed: 0,
  },
};

const recentAlerts = [
  { id: '1', type: 'warning', message: 'Source "Reuters BR" showing degraded health', time: '5 min ago' },
  { id: '2', type: 'info', message: 'Agent "Debunker-v3" completed 50 analyses', time: '12 min ago' },
  { id: '3', type: 'success', message: 'Case "Eleições 2024" moved to stable', time: '1 hour ago' },
  { id: '4', type: 'error', message: 'Ingestion failed for "Twitter Feed"', time: '2 hours ago' },
];

const quickLinks = [
  { label: 'Truth Console', href: '/spovest/admin/truth', icon: 'database' },
  { label: 'Cases', href: '/spovest/admin/cases', icon: 'folder' },
  { label: 'Sources', href: '/spovest/admin/sources', icon: 'globe' },
  { label: 'Agents', href: '/spovest/admin/agents', icon: 'cpu' },
  { label: 'Ingestion', href: '/spovest/admin/ingestion', icon: 'download' },
  { label: 'Ops Cockpit', href: '/spovest/admin/ops', icon: 'activity' },
];

const iconMap: Record<string, React.ReactNode> = {
  database: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
    </svg>
  ),
  folder: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
    </svg>
  ),
  globe: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
    </svg>
  ),
  cpu: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
    </svg>
  ),
  download: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  ),
  activity: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
};

export function SpAdminOverviewPage() {
  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Admin Overview</h1>
          <p className="text-slate-400">System health and quick actions</p>
        </div>
        <SpButton variant="outline" size="sm">
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </SpButton>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <SpStatCard
          label="Sources Health"
          value={`${mockHealthData.sources.healthy}/${mockHealthData.sources.total}`}
          prefix=""
          changePercent={((mockHealthData.sources.healthy / mockHealthData.sources.total) * 100) - 100}
          icon={
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9" />
            </svg>
          }
        />
        <SpStatCard
          label="Cases Stable"
          value={`${mockHealthData.cases.stable}/${mockHealthData.cases.total}`}
          prefix=""
          icon={
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <SpStatCard
          label="Active Agents"
          value={`${mockHealthData.agents.active}/${mockHealthData.agents.total}`}
          prefix=""
          icon={
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          }
        />
        <SpStatCard
          label="Ingestion Today"
          value={`${mockHealthData.ingestion.completed}`}
          prefix=""
          icon={
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          }
        />
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Health Overview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Sources Health */}
          <SpCard variant="bordered">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Sources Health</h3>
              <Link to="/spovest/admin/sources" className="text-sm text-violet-400 hover:text-violet-300">
                View All
              </Link>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                <p className="text-3xl font-bold text-emerald-400">{mockHealthData.sources.healthy}</p>
                <p className="text-sm text-slate-400">Healthy</p>
              </div>
              <div className="text-center p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                <p className="text-3xl font-bold text-yellow-400">{mockHealthData.sources.degraded}</p>
                <p className="text-sm text-slate-400">Degraded</p>
              </div>
              <div className="text-center p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                <p className="text-3xl font-bold text-red-400">{mockHealthData.sources.unhealthy}</p>
                <p className="text-sm text-slate-400">Unhealthy</p>
              </div>
            </div>
          </SpCard>

          {/* Cases Status */}
          <SpCard variant="bordered">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Cases Status</h3>
              <Link to="/spovest/admin/cases" className="text-sm text-violet-400 hover:text-violet-300">
                View All
              </Link>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                <p className="text-3xl font-bold text-emerald-400">{mockHealthData.cases.stable}</p>
                <p className="text-sm text-slate-400">Stable</p>
              </div>
              <div className="text-center p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                <p className="text-3xl font-bold text-yellow-400">{mockHealthData.cases.attention}</p>
                <p className="text-sm text-slate-400">Attention</p>
              </div>
              <div className="text-center p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                <p className="text-3xl font-bold text-red-400">{mockHealthData.cases.critical}</p>
                <p className="text-sm text-slate-400">Critical</p>
              </div>
            </div>
          </SpCard>

          {/* Quick Links */}
          <SpCard variant="gradient">
            <h3 className="text-lg font-bold text-white mb-4">Quick Access</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {quickLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="flex items-center gap-3 p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors group"
                >
                  <div className="text-violet-400 group-hover:text-violet-300">
                    {iconMap[link.icon]}
                  </div>
                  <span className="text-sm font-medium text-white">{link.label}</span>
                </Link>
              ))}
            </div>
          </SpCard>
        </div>

        {/* Sidebar - Recent Alerts */}
        <div className="space-y-6">
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Recent Alerts</h3>
            <div className="space-y-3">
              {recentAlerts.map((alert) => (
                <div key={alert.id} className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex-shrink-0 mt-0.5">
                    {alert.type === 'success' && (
                      <div className="w-2 h-2 rounded-full bg-emerald-400" />
                    )}
                    {alert.type === 'warning' && (
                      <div className="w-2 h-2 rounded-full bg-yellow-400" />
                    )}
                    {alert.type === 'error' && (
                      <div className="w-2 h-2 rounded-full bg-red-400" />
                    )}
                    {alert.type === 'info' && (
                      <div className="w-2 h-2 rounded-full bg-cyan-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-300">{alert.message}</p>
                    <p className="text-xs text-slate-500 mt-1">{alert.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </SpCard>

          {/* System Status */}
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">System Status</h3>
            <div className="space-y-3">
              {[
                { name: 'API Server', status: 'operational' },
                { name: 'Database', status: 'operational' },
                { name: 'Redis Cache', status: 'operational' },
                { name: 'LLM Gateway', status: 'degraded' },
                { name: 'Ingestion Workers', status: 'operational' },
              ].map((service) => (
                <div key={service.name} className="flex items-center justify-between">
                  <span className="text-sm text-slate-300">{service.name}</span>
                  <SpBadge
                    variant={service.status === 'operational' ? 'success' : 'warning'}
                    size="sm"
                    dot
                  >
                    {service.status}
                  </SpBadge>
                </div>
              ))}
            </div>
          </SpCard>
        </div>
      </div>
    </div>
  );
}
