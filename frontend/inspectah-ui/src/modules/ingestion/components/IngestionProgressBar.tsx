import type { IngestionRun, IngestionStatus } from '../../../core/api/api-types';

interface Props {
  status?: IngestionStatus;
  progress: number;
  lastRun?: IngestionRun;
}

function statusLabel(status?: IngestionStatus) {
  if (!status) return 'Nenhuma ingestão executada';
  if (status === 'RUNNING') return 'Ingestão em andamento';
  if (status === 'SUCCESS') return 'Concluída com sucesso';
  if (status === 'PARTIAL_SUCCESS') return 'Concluída parcialmente';
  if (status === 'FAIL') return 'Falhou (ver detalhes)';
  return 'Status desconhecido';
}

export function IngestionProgressBar({ status, progress, lastRun }: Props) {
  const clamp = Math.min(100, Math.max(0, Math.round(progress)));
  const barColor =
    status === 'RUNNING'
      ? 'bg-amber-400'
      : status === 'SUCCESS'
        ? 'bg-emerald-400'
        : status === 'PARTIAL_SUCCESS'
          ? 'bg-amber-500'
          : status === 'FAIL'
            ? 'bg-rose-500'
            : 'bg-slate-400';

  const helper =
    status === 'RUNNING' && lastRun?.started_at
      ? `Iniciada em ${new Date(lastRun.started_at).toLocaleTimeString()}`
      : status && lastRun?.finished_at
        ? `Atualizado em ${new Date(lastRun.finished_at).toLocaleTimeString()}`
        : null;

  return (
    <div className="space-y-1" aria-live="polite">
      <div className="flex items-center justify-between text-xs text-slate-300">
        <span>{statusLabel(status)}</span>
        <span>{clamp}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/10" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={clamp}>
        <div className={`h-2 rounded-full transition-all duration-300 ease-out ${barColor}`} style={{ width: `${clamp}%` }} />
      </div>
      {helper ? <p className="text-[11px] text-slate-400">{helper}</p> : null}
    </div>
  );
}

export default IngestionProgressBar;
