import { useState } from 'react';
import { clsx } from 'clsx';
import { SpCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpInput } from '../../components/ui/Input';
import { SpBadge } from '../../components/ui/Badge';

interface TruthRecord {
  id: string;
  claim: string;
  verdict: 'true' | 'false' | 'misleading' | 'unverified' | 'satire';
  confidence: number;
  sources: number;
  createdAt: string;
  updatedAt: string;
  author: string;
}

const mockRecords: TruthRecord[] = [
  {
    id: '1',
    claim: 'Governo federal anuncia novo programa de habitacao popular',
    verdict: 'true',
    confidence: 0.95,
    sources: 12,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-15T14:20:00Z',
    author: 'Sistema',
  },
  {
    id: '2',
    claim: 'Presidente assinou decreto que acaba com o bolsa familia',
    verdict: 'false',
    confidence: 0.98,
    sources: 8,
    createdAt: '2024-01-15T09:00:00Z',
    updatedAt: '2024-01-15T12:00:00Z',
    author: 'Debunker-1',
  },
  {
    id: '3',
    claim: 'Vacina contra COVID causa alteracoes geneticas',
    verdict: 'false',
    confidence: 0.99,
    sources: 25,
    createdAt: '2024-01-14T15:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    author: 'Debunker-2',
  },
  {
    id: '4',
    claim: 'Novo imposto sobre compras internacionais entra em vigor em marco',
    verdict: 'misleading',
    confidence: 0.85,
    sources: 6,
    createdAt: '2024-01-14T11:00:00Z',
    updatedAt: '2024-01-14T16:00:00Z',
    author: 'Sistema',
  },
  {
    id: '5',
    claim: 'Estudo mostra que cafe previne cancer',
    verdict: 'unverified',
    confidence: 0.45,
    sources: 3,
    createdAt: '2024-01-13T09:00:00Z',
    updatedAt: '2024-01-13T14:00:00Z',
    author: 'Debunker-1',
  },
  {
    id: '6',
    claim: 'Politico X foi preso em operacao da PF',
    verdict: 'satire',
    confidence: 0.92,
    sources: 1,
    createdAt: '2024-01-12T18:00:00Z',
    updatedAt: '2024-01-12T20:00:00Z',
    author: 'Sistema',
  },
];

const verdictFilters = ['all', 'true', 'false', 'misleading', 'unverified', 'satire'];

