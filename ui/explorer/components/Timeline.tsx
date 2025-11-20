import React from "react";

export interface TimelineEventView {
  id: string;
  timestamp: string;
  title: string;
  status: "aceito" | "incerto" | "suspeito";
  source: string;
}

/**
 * Timeline visualization placeholder. Receives normalized events from the
 * backend and renders a simple list until the final UI lands in Wave 3.
 */
export function Timeline({ events }: { events: TimelineEventView[] }): JSX.Element {
  return (
    <div className="s12-timeline">
      {events.length === 0 ? (
        <p>Nenhum evento carregado ainda.</p>
      ) : (
        <ul>
          {events.map((evt) => (
            <li key={evt.id}>
              <strong>{evt.timestamp}</strong> — {evt.title} ({evt.status})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
