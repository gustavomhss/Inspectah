import Modal from '../../../shared/components/Modal';
import type { IngestionRun } from '../../../core/api/api-types';
import IngestionStatusBadge from './IngestionStatusBadge';

interface Props {
  run: IngestionRun | null;
  open: boolean;
  onClose: () => void;
}

function IngestionRunDetailModal({ run, open, onClose }: Props) {
  if (!run) return null;
  const start = run.started_at ? new Date(run.started_at).toLocaleString() : '—';
  const finish = run.finished_at ? new Date(run.finished_at).toLocaleString() : '—';
  const durationMs =
    run.started_at && run.finished_at ? new Date(run.finished_at).getTime() - new Date(run.started_at).getTime() : null;
  const durationLabel = durationMs !== null ? `${Math.max(durationMs / 1000, 0).toFixed(1)}s` : '—';

  return (
    <Modal open={open} onClose={onClose} title={`Run ${run.id}`}>
      <div className="space-y-3 text-sm text-slate-100">
        <div className="flex items-center gap-2">
          <IngestionStatusBadge status={run.status} />
          <span className="text-xs text-slate-300">{run.trigger}</span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <p className="text-xs text-slate-300">Início</p>
            <p className="font-semibold text-white">{start}</p>
          </div>
          <div>
            <p className="text-xs text-slate-300">Fim</p>
            <p className="font-semibold text-white">{finish}</p>
          </div>
          <div>
            <p className="text-xs text-slate-300">Duração</p>
            <p className="font-semibold text-white">{durationLabel}</p>
          </div>
          <div>
            <p className="text-xs text-slate-300">Itens processados</p>
            <p className="font-semibold text-white">{run.items_processed ?? 0}</p>
          </div>
        </div>
        <div>
          <p className="text-xs text-slate-300">payload_ref</p>
          <code className="break-all text-xs text-slate-100">{run.payload_ref || '—'}</code>
        </div>
        {run.error_message ? (
          <div className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-rose-100">
            {run.error_message}
          </div>
        ) : null}
      </div>
    </Modal>
  );
}

export default IngestionRunDetailModal;
