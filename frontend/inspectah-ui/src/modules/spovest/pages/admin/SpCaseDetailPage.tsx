import { useParams, Link } from 'react-router-dom';
import { clsx } from 'clsx';
import { SpCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpBadge } from '../../components/ui/Badge';

interface TimelineEvent {
  id: string;
  type: 'claim' | 'evidence' | 'debunk' | 'verdict' | 'update';
  title: string;
  description: string;
  timestamp: string;
  actor: string;
}

const mockCase = {
  id: '1',
  title: 'Afirmacao sobre nova lei trabalhista',
  description: 'Claim viralizado sobre mudancas na CLT que circula em redes sociais desde janeiro de 2024.',
  status: 'investigating' as const,
  priority: 'high' as const,
  createdAt: '2024-01-10T08:00:00Z',
  updatedAt: '2024-01-15T14:30:00Z',
  claimsCount: 5,
  evidenceCount: 12,
  sourcesCount: 8,
  assignedTo: 'Debunker-1',
  tags: ['politica', 'trabalho', 'fake-news'],
};

const mockTimeline: TimelineEvent[] = [
  {
    id: '1',
    type: 'claim',
    title: 'Claim inicial detectado',
    description: 'Post viral no Facebook com 50k compartilhamentos identificado.',
    timestamp: '2024-01-10T08:00:00Z',
    actor: 'Sistema',
  },
  {
    id: '2',
    type: 'evidence',
    title: 'Evidencias coletadas',
    description: '5 fontes oficiais consultadas. Documento do Ministerio do Trabalho obtido.',
    timestamp: '2024-01-10T10:30:00Z',
    actor: 'Ingestion Pipeline',
  },
  {
    id: '3',
    type: 'debunk',
    title: 'Analise iniciada',
    description: 'Debunker-1 assumiu o caso. Verificacao cruzada em andamento.',
    timestamp: '2024-01-11T09:00:00Z',
    actor: 'Debunker-1',
  },
  {
    id: '4',
    type: 'update',
    title: 'Novas evidencias',
    description: 'Comunicado oficial do governo adicionado ao caso.',
    timestamp: '2024-01-12T14:00:00Z',
    actor: 'Sistema',
  },
  {
    id: '5',
    type: 'debunk',
    title: 'Parecer preliminar',
    description: 'Claim parcialmente falso. Aguardando confirmacao adicional.',
    timestamp: '2024-01-15T10:00:00Z',
    actor: 'Debunker-1',
  },
];

const mockEvidence = [
  { id: '1', type: 'document', title: 'Nota oficial do Ministerio do Trabalho', source: 'gov.br', relevance: 'high' },
  { id: '2', type: 'article', title: 'Materia do G1 sobre CLT', source: 'g1.com.br', relevance: 'medium' },
  { id: '3', type: 'social', title: 'Post original viralizado', source: 'Facebook', relevance: 'high' },
  { id: '4', type: 'document', title: 'Texto da lei atual', source: 'planalto.gov.br', relevance: 'high' },
];

