import { useState } from 'react';
import { clsx } from 'clsx';
import { SpCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpInput } from '../../components/ui/Input';
import { SpBadge } from '../../components/ui/Badge';

interface GuardianClaim {
  id: string;
  claim: string;
  source: string;
  submittedAt: string;
  status: 'pending' | 'validating' | 'validated' | 'rejected';
  verdict: 'true' | 'false' | 'misleading' | null;
  confidence: number | null;
  evidenceCount: number;
  validatorId: string | null;
}

const mockClaims: GuardianClaim[] = [
  {
    id: '1',
    claim: 'Ministro afirma que inflacao vai cair para 3% ate o final do ano',
    source: 'G1 Economia',
    submittedAt: '2024-01-15T10:30:00Z',
    status: 'validating',
    verdict: null,
    confidence: null,
    evidenceCount: 5,
    validatorId: 'Debunker-1',
  },
  {
    id: '2',
    claim: 'Brasil bate recorde de exportacao de soja em 2024',
    source: 'Folha Agro',
    submittedAt: '2024-01-15T09:45:00Z',
    status: 'validated',
    verdict: 'true',
    confidence: 0.94,
    evidenceCount: 8,
    validatorId: 'Debunker-2',
  },
  {
    id: '3',
    claim: 'Governo vai acabar com o Pix gratuito a partir de marco',
    source: 'WhatsApp Forward',
    submittedAt: '2024-01-15T09:00:00Z',
    status: 'validated',
    verdict: 'false',
    confidence: 0.99,
    evidenceCount: 12,
    validatorId: 'Debunker-1',
  },
  {
    id: '4',
    claim: 'Nova lei de transito aumenta multas em 50%',
    source: 'Portal de Noticias',
    submittedAt: '2024-01-15T08:30:00Z',
    status: 'validated',
    verdict: 'misleading',
    confidence: 0.87,
    evidenceCount: 6,
    validatorId: 'Debunker-3',
  },
  {
    id: '5',
    claim: 'Terremoto de magnitude 7 atinge o sul do Brasil',
    source: 'Twitter Viral',
    submittedAt: '2024-01-15T08:00:00Z',
    status: 'rejected',
    verdict: null,
    confidence: null,
    evidenceCount: 0,
    validatorId: null,
  },
  {
    id: '6',
    claim: 'Novo beneficio do governo para familias com renda ate 2 salarios',
    source: 'Facebook Share',
    submittedAt: '2024-01-15T07:30:00Z',
    status: 'pending',
    verdict: null,
    confidence: null,
    evidenceCount: 0,
    validatorId: null,
  },
];

const statusFilters = ['all', 'pending', 'validating', 'validated', 'rejected'];

