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

interface Agent {
  id: string;
  name: string;
  role: 'interpreter' | 'classifier' | 'analyst' | 'debunker' | 'decision_maker' | 'librarian';
  layer: 'interpretation' | 'classification' | 'debunk';
  status: 'active' | 'paused' | 'deprecated';
  model: string;
  version: string;
  analysesCount: number;
  avgLatency: number;
  lastActive: string;
}

const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Interpreter-v3',
    role: 'interpreter',
    layer: 'interpretation',
    status: 'active',
    model: 'gpt-4-turbo',
    version: '3.2.1',
    analysesCount: 15420,
    avgLatency: 1250,
    lastActive: '2024-01-15T10:30:00Z',
  },
  {
    id: '2',
    name: 'Classifier-BR',
    role: 'classifier',
    layer: 'classification',
    status: 'active',
    model: 'claude-3-opus',
    version: '2.1.0',
    analysesCount: 8934,
    avgLatency: 890,
    lastActive: '2024-01-15T10:28:00Z',
  },
  {
    id: '3',
    name: 'Debunker-Primary',
    role: 'debunker',
    layer: 'debunk',
    status: 'active',
    model: 'gpt-4-turbo',
    version: '4.0.0',
    analysesCount: 5621,
    avgLatency: 2100,
    lastActive: '2024-01-15T10:25:00Z',
  },
  {
    id: '4',
    name: 'Debunker-Secondary',
    role: 'debunker',
    layer: 'debunk',
    status: 'active',
    model: 'claude-3-sonnet',
    version: '3.5.2',
    analysesCount: 5589,
    avgLatency: 1850,
    lastActive: '2024-01-15T10:25:00Z',
  },
  {
    id: '5',
    name: 'Mediator-v2',
    role: 'decision_maker',
    layer: 'debunk',
    status: 'active',
    model: 'gpt-4-turbo',
    version: '2.0.0',
    analysesCount: 2834,
    avgLatency: 980,
    lastActive: '2024-01-15T10:20:00Z',
  },
  {
    id: '6',
    name: 'Analyst-Economy',
    role: 'analyst',
    layer: 'classification',
    status: 'paused',
    model: 'claude-3-haiku',
    version: '1.2.0',
    analysesCount: 1245,
    avgLatency: 450,
    lastActive: '2024-01-14T18:00:00Z',
  },
  {
    id: '7',
    name: 'Librarian-v1',
    role: 'librarian',
    layer: 'interpretation',
    status: 'deprecated',
    model: 'gpt-3.5-turbo',
    version: '1.0.0',
    analysesCount: 3456,
    avgLatency: 320,
    lastActive: '2024-01-10T12:00:00Z',
  },
];

const layerFilters = ['all', 'interpretation', 'classification', 'debunk'];
const roleFilters = ['all', 'interpreter', 'classifier', 'analyst', 'debunker', 'decision_maker', 'librarian'];
const statusFilters = ['all', 'active', 'paused', 'deprecated'];

