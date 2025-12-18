import { useState } from 'react';
import { clsx } from 'clsx';
import { SpCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpBadge } from '../../components/ui/Badge';

interface SLO {
  id: string;
  name: string;
  target: number;
  current: number;
  status: 'healthy' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
}

interface Incident {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'active' | 'investigating' | 'resolved';
  startedAt: string;
  resolvedAt: string | null;
  affectedServices: string[];
}

interface SystemMetric {
  name: string;
  value: number;
  unit: string;
  status: 'healthy' | 'warning' | 'critical';
}

const mockSLOs: SLO[] = [
  { id: '1', name: 'API Availability', target: 99.9, current: 99.95, status: 'healthy', trend: 'stable' },
  { id: '2', name: 'Ingestion Latency p99', target: 5000, current: 3200, status: 'healthy', trend: 'down' },
  { id: '3', name: 'Debunk Accuracy', target: 95, current: 97.2, status: 'healthy', trend: 'up' },
  { id: '4', name: 'Error Rate', target: 0.1, current: 0.08, status: 'healthy', trend: 'down' },
  { id: '5', name: 'LLM Response Time', target: 3000, current: 2850, status: 'warning', trend: 'up' },
];

const mockIncidents: Incident[] = [
  {
    id: '1',
    title: 'High latency on ingestion pipeline',
    severity: 'medium',
    status: 'investigating',
    startedAt: '2024-01-15T09:30:00Z',
    resolvedAt: null,
    affectedServices: ['Ingestion', 'RSS Scraper'],
  },
  {
    id: '2',
    title: 'Database connection pool exhaustion',
    severity: 'high',
    status: 'resolved',
    startedAt: '2024-01-14T22:00:00Z',
    resolvedAt: '2024-01-14T23:30:00Z',
    affectedServices: ['API', 'Truth DB'],
  },
  {
    id: '3',
    title: 'LLM rate limit exceeded',
    severity: 'low',
    status: 'resolved',
    startedAt: '2024-01-14T15:00:00Z',
    resolvedAt: '2024-01-14T15:45:00Z',
    affectedServices: ['Debunker', 'Classifier'],
  },
];

const mockMetrics: SystemMetric[] = [
  { name: 'CPU Usage', value: 45, unit: '%', status: 'healthy' },
  { name: 'Memory Usage', value: 72, unit: '%', status: 'warning' },
  { name: 'Disk Usage', value: 38, unit: '%', status: 'healthy' },
  { name: 'Active Connections', value: 156, unit: '', status: 'healthy' },
  { name: 'Queue Depth', value: 23, unit: 'msgs', status: 'healthy' },
  { name: 'Cache Hit Rate', value: 94, unit: '%', status: 'healthy' },
];

