import { useTruthStateLabel } from '../hooks/useTruthStateLabel';
import Badge from './Badge';

interface StatusPillProps {
  state?: string | null;
}

const toneMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'default'> = {
  success: 'success',
  warning: 'warning',
  danger: 'danger',
  info: 'info',
};

function StatusPill({ state }: StatusPillProps) {
  const meta = useTruthStateLabel(state);
  const tone = toneMap[meta.tone] ?? 'default';

  return (
    <Badge tone={tone}>
      <span>{meta.label}</span>
    </Badge>
  );
}

export default StatusPill;
