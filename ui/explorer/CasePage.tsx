import React, { useEffect, useState } from "react";
import { Timeline, TimelineEventView } from "./components/Timeline";
import { FeedbackButton } from "./components/FeedbackButton";

interface CaseDetailResponse {
  case: {
    id_caso: string;
    dominio: string;
    titulo: string;
    descricao: string;
    status: string;
    metadata?: Record<string, unknown>;
  };
  timeline: TimelineEventView[];
  stats: { events: number; by_status: Record<string, number> };
}

interface CasePageProps {
  caseId: string;
  onClose?: () => void;
}

export function CasePage({ caseId, onClose }: CasePageProps): JSX.Element {
  const [data, setData] = useState<CaseDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function loadCase() {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`/explorer/cases/${caseId}`);
        if (!response.ok) {
          throw new Error(`Falha ao carregar caso ${caseId}`);
        }
        const payload = (await response.json()) as CaseDetailResponse;
        if (!cancelled) {
          setData(payload);
        }
      } catch (err) {
        if (!cancelled) {
          setError((err as Error).message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    loadCase().catch(() => null);
    return () => {
      cancelled = true;
    };
  }, [caseId]);

  if (loading) {
    return <p>Carregando caso...</p>;
  }

  if (error) {
    return (
      <div>
        <p className="error">{error}</p>
        {onClose && (
          <button type="button" onClick={onClose}>
            Voltar
          </button>
        )}
      </div>
    );
  }

  if (!data) {
    return <p>Selecione um caso.</p>;
  }

  const { case: caseInfo, timeline, stats } = data;

  return (
    <article className="case-detail">
      <header>
        {onClose && (
          <button type="button" className="link" onClick={onClose}>
            ← Voltar para lista
          </button>
        )}
        <h2>{caseInfo.titulo}</h2>
        <p>{caseInfo.descricao}</p>
        <p>
          Domínio: {caseInfo.dominio} · Status geral: {caseInfo.status} · Eventos: {stats.events}
        </p>
        <FeedbackButton targetId={caseInfo.id_caso} variant="case" />
      </header>
      <section>
        <h3>Timeline</h3>
        <Timeline events={timeline} />
      </section>
    </article>
  );
}
