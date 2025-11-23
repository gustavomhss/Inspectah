import CaseStatusBadge from '../../../admin/components/CaseStatusBadge';
import RiskBadge from '../../../admin/components/RiskBadge';
import type { AdminCaseXRay } from '../../../../core/api/api-types';
import AnchorsPanel from './AnchorsPanel';
import CommitteesPanel from './CommitteesPanel';
import DebunkerPanel from './DebunkerPanel';
import EvidenceSummaryPanel from './EvidenceSummaryPanel';

function CaseXRayLayout({ xray }: { xray: AdminCaseXRay }) {
  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Visão do caso</p>
            <h3 className="text-2xl font-bold text-white">{xray.title}</h3>
            <p className="text-sm text-slate-200">{xray.category || 'sem categoria'}</p>
          </div>
          <div className="flex items-center gap-2">
            <CaseStatusBadge status={xray.status} />
            <RiskBadge risk={xray.risk} />
          </div>
        </div>
        <p className="mt-3 text-sm text-slate-200">{xray.summary}</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <DebunkerPanel debunker={xray.debunker} risk={xray.risk} />
        <CommitteesPanel committees={xray.committees} />
        <AnchorsPanel anchors={xray.anchors} />
        <EvidenceSummaryPanel evidences={xray.evidences} />
      </div>
    </div>
  );
}

export default CaseXRayLayout;
