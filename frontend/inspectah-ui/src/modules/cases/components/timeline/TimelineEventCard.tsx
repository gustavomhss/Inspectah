import type { AdminTimelineEvent, TimelineSeverity } from '../../../../core/api/api-types';

const severityStyle: Record<TimelineSeverity | 'default', string> = {
  critical: 'bg-rose-500/20 text-rose-100 border border-rose-500/30',
  warning: 'bg-amber-400/20 text-amber-100 border border-amber-400/30',
  info: 'bg-sky-400/15 text-sky-100 border border-sky-400/30',
  default: 'bg-white/5 text-slate-100 border border-white/5',
};

function formatDate(iso: string) {
  const date = new Date(iso);
  return date.toLocaleString('pt-BR', { timeZone: 'UTC' });
}

function TimelineEventCard({ event }: { event: AdminTimelineEvent }) {
  const badgeClass = severityStyle[event.severity || 'default'] || severityStyle.default;
  return (
    <div className="relative rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
      <div className="absolute left-[-10px] top-5 h-2 w-2 rounded-full bg-sky-300" />
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-300">{event.event_type}</p>
          <p className="text-base font-semibold text-white">{event.summary || 'Evento sem resumo'}</p>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-200">
            <span className={`rounded-full px-2 py-1 ${badgeClass}`}>{event.severity || 'info'}</span>
            {event.source && <span className="rounded-full bg-white/5 px-2 py-1 text-slate-200">Fonte: {event.source}</span>}
            <span className="rounded-full bg-white/5 px-2 py-1 text-slate-300">ID: {event.id}</span>
          </div>
        </div>
        <p className="text-sm text-slate-200">{formatDate(event.timestamp)}</p>
      </div>
    </div>
  );
}

export default TimelineEventCard;