export function SpOpsPage() {
  const [selectedTab, setSelectedTab] = useState<'overview' | 'incidents' | 'slos'>('overview');

  const getSeverityBadge = (severity: Incident['severity']) => {
    const variants: Record<Incident['severity'], 'danger' | 'warning' | 'primary' | 'default'> = {
      critical: 'danger',
      high: 'warning',
      medium: 'primary',
      low: 'default',
    };
    return <SpBadge variant={variants[severity]} size="sm">{severity.toUpperCase()}</SpBadge>;
  };

  const getIncidentStatusBadge = (status: Incident['status']) => {
    const config: Record<Incident['status'], { variant: 'danger' | 'warning' | 'success'; label: string }> = {
      active: { variant: 'danger', label: 'ACTIVE' },
      investigating: { variant: 'warning', label: 'INVESTIGATING' },
      resolved: { variant: 'success', label: 'RESOLVED' },
    };
    return <SpBadge variant={config[status].variant} dot size="sm">{config[status].label}</SpBadge>;
  };

  const getStatusColor = (status: 'healthy' | 'warning' | 'critical') => {
    switch (status) {
      case 'healthy': return 'text-emerald-400';
      case 'warning': return 'text-yellow-400';
      case 'critical': return 'text-red-400';
    }
  };

  const getMetricBarColor = (status: 'healthy' | 'warning' | 'critical') => {
    switch (status) {
      case 'healthy': return 'bg-emerald-500';
      case 'warning': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
    }
  };

  const activeIncidents = mockIncidents.filter((i) => i.status !== 'resolved').length;
  const healthySLOs = mockSLOs.filter((s) => s.status === 'healthy').length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Operations Cockpit</h1>
          <p className="text-slate-400">Monitor system health and incidents</p>
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Report Incident
          </SpButton>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <SpCard variant="bordered" padding="sm">
          <div className="flex items-center gap-3">
            <div className={clsx('w-3 h-3 rounded-full', activeIncidents > 0 ? 'bg-yellow-400 animate-pulse' : 'bg-emerald-400')}>
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{activeIncidents}</p>
              <p className="text-xs text-slate-400">Active Incidents</p>
            </div>
          </div>
        </SpCard>
        <SpCard variant="bordered" padding="sm">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
            <div>
              <p className="text-2xl font-bold text-emerald-400">{healthySLOs}/{mockSLOs.length}</p>
              <p className="text-xs text-slate-400">SLOs Met</p>
            </div>
          </div>
        </SpCard>
        <SpCard variant="bordered" padding="sm">
          <div>
            <p className="text-2xl font-bold text-violet-400">99.95%</p>
            <p className="text-xs text-slate-400">Uptime (30d)</p>
          </div>
        </SpCard>
        <SpCard variant="bordered" padding="sm">
          <div>
            <p className="text-2xl font-bold text-cyan-400">2.1s</p>
            <p className="text-xs text-slate-400">Avg Response</p>
          </div>
        </SpCard>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-slate-800 rounded-lg w-fit">
        {(['overview', 'incidents', 'slos'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab)}
            className={clsx(
              'px-4 py-2 text-sm font-medium rounded-md transition-colors capitalize',
              selectedTab === tab
                ? 'bg-violet-600 text-white'
                : 'text-slate-400 hover:text-white'
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      {selectedTab === 'overview' && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* System Metrics */}
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">System Metrics</h3>
            <div className="space-y-4">
              {mockMetrics.map((metric) => (
                <div key={metric.name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-slate-300">{metric.name}</span>
                    <span className={clsx('text-sm font-medium', getStatusColor(metric.status))}>
                      {metric.value}{metric.unit}
                    </span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={clsx('h-full rounded-full transition-all', getMetricBarColor(metric.status))}
                      style={{ width: `${Math.min(metric.value, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </SpCard>

          {/* Recent Incidents */}
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Recent Incidents</h3>
            <div className="space-y-3">
              {mockIncidents.slice(0, 3).map((incident) => (
                <div key={incident.id} className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="text-white font-medium text-sm">{incident.title}</span>
                    {getIncidentStatusBadge(incident.status)}
                  </div>
                  <div className="flex items-center gap-2">
                    {getSeverityBadge(incident.severity)}
                    <span className="text-xs text-slate-500">
                      {new Date(incident.startedAt).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </SpCard>

          {/* SLO Summary */}
          <SpCard variant="bordered" className="lg:col-span-2">
            <h3 className="text-lg font-bold text-white mb-4">SLO Status</h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
              {mockSLOs.map((slo) => (
                <div key={slo.id} className="p-3 bg-slate-800/50 rounded-lg text-center">
                  <p className="text-xs text-slate-400 mb-1">{slo.name}</p>
                  <p className={clsx('text-2xl font-bold', getStatusColor(slo.status))}>
                    {slo.current}{slo.name.includes('Latency') ? 'ms' : slo.name.includes('Rate') ? '%' : '%'}
                  </p>
                  <p className="text-xs text-slate-500">
                    Target: {slo.target}{slo.name.includes('Latency') ? 'ms' : '%'}
                  </p>
                </div>
              ))}
            </div>
          </SpCard>
        </div>
      )}

      {selectedTab === 'incidents' && (
        <SpCard variant="bordered">
          <div className="space-y-4">
            {mockIncidents.map((incident) => (
              <div key={incident.id} className="p-4 bg-slate-800/50 rounded-lg">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div>
                    <h4 className="text-white font-medium">{incident.title}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      {getSeverityBadge(incident.severity)}
                      {getIncidentStatusBadge(incident.status)}
                    </div>
                  </div>
                  <SpButton variant="outline" size="sm">View Details</SpButton>
                </div>
                <div className="flex flex-wrap gap-4 text-xs text-slate-400">
                  <span>Started: {new Date(incident.startedAt).toLocaleString()}</span>
                  {incident.resolvedAt && (
                    <span>Resolved: {new Date(incident.resolvedAt).toLocaleString()}</span>
                  )}
                  <span>Affected: {incident.affectedServices.join(', ')}</span>
                </div>
              </div>
            ))}
          </div>
        </SpCard>
      )}

      {selectedTab === 'slos' && (
        <div className="space-y-4">
          {mockSLOs.map((slo) => (
            <SpCard key={slo.id} variant="bordered" padding="sm">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={clsx('w-3 h-3 rounded-full',
                      slo.status === 'healthy' ? 'bg-emerald-400' :
                      slo.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                    )} />
                    <h4 className="text-white font-medium">{slo.name}</h4>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden max-w-md">
                    <div
                      className={clsx('h-full rounded-full', getMetricBarColor(slo.status))}
                      style={{ width: `${Math.min((slo.current / slo.target) * 100, 100)}%` }}
                    />
                  </div>
                </div>
                <div className="text-right ml-6">
                  <p className={clsx('text-2xl font-bold', getStatusColor(slo.status))}>
                    {slo.current}{slo.name.includes('Latency') ? 'ms' : slo.name.includes('Rate') ? '%' : '%'}
                  </p>
                  <p className="text-xs text-slate-500">
                    Target: {slo.target}{slo.name.includes('Latency') ? 'ms' : '%'}
                  </p>
                </div>
              </div>
            </SpCard>
          ))}
        </div>
      )}
    </div>
  );
}