export function SpTruthConsolePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [verdictFilter, setVerdictFilter] = useState('all');
  const [selectedRecord, setSelectedRecord] = useState<TruthRecord | null>(null);

  const filteredRecords = mockRecords.filter((record) => {
    const matchesSearch = record.claim.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesVerdict = verdictFilter === 'all' || record.verdict === verdictFilter;
    return matchesSearch && matchesVerdict;
  });

  const getVerdictBadge = (verdict: TruthRecord['verdict']) => {
    const config: Record<TruthRecord['verdict'], { variant: 'success' | 'danger' | 'warning' | 'default' | 'primary'; label: string }> = {
      true: { variant: 'success', label: 'TRUE' },
      false: { variant: 'danger', label: 'FALSE' },
      misleading: { variant: 'warning', label: 'MISLEADING' },
      unverified: { variant: 'default', label: 'UNVERIFIED' },
      satire: { variant: 'primary', label: 'SATIRE' },
    };
    return <SpBadge variant={config[verdict].variant} size="sm">{config[verdict].label}</SpBadge>;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-emerald-400';
    if (confidence >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  const trueCount = mockRecords.filter((r) => r.verdict === 'true').length;
  const falseCount = mockRecords.filter((r) => r.verdict === 'false').length;
  const misleadingCount = mockRecords.filter((r) => r.verdict === 'misleading').length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Truth Console</h1>
          <p className="text-slate-400">Manage verified claims and fact-checks</p>
        </div>
        <div className="flex gap-2">
          <SpButton variant="outline">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Export
          </SpButton>
          <SpButton>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Record
          </SpButton>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-white">{mockRecords.length}</p>
          <p className="text-xs text-slate-400">Total Records</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-emerald-400">{trueCount}</p>
          <p className="text-xs text-slate-400">Verified True</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-red-400">{falseCount}</p>
          <p className="text-xs text-slate-400">Verified False</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-yellow-400">{misleadingCount}</p>
          <p className="text-xs text-slate-400">Misleading</p>
        </SpCard>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Records List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search and Filters */}
          <SpCard variant="bordered" padding="sm">
            <div className="space-y-4">
              <SpInput
                placeholder="Search claims..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                leftIcon={
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                }
              />

              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Verdict:</span>
                <div className="flex flex-wrap gap-1">
                  {verdictFilters.map((filter) => (
                    <button
                      key={filter}
                      onClick={() => setVerdictFilter(filter)}
                      className={clsx(
                        'px-2 py-1 text-xs font-medium rounded transition-colors',
                        verdictFilter === filter
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
          </SpCard>

          {/* Records */}
          <div className="space-y-3">
            {filteredRecords.map((record) => (
              <SpCard
                key={record.id}
                variant="bordered"
                padding="sm"
                className={clsx(
                  'cursor-pointer transition-all',
                  selectedRecord?.id === record.id
                    ? 'ring-2 ring-violet-500'
                    : 'hover:border-slate-600'
                )}
                onClick={() => setSelectedRecord(record)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium truncate">{record.claim}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                      <span>{record.sources} sources</span>
                      <span>by {record.author}</span>
                      <span>{new Date(record.updatedAt).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    {getVerdictBadge(record.verdict)}
                    <span className={clsx('text-sm font-medium', getConfidenceColor(record.confidence))}>
                      {Math.round(record.confidence * 100)}%
                    </span>
                  </div>
                </div>
              </SpCard>
            ))}

            {filteredRecords.length === 0 && (
              <SpCard variant="bordered" className="text-center py-12">
                <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-lg font-semibold text-white mb-2">No records found</h3>
                <p className="text-slate-400">Try adjusting your search or filters</p>
              </SpCard>
            )}
          </div>
        </div>

        {/* Detail Panel */}
        <div className="space-y-4">
          <SpCard variant="bordered">
            {selectedRecord ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-bold text-white">Record Details</h3>
                  {getVerdictBadge(selectedRecord.verdict)}
                </div>

                <div>
                  <label className="text-xs text-slate-400">Claim</label>
                  <p className="text-white mt-1">{selectedRecord.claim}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-slate-400">Confidence</label>
                    <p className={clsx('text-lg font-bold', getConfidenceColor(selectedRecord.confidence))}>
                      {Math.round(selectedRecord.confidence * 100)}%
                    </p>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400">Sources</label>
                    <p className="text-lg font-bold text-white">{selectedRecord.sources}</p>
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-400">Author</label>
                  <p className="text-white mt-1">{selectedRecord.author}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-slate-400">Created</label>
                    <p className="text-slate-300 text-sm">
                      {new Date(selectedRecord.createdAt).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400">Updated</label>
                    <p className="text-slate-300 text-sm">
                      {new Date(selectedRecord.updatedAt).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-700 flex gap-2">
                  <SpButton variant="outline" size="sm" className="flex-1">
                    <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                    Edit
                  </SpButton>
                  <SpButton variant="outline" size="sm" className="flex-1">
                    <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Delete
                  </SpButton>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <svg className="w-12 h-12 text-slate-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                </svg>
                <p className="text-slate-400">Select a record to view details</p>
              </div>
            )}
          </SpCard>

          {/* Quick Actions */}
          <SpCard variant="bordered">
            <h3 className="text-sm font-bold text-white mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span className="text-sm">Import from CSV</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className="text-sm">Re-verify all</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm">Generate report</span>
              </button>
            </div>
          </SpCard>
        </div>
      </div>
    </div>
  );
}
