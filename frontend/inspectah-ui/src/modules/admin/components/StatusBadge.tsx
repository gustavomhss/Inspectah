interface Props {
  status: 'ok' | 'warn' | 'unknown' | 'error';
  label?: string;
}

function StatusBadge({ status, label }: Props) {
  const color =
    status === 'ok'
      ? 'bg-emerald-500/20 text-emerald-200 border-emerald-400/40'
      : status === 'warn'
        ? 'bg-amber-500/15 text-amber-200 border-amber-400/50'
        : status === 'error'
          ? 'bg-red-500/20 text-red-200 border-red-400/40'
          : 'bg-slate-500/20 text-slate-200 border-slate-400/30';
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${color}`}>
      <span className="h-2 w-2 rounded-full bg-current" />
      {label || status}
    </span>
  );
}

export default StatusBadge;