export function SpCaseDetailPage() {
  const { caseId } = useParams();

  const getStatusBadge = (status: typeof mockCase.status) => {
    const config = {
      pending: { variant: 'default' as const, label: 'PENDING' },
      investigating: { variant: 'warning' as const, label: 'INVESTIGATING' },
      verified: { variant: 'success' as const, label: 'VERIFIED' },
      debunked: { variant: 'danger' as const, label: 'DEBUNKED' },
      closed: { variant: 'default' as const, label: 'CLOSED' },
    };
    return <SpBadge variant={config[status].variant} dot>{config[status].label}</SpBadge>;
  };

  const getPriorityBadge = (priority: typeof mockCase.priority) => {
    const config = {
      critical: { variant: 'danger' as const, label: 'CRITICAL' },
      high: { variant: 'warning' as const, label: 'HIGH' },
      medium: { variant: 'primary' as const, label: 'MEDIUM' },
      low: { variant: 'default' as const, label: 'LOW' },
    };
    return <SpBadge variant={config[priority].variant} size="sm">{config[priority].label}</SpBadge>;
  };

  const getEventIcon = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'claim':
        return (
          <div className="w-8 h-8 rounded-full bg-violet-600/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
          </div>
        );
      case 'evidence':
        return (
          <div className="w-8 h-8 rounded-full bg-cyan-600/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        );
      case 'debunk':
        return (
          <div className="w-8 h-8 rounded-full bg-orange-600/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        );
      case 'verdict':
        return (
          <div className="w-8 h-8 rounded-full bg-emerald-600/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 rounded-full bg-slate-600/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        );
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Link to="/spovest/admin/cases" className="hover:text-white transition-colors">Cases</Link>
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span className="text-white">Case #{caseId || mockCase.id}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-white">{mockCase.title}</h1>
            {getStatusBadge(mockCase.status)}
          </div>
          <p className="text-slate-400">{mockCase.description}</p>
        </div>
        <div className="flex gap-2">
          <SpButton variant="outline">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            Edit
          </SpButton>
          <SpButton>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Close Case
          </SpButton>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-violet-400">{mockCase.claimsCount}</p>
          <p className="text-xs text-slate-400">Claims</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-cyan-400">{mockCase.evidenceCount}</p>
          <p className="text-xs text-slate-400">Evidence</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-2xl font-bold text-orange-400">{mockCase.sourcesCount}</p>
          <p className="text-xs text-slate-400">Sources</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          {getPriorityBadge(mockCase.priority)}
          <p className="text-xs text-slate-400 mt-1">Priority</p>
        </SpCard>
        <SpCard variant="bordered" padding="sm" className="text-center">
          <p className="text-lg font-bold text-white">{mockCase.assignedTo}</p>
          <p className="text-xs text-slate-400">Assigned To</p>
        </SpCard>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Timeline */}
        <div className="lg:col-span-2">
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-6">Timeline</h3>
            <div className="space-y-6">
              {mockTimeline.map((event, index) => (
                <div key={event.id} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    {getEventIcon(event.type)}
                    {index < mockTimeline.length - 1 && (
                      <div className="w-0.5 flex-1 bg-slate-700 mt-2"></div>
                    )}
                  </div>
                  <div className="flex-1 pb-6">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="font-medium text-white">{event.title}</h4>
                      <span className="text-xs text-slate-500 whitespace-nowrap">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 mb-2">{event.description}</p>
                    <span className="text-xs text-slate-500">by {event.actor}</span>
                  </div>
                </div>
              ))}
            </div>
          </SpCard>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Evidence */}
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Evidence</h3>
            <div className="space-y-3">
              {mockEvidence.map((item) => (
                <div key={item.id} className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{item.title}</p>
                      <p className="text-xs text-slate-500">{item.source}</p>
                    </div>
                    <span className={clsx(
                      'text-xs px-2 py-0.5 rounded',
                      item.relevance === 'high' ? 'bg-emerald-400/10 text-emerald-400' :
                      item.relevance === 'medium' ? 'bg-yellow-400/10 text-yellow-400' :
                      'bg-slate-400/10 text-slate-400'
                    )}>
                      {item.relevance}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <SpButton variant="outline" size="sm" className="w-full mt-4">
              View All Evidence
            </SpButton>
          </SpCard>

          {/* Tags */}
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {mockCase.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 text-sm bg-slate-800 text-slate-300 rounded-full"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </SpCard>

          {/* Metadata */}
          <SpCard variant="bordered">
            <h3 className="text-lg font-bold text-white mb-4">Details</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-slate-500">Created</label>
                <p className="text-sm text-slate-300">{new Date(mockCase.createdAt).toLocaleString()}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Last Updated</label>
                <p className="text-sm text-slate-300">{new Date(mockCase.updatedAt).toLocaleString()}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Case ID</label>
                <p className="text-sm text-slate-300 font-mono">{mockCase.id}</p>
              </div>
            </div>
          </SpCard>
        </div>
      </div>
    </div>
  );
}
