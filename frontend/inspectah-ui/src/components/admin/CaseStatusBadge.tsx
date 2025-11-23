import StatusBadge from './StatusBadge';

function CaseStatusBadge({ status }: { status: string }) {
  const normalized = (status || '').toLowerCase();
  if (normalized === 'estavel' || normalized === 'ok') {
    return <StatusBadge status="ok" label="Estável" />;
  }
  return <StatusBadge status="warn" label={status || 'Em atenção'} />;
}

export default CaseStatusBadge;