export function SpAgentsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [layerFilter, setLayerFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredAgents = mockAgents.filter((a) => {
    const matchesSearch = a.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesLayer = layerFilter === 'all' || a.layer === layerFilter;
    const matchesRole = roleFilter === 'all' || a.role === roleFilter;
    const matchesStatus = statusFilter === 'all' || a.status === statusFilter;
    return matchesSearch && matchesLayer && matchesRole && matchesStatus;
  });

  const getStatusBadge = (status: Agent['status']) => {
    const variants: Record<Agent['status'], 'success' | 'warning' | 'default'> = {
      active: 'success',
      paused: 'warning',
      deprecated: 'default',
    };
    return <SpBadge variant={variants[status]} dot size="sm">{status}</SpBadge>;
  };

  const getLayerBadge = (layer: Agent['layer']) => {
    const colors: Record<Agent['layer'], string> = {
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

  const getRoleBadge = (role: Agent['role']) => {
    return <SpBadge variant="primary" size="sm">{role.replace('_', ' ')}</SpBadge>;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Agents</h1>
          <p className="text-slate-400">Manage AI agents and their configurations</p>
        </div>
        <div className="flex gap-2">
          <Link to="/spovest/admin/agents/flow">
            <SpButton variant="outline">
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
              Flow Editor
            </SpButton>
          </Link>
          <SpButton>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Agent
          </SpButton>
        </div>
      </div>

      {/* Filters */}
      <SpCard variant="bordered" padding="sm">
        <div className="space-y-4">
          <SpInput
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />

          <div className="flex flex-wrap gap-4">
            {/* Layer Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Layer:</span>
              <div className="flex gap-1">
                {layerFilters.map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setLayerFilter(filter)}
                    className={clsx(
                      'px-2 py-1 text-xs font-medium rounded transition-colors',
                      layerFilter === filter
                        ? 'bg-violet-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    )}
                  >
                    {filter}
                  </button>
                ))}
              </div>
            </div>

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
          </div>
        </div>
      </SpCard>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-white">{mockAgents.length}</p>
          <p className="text-xs text-slate-400">Total Agents</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-emerald-400">
            {mockAgents.filter((a) => a.status === 'active').length}
          </p>
          <p className="text-xs text-slate-400">Active</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-violet-400">
            {mockAgents.reduce((sum, a) => sum + a.analysesCount, 0).toLocaleString()}
          </p>
          <p className="text-xs text-slate-400">Total Analyses</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-cyan-400">
            {Math.round(mockAgents.reduce((sum, a) => sum + a.avgLatency, 0) / mockAgents.length)}ms
          </p>
          <p className="text-xs text-slate-400">Avg Latency</p>
        </SpCard>
      </div>

      {/* Table */}
      <SpTable>
        <SpTableHead>
          <tr>
            <SpTableHeader>Agent</SpTableHeader>
            <SpTableHeader>Layer</SpTableHeader>
            <SpTableHeader>Role</SpTableHeader>
            <SpTableHeader className="text-center">Status</SpTableHeader>
            <SpTableHeader>Model</SpTableHeader>
            <SpTableHeader className="text-right">Analyses</SpTableHeader>
            <SpTableHeader className="text-right">Latency</SpTableHeader>
            <SpTableHeader className="w-20">&nbsp;</SpTableHeader>
          </tr>
        </SpTableHead>
        <SpTableBody>
          {filteredAgents.map((agent) => (
            <SpTableRow key={agent.id}>
              <SpTableCell>
                <div>
                  <Link
                    to={`/spovest/admin/agents/${agent.id}`}
                    className="font-medium text-white hover:text-violet-400 transition-colors"
                  >
                    {agent.name}
                  </Link>
                  <p className="text-xs text-slate-500">v{agent.version}</p>
                </div>
              </SpTableCell>
              <SpTableCell>{getLayerBadge(agent.layer)}</SpTableCell>
              <SpTableCell>{getRoleBadge(agent.role)}</SpTableCell>
              <SpTableCell className="text-center">{getStatusBadge(agent.status)}</SpTableCell>
              <SpTableCell className="text-slate-300 text-sm">{agent.model}</SpTableCell>
              <SpTableCell className="text-right font-medium text-white">
                {agent.analysesCount.toLocaleString()}
              </SpTableCell>
              <SpTableCell className="text-right">
                <span className={clsx(
                  agent.avgLatency < 1000 ? 'text-emerald-400' :
                  agent.avgLatency < 2000 ? 'text-yellow-400' : 'text-red-400'
                )}>
                  {agent.avgLatency}ms
                </span>
              </SpTableCell>
              <SpTableCell>
                <Link to={`/spovest/admin/agents/${agent.id}`}>
                  <SpButton variant="ghost" size="sm">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </SpButton>
                </Link>
              </SpTableCell>
            </SpTableRow>
          ))}
        </SpTableBody>
      </SpTable>

      {filteredAgents.length === 0 && (
        <SpCard variant="bordered" className="text-center py-12">
          <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 className="text-lg font-semibold text-white mb-2">No agents found</h3>
          <p className="text-slate-400">Try adjusting your filters</p>
        </SpCard>
      )}
    </div>
  );
}
