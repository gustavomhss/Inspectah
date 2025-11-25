import Badge from '../../../shared/components/Badge';
import type { IngestionStatus } from '../../../core/api/api-types';

const STATUS_MAP: Record<
  IngestionStatus | 'NEVER',
  { label: string; tone: 'success' | 'warning' | 'danger' | 'info' | 'default' }
> = {
  SUCCESS: { label: 'Sucesso', tone: 'success' },
  FAIL: { label: 'Falhou', tone: 'danger' },
  RUNNING: { label: 'Em andamento', tone: 'warning' },
  PARTIAL_SUCCESS: { label: 'Parcial', tone: 'warning' },
  PENDING: { label: 'Pendente', tone: 'info' },
  NEVER: { label: 'Nunca rodou', tone: 'default' },
};

interface Props {
  status?: IngestionStatus;
  showNever?: boolean;
}

function IngestionStatusBadge({ status, showNever }: Props) {
  const key = status || (showNever ? 'NEVER' : 'PENDING');
  const entry = STATUS_MAP[key];
  return <Badge tone={entry.tone}>{entry.label}</Badge>;
}

export default IngestionStatusBadge;
