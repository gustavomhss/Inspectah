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
  const meta = (run.meta as Record<string, unknown>) || {};
  const attempts = Array.isArray(meta.attempts) ? (meta.attempts as Array<Record<string, unknown>>) : [];
  const metaPairs: Array<{ label: string; value: string }> = [
    { label: 'Trigger origin', value: String(meta.trigger_origin ?? '—') },
    { label: 'Domínios', value: Array.isArray(meta.domains) ? meta.domains.join(', ') : String(meta.domains ?? '—') },
    { label: 'Size requisitado', value: String(meta.requested_size ?? '—') },
    { label: 'Size por requisição', value: String(meta.per_request_size ?? '—') },
    { label: 'Itens buscados', value: String(meta.fetched ?? '—') },
    { label: 'Itens deduplicados', value: String(meta.deduped ?? '—') },
    { label: 'Duplicatas', value: String(meta.duplicates ?? '—') },
    { label: 'Requests', value: String(meta.requests_count ?? (attempts.length || '—')) },
    { label: 'Throttle (s)', value: String(meta.throttle_seconds ?? '—') },
    { label: 'Max attempts', value: String(meta.max_attempts ?? '—') },
    { label: 'Erro', value: String(meta.error_type ?? meta.error_code ?? '—') },
    { label: 'Payload ref', value: String(run.payload_ref || '—') },
    { label: 'Operation id', value: String(meta.operation_id ?? '—') },
    { label: 'Actor', value: String(meta.actor ?? '—') },
    { label: 'Catalog hash', value: String(meta.catalog_hash ?? meta.flow_catalog_hash ?? '—') },
    { label: 'Hash run', value: String(meta.hash ?? meta.flow_hash ?? '—') },
  ].filter((entry) => entry.value && entry.value !== '—');

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
        {metaPairs.length ? (
          <div className="grid grid-cols-2 gap-2 rounded-lg border border-white/10 bg-white/5 p-3">
            {metaPairs.map((entry) => (
              <div key={entry.label}>
                <p className="text-[11px] uppercase tracking-wide text-slate-400">{entry.label}</p>
                <p className="break-all text-sm text-white">{entry.value}</p>
              </div>
            ))}
          </div>
        ) : null}
        {attempts.length ? (
          <div className="rounded-lg border border-white/10 bg-white/5 p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Tentativas</p>
            <div className="mt-2 max-h-48 overflow-y-auto rounded-lg border border-white/5">
              <table className="min-w-full text-xs">
                <thead className="bg-white/5 text-[11px] uppercase tracking-wide text-slate-300">
                  <tr>
                    <th className="px-2 py-1 text-left">#</th>
                    <th className="px-2 py-1 text-left">Status</th>
                    <th className="px-2 py-1 text-left">Erro</th>
                    <th className="px-2 py-1 text-left">Backoff</th>
                    <th className="px-2 py-1 text-left">Duração</th>
                  </tr>
                </thead>
                <tbody>
                  {attempts.map((att, idx) => {
                    const durationRaw = att.duration_seconds;
                    const duration =
                      typeof durationRaw === 'number'
                        ? `${durationRaw.toFixed(2)}s`
                        : durationRaw
                          ? `${String(durationRaw)}s`
                          : '—';
                    const backoff =
                      typeof att.backoff_seconds === 'number' ? `${att.backoff_seconds.toFixed(2)}s` : att.backoff_seconds ? String(att.backoff_seconds) : '—';
                    return (
                      <tr key={`${att.attempt ?? idx}`} className="odd:bg-white/5">
                        <td className="px-2 py-1">{String(att.attempt ?? idx + 1)}</td>
                        <td className="px-2 py-1">{att.status_code ?? '—'}</td>
                        <td className="px-2 py-1">{att.error ? String(att.error) : '—'}</td>
                        <td className="px-2 py-1">{backoff}</td>
                        <td className="px-2 py-1">{duration}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}
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
