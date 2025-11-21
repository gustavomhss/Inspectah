import React, { useEffect, useState } from "react";

interface FeedbackEntry {
  id_feedback: string;
  target_type: string;
  target_id: string;
  mensagem: string;
  status: string;
  autor?: string | null;
  created_at: string;
  updated_at: string;
}

interface FeedbackResponse {
  status: string;
  items: FeedbackEntry[];
}

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`Falha ao chamar ${url}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export function FeedbackListPage(): JSX.Element {
  const [statusFilter, setStatusFilter] = useState("novo");
  const [items, setItems] = useState<FeedbackEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadFeedbacks(filter: string) {
    try {
      setLoading(true);
      setError(null);
      const payload = await fetchJSON<FeedbackResponse>(`/admin/feedback?status=${filter}`);
      setItems(payload.items);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadFeedbacks(statusFilter).catch(() => null);
  }, [statusFilter]);

  async function updateStatus(feedbackId: string, nextStatus: string) {
    try {
      await fetchJSON(`/admin/feedback/${feedbackId}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus }),
      });
      loadFeedbacks(statusFilter).catch(() => null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <section className="feedback-admin">
      <h2>Fila de feedbacks (Sprint 12)</h2>
      <label>
        Status:
        <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="novo">Novo</option>
          <option value="em_analise">Em análise</option>
          <option value="resolvido">Resolvido</option>
          <option value="todos">Todos</option>
        </select>
      </label>
      {loading && <p>Carregando feedbacks...</p>}
      {error && <p className="error">{error}</p>}
      <ul className="feedback-list">
        {items.map((item) => (
          <li key={item.id_feedback}>
            <header>
              <strong>{item.target_type.toUpperCase()}</strong> → {item.target_id}
            </header>
            <p>{item.mensagem}</p>
            <small>
              Status atual: {item.status} · Criado em {new Date(item.created_at).toLocaleString()} · Autor: {item.autor || "N/D"}
            </small>
            <div className="actions">
              {item.status !== "novo" && (
                <button type="button" onClick={() => updateStatus(item.id_feedback, "novo")}>
                  Marcar como novo
                </button>
              )}
              {item.status !== "em_analise" && (
                <button type="button" onClick={() => updateStatus(item.id_feedback, "em_analise")}>
                  Em análise
                </button>
              )}
              {item.status !== "resolvido" && (
                <button type="button" onClick={() => updateStatus(item.id_feedback, "resolvido")}>
                  Resolver
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
