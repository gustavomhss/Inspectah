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

interface Case {
  id: string;
  slug: string;
  title: string;
  category: string;
  status: 'stable' | 'attention' | 'critical';
  risk: 'low' | 'medium' | 'high';
  sourcesCount: number;
  evidenceCount: number;
  lastUpdate: string;
}

const mockCases: Case[] = [
  {
    id: '1',
    slug: 'eleicoes-2024',
    title: 'Eleições 2024',
    category: 'Política',
    status: 'attention',
    risk: 'high',
    sourcesCount: 15,
    evidenceCount: 234,
    lastUpdate: '2024-01-15T10:30:00Z',
  },
  {
    id: '2',
    slug: 'vacinas-covid',
    title: 'Vacinas COVID-19',
    category: 'Saúde',
    status: 'stable',
    risk: 'medium',
    sourcesCount: 22,
    evidenceCount: 456,
    lastUpdate: '2024-01-14T15:20:00Z',
  },
  {
    id: '3',
    slug: 'economia-br',
    title: 'Economia Brasileira',
    category: 'Economia',
    status: 'stable',
    risk: 'low',
    sourcesCount: 18,
    evidenceCount: 189,
    lastUpdate: '2024-01-15T08:45:00Z',
  },
  {
    id: '4',
    slug: 'amazonia-desmate',
    title: 'Desmatamento Amazônia',
    category: 'Meio Ambiente',
    status: 'critical',
    risk: 'high',
    sourcesCount: 12,
    evidenceCount: 78,
    lastUpdate: '2024-01-15T11:00:00Z',
  },
  {
    id: '5',
    slug: 'seguranca-publica',
    title: 'Segurança Pública',
    category: 'Segurança',
    status: 'attention',
    risk: 'medium',
    sourcesCount: 9,
    evidenceCount: 145,
    lastUpdate: '2024-01-13T16:30:00Z',
  },
];

const statusFilters = [
  { value: 'all', label: 'All' },
  { value: 'stable', label: 'Stable' },
  { value: 'attention', label: 'Attention' },
  { value: 'critical', label: 'Critical' },
];

export function SpCasesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredCases = mockCases.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.slug.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: Case['status']) => {
    const variants: Record<Case['status'], 'success' | 'warning' | 'danger'> = {
      stable: 'success',
      attention: 'warning',
      critical: 'danger',
    };
    return <SpBadge variant={variants[status]} dot>{status}</SpBadge>;
  };

  const getRiskBadge = (risk: Case['risk']) => {
    const variants: Record<Case['risk'], 'success' | 'warning' | 'danger'> = {
      low: 'success',
      medium: 'warning',
      high: 'danger',
    };
    return <SpBadge variant={variants[risk]} size="sm">{risk}</SpBadge>;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Cases</h1>
          <p className="text-slate-400">Monitor and manage fact-checking cases</p>
        </div>
        <SpButton>
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Case
        </SpButton>
      </div>

      {/* Filters */}
      <SpCard variant="bordered" padding="sm">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <SpInput
              placeholder="Search cases..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              }
            />
          </div>
          <div className="flex gap-2">
            {statusFilters.map((filter) => (
              <button
                key={filter.value}
                onClick={() => setStatusFilter(filter.value)}
                className={clsx(
                  'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                  statusFilter === filter.value
                    ? 'bg-violet-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
                )}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>
      </SpCard>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-white">{mockCases.length}</p>
          <p className="text-xs text-slate-400">Total Cases</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-emerald-400">
            {mockCases.filter((c) => c.status === 'stable').length}
          </p>
          <p className="text-xs text-slate-400">Stable</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-yellow-400">
            {mockCases.filter((c) => c.status === 'attention').length}
          </p>
          <p className="text-xs text-slate-400">Attention</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-red-400">
            {mockCases.filter((c) => c.status === 'critical').length}
          </p>
          <p className="text-xs text-slate-400">Critical</p>
        </SpCard>
      </div>

      {/* Table */}
      <SpTable>
        <SpTableHead>
          <tr>
            <SpTableHeader>Case</SpTableHeader>
            <SpTableHeader>Category</SpTableHeader>
            <SpTableHeader className="text-center">Status</SpTableHeader>
            <SpTableHeader className="text-center">Risk</SpTableHeader>
            <SpTableHeader className="text-right">Sources</SpTableHeader>
            <SpTableHeader className="text-right">Evidence</SpTableHeader>
            <SpTableHeader className="text-right">Last Update</SpTableHeader>
            <SpTableHeader className="w-24">&nbsp;</SpTableHeader>
          </tr>
        </SpTableHead>
        <SpTableBody>
          {filteredCases.map((c) => (
            <SpTableRow key={c.id}>
              <SpTableCell>
                <div>
                  <Link
                    to={`/spovest/admin/cases/${c.id}`}
                    className="font-medium text-white hover:text-violet-400 transition-colors"
                  >
                    {c.title}
                  </Link>
                  <p className="text-xs text-slate-500">{c.slug}</p>
                </div>
              </SpTableCell>
              <SpTableCell>{c.category}</SpTableCell>
              <SpTableCell className="text-center">{getStatusBadge(c.status)}</SpTableCell>
              <SpTableCell className="text-center">{getRiskBadge(c.risk)}</SpTableCell>
              <SpTableCell className="text-right">{c.sourcesCount}</SpTableCell>
              <SpTableCell className="text-right">{c.evidenceCount}</SpTableCell>
              <SpTableCell className="text-right text-slate-400">
                {new Date(c.lastUpdate).toLocaleDateString()}
              </SpTableCell>
              <SpTableCell>
                <div className="flex items-center justify-end gap-2">
                  <Link to={`/spovest/admin/cases/${c.id}/timeline`}>
                    <SpButton variant="ghost" size="sm">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </SpButton>
                  </Link>
                  <Link to={`/spovest/admin/cases/${c.id}/xray`}>
                    <SpButton variant="ghost" size="sm">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </SpButton>
                  </Link>
                </div>
              </SpTableCell>
            </SpTableRow>
          ))}
        </SpTableBody>
      </SpTable>

      {filteredCases.length === 0 && (
        <SpCard variant="bordered" className="text-center py-12">
          <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-white mb-2">No cases found</h3>
          <p className="text-slate-400">Try adjusting your search or filters</p>
        </SpCard>
      )}
    </div>
  );
}