export function SpGuardianPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedClaim, setSelectedClaim] = useState<GuardianClaim | null>(null);

  const filteredClaims = mockClaims.filter((claim) => {
    const matchesSearch = claim.claim.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || claim.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: GuardianClaim['status']) => {
    const config: Record<GuardianClaim['status'], { variant: 'default' | 'warning' | 'success' | 'danger'; label: string }> = {
      pending: { variant: 'default', label: 'PENDING' },
      validating: { variant: 'warning', label: 'VALIDATING' },
      validated: { variant: 'success', label: 'VALIDATED' },
      rejected: { variant: 'danger', label: 'REJECTED' },
    };
    return <SpBadge variant={config[status].variant} dot size="sm">{config[status].label}</SpBadge>;
  };

  const getVerdictBadge = (verdict: GuardianClaim['verdict']) => {
    if (!verdict) return null;
    const config: Record<NonNullable<GuardianClaim['verdict']>, { variant: 'success' | 'danger' | 'warning'; label: string }> = {
      true: { variant: 'success', label: 'TRUE' },
      false: { variant: 'danger', label: 'FALSE' },
      misleading: { variant: 'warning', label: 'MISLEADING' },
    };
    return <SpBadge variant={config[verdict].variant} size="sm">{config[verdict].label}</SpBadge>;
  };

  const pendingCount = mockClaims.filter((c) => c.status === 'pending').length;
  const validatingCount = mockClaims.filter((c) => c.status === 'validating').length;
  const validatedToday = mockClaims.filter((c) => c.status === 'validated').length;
  const avgConfidence = mockClaims
    .filter((c) => c.confidence !== null)
    .reduce((sum, c) => sum + (c.confidence || 0), 0) / mockClaims.filter((c) => c.confidence !== null).length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Guardian Cockpit</h1>
          <p className="text-slate-400">Monitor and validate claims in real-time</p>
        </div>
        <div className="flex gap-2">
          <SpButton variant="outline">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Settings
          </SpButton>
          <SpButton>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Submit Claim
          </SpButton>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <SpCard variant="bordered" padding="sm">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-slate-400"></div>
            <div>
              <p className="text-2xl font-bold text-white">{pendingCount}</p>
              <p className="text-xs text-slate-400">Pending</p>
            </div>
          </div>
        </SpCard>
        <SpCard variant="bordered" padding="sm">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></div>
            <div>
              <p className="text-2xl font-bold text-yellow-400">{validatingCount}</p>
              <p className="text-xs text-slate-400">Validating</p>
            </div>
          </div>
        </SpCard>
        <SpCard variant="bordered" padding="sm">
          <p className="text-2xl font-bold text-emerald-400">{validatedToday}</p>
          <p className="text-xs text-slate-400">Validated Today</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm">
          <p className="text-2xl font-bold text-violet-400">{Math.round(avgConfidence * 100)}%</p>
          <p className="text-xs text-slate-400">Avg Confidence</p>
        </SpCard>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Claims List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filters */}
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
                <span className="text-xs text-slate-400">Status:</span>
                <div className="flex flex-wrap gap-1">
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
          </SpCard>

          {/* Claims */}
          <div className="space-y-3">
            {filteredClaims.map((claim) => (
              <SpCard
                key={claim.id}
                variant="bordered"
                padding="sm"
                className={clsx(
                  'cursor-pointer transition-all',
                  selectedClaim?.id === claim.id
                    ? 'ring-2 ring-violet-500'
                    : 'hover:border-slate-600'
                )}
                onClick={() => setSelectedClaim(claim)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium">{claim.claim}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                      <span>{claim.source}</span>
                      <span>{new Date(claim.submittedAt).toLocaleTimeString()}</span>
                      {claim.evidenceCount > 0 && (
                        <span className="text-cyan-400">{claim.evidenceCount} evidence</span>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    {getStatusBadge(claim.status)}
                    {claim.verdict && getVerdictBadge(claim.verdict)}
                  </div>
                </div>
              </SpCard>
            ))}

            {filteredClaims.length === 0 && (
              <SpCard variant="bordered" className="text-center py-12">
                <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <h3 className="text-lg font-semibold text-white mb-2">No claims found</h3>
                <p className="text-slate-400">Try adjusting your filters</p>
              </SpCard>
            )}
          </div>
        </div>

        {/* Detail Panel */}
        <div className="space-y-4">
          <SpCard variant="bordered">
            {selectedClaim ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-bold text-white">Claim Details</h3>
                  {getStatusBadge(selectedClaim.status)}
                </div>

                <div>
                  <label className="text-xs text-slate-400">Claim</label>
                  <p className="text-white mt-1">{selectedClaim.claim}</p>
                </div>

                <div>
                  <label className="text-xs text-slate-400">Source</label>
                  <p className="text-slate-300 mt-1">{selectedClaim.source}</p>
                </div>

                {selectedClaim.verdict && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs text-slate-400">Verdict</label>
                      <div className="mt-1">{getVerdictBadge(selectedClaim.verdict)}</div>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400">Confidence</label>
                      <p className={clsx(
                        'text-lg font-bold',
                        selectedClaim.confidence && selectedClaim.confidence >= 0.9 ? 'text-emerald-400' :
                        selectedClaim.confidence && selectedClaim.confidence >= 0.7 ? 'text-yellow-400' : 'text-red-400'
                      )}>
                        {selectedClaim.confidence ? `${Math.round(selectedClaim.confidence * 100)}%` : '-'}
                      </p>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-slate-400">Evidence</label>
                    <p className="text-lg font-bold text-cyan-400">{selectedClaim.evidenceCount}</p>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400">Validator</label>
                    <p className="text-slate-300">{selectedClaim.validatorId || '-'}</p>
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-400">Submitted</label>
                  <p className="text-slate-300 text-sm">
                    {new Date(selectedClaim.submittedAt).toLocaleString()}
                  </p>
                </div>

                {selectedClaim.status === 'pending' && (
                  <div className="pt-4 border-t border-slate-700 flex gap-2">
                    <SpButton size="sm" className="flex-1">
                      <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Start Validation
                    </SpButton>
                    <SpButton variant="outline" size="sm">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </SpButton>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <svg className="w-12 h-12 text-slate-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <p className="text-slate-400">Select a claim to view details</p>
              </div>
            )}
          </SpCard>

          {/* Validation Queue */}
          <SpCard variant="bordered">
            <h3 className="text-sm font-bold text-white mb-3">Validation Queue</h3>
            <div className="space-y-2">
              {mockClaims.filter((c) => c.status === 'validating').map((claim) => (
                <div key={claim.id} className="flex items-center gap-3 p-2 bg-slate-800/50 rounded-lg">
                  <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">{claim.claim}</p>
                    <p className="text-xs text-slate-500">{claim.validatorId}</p>
                  </div>
                </div>
              ))}
              {mockClaims.filter((c) => c.status === 'validating').length === 0 && (
                <p className="text-sm text-slate-500 text-center py-2">No claims in queue</p>
              )}
            </div>
          </SpCard>
        </div>
      </div>
    </div>
  );
}
