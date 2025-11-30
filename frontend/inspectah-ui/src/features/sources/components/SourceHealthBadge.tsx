import { Badge } from '@/ui/admin';
import type { SourceHealth } from '../types/Source';

interface SourceHealthBadgeProps {
  status?: SourceHealth | null;
}

const toneByHealth: Record<SourceHealth, Parameters<typeof Badge>[0]['tone']> = {
  OK: 'success',
  DEGRADED: 'warning',
  FAIL: 'danger',
  unknown: 'neutral',
};

const labelByHealth: Record<SourceHealth, string> = {
  OK: 'Saudável',
  DEGRADED: 'Degradada',
  FAIL: 'Quebrada',
  unknown: 'Desconhecida',
};

export function SourceHealthBadge({ status }: SourceHealthBadgeProps) {
  const resolved = status || 'unknown';
  return <Badge tone={toneByHealth[resolved]}>{labelByHealth[resolved]}</Badge>;
}
