import StatusPill from '../../../shared/components/StatusPill';

function CaseStatusBadge({ status }: { status: string }) {
  return <StatusPill state={status} />;
}

export default CaseStatusBadge;
