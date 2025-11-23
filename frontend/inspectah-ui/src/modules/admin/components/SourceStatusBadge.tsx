import type { AdminSourceStatus } from '../../../core/api/api-types';
import StatusBadge from './StatusBadge';

function SourceStatusBadge({ status }: { status: AdminSourceStatus }) {
  if (status === 'healthy') {
    return <StatusBadge status="ok" label="Saudável" />;
  }
  if (status === 'degraded') {
    return <StatusBadge status="warn" label="Em atenção" />;
  }
  return <StatusBadge status="unknown" label="Desconhecido" />;
}

export default SourceStatusBadge;
