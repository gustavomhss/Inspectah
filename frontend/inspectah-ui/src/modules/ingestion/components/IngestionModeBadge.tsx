import Badge from '../../../shared/components/Badge';
import type { IngestionMode } from '../../../core/api/api-types';

interface Props {
  mode: IngestionMode;
  onToggle?: (mode: IngestionMode) => void;
}

function IngestionModeBadge({ mode, onToggle }: Props) {
  const label = mode === 'AUTOMATIC' ? 'Automático' : 'Manual';
  const tone = mode === 'AUTOMATIC' ? 'success' : 'warning';

  return (
    <button
      type="button"
      onClick={() => onToggle?.(mode === 'AUTOMATIC' ? 'MANUAL_ONLY' : 'AUTOMATIC')}
      className="inline-flex items-center gap-2 rounded-full bg-transparent text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
      aria-label={`Modo de ingestão: ${label}`}
    >
      <Badge tone={tone}>{label}</Badge>
      {onToggle ? <span className="text-xs text-slate-300 underline">Alterar</span> : null}
    </button>
  );
}

export default IngestionModeBadge;
