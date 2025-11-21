import React from "react";
import { FeedbackButton } from "./FeedbackButton";

export interface TimelineEventView {
  id_evento: string;
  timestamp: string;
  titulo: string;
  status_debunker: "aceito" | "incerto" | "suspeito" | string;
  resumo: string;
  tipo_evento: string;
  fonte: string;
  rationale?: string;
}

interface TimelineProps {
  events: TimelineEventView[];
}

/**
 * Renderiza timeline em ordem cronológica simples.
 */
export function Timeline({ events }: TimelineProps): JSX.Element {
  if (!events || events.length === 0) {
    return <p>Nenhum evento registrado para este caso ainda.</p>;
  }

  return (
    <ol className="s12-timeline">
      {events.map((event) => (
        <li key={event.id_evento} className={`timeline-item status-${event.status_debunker}`}>
          <header>
            <span className="timestamp">{new Date(event.timestamp).toLocaleString()}</span>
            <span className="status">{event.status_debunker.toUpperCase()}</span>
          </header>
          <strong>{event.titulo}</strong>
          <p>{event.resumo}</p>
          <small>
            Fonte: {event.fonte} · Tipo: {event.tipo_evento}
            {event.rationale ? ` · Racional: ${event.rationale}` : ""}
          </small>
          <FeedbackButton targetId={event.id_evento} variant="event" />
        </li>
      ))}
    </ol>
  );
}
