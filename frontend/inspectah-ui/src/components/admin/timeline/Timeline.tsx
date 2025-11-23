import EmptyState from '../EmptyState';
import type { AdminTimelineEvent } from '../../../types/admin';
import TimelineEventCard from './TimelineEventCard';

function Timeline({ events }: { events: AdminTimelineEvent[] }) {
  if (!events || events.length === 0) {
    return <EmptyState title="Nenhum evento" description="Não encontramos eventos para este recorte." />;
  }

  return (
    <div className="relative space-y-4 border-l-2 border-white/10 pl-4">
      {events.map((event) => (
        <TimelineEventCard key={event.id} event={event} />
      ))}
    </div>
  );
}

export default Timeline;
