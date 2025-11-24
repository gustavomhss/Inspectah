import type { AdminSourceHealthStatus } from '../../../core/api/api-types';
import StatusBadge from './StatusBadge';

function SourceStatusBadge({ status }: { status: AdminSourceHealthStatus }) {
  if (status === 'OK') {
    return <StatusBadge status="ok" label="Saudável" />;
  }
  if (status === 'DEGRADED') {
    return <StatusBadge status="warn" label="Em atenção" />;
  }
  if (status === 'FAIL') {
    return <StatusBadge status="error" label="Falha" />;
  }
  return <StatusBadge status="unknown" label="Desconhecido" />;
}

export default SourceStatusBadge;
