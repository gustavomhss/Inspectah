import { Badge } from '@/ui/admin';
import type { SourceStatus } from '../types/Source';

interface SourceStatusBadgeProps {
  status: SourceStatus;
}

const toneByStatus: Record<SourceStatus, Parameters<typeof Badge>[0]['tone']> = {
  PROPOSED: 'info',
  TESTING: 'info',
  ACTIVE: 'success',
  UNDER_REVIEW: 'warning',
  SUSPECT: 'warning',
  DISABLED_TEMP: 'warning',
  DISABLED_PERM: 'danger',
};

const labelByStatus: Record<SourceStatus, string> = {
  PROPOSED: 'Proposta',
  TESTING: 'Em teste',
  ACTIVE: 'Ativa',
  UNDER_REVIEW: 'Em revisão',
  SUSPECT: 'Suspeita',
  DISABLED_TEMP: 'Pausada',
  DISABLED_PERM: 'Arquivada',
};

export function SourceStatusBadge({ status }: SourceStatusBadgeProps) {
  return <Badge tone={toneByStatus[status]}>{labelByStatus[status]}</Badge>;
}
