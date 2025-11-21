import React, { useState } from "react";

interface FeedbackButtonProps {
  targetId: string;
  variant: "case" | "event";
}

/**
 * Botão + formulário mínimo para reportar problemas em casos/eventos.
 */
export function FeedbackButton({ targetId, variant }: FeedbackButtonProps): JSX.Element {
  const [open, setOpen] = useState(false);
  const [mensagem, setMensagem] = useState("");
  const [autor, setAutor] = useState("");
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const endpoint = variant === "case" ? `/explorer/cases/${targetId}/feedback` : `/explorer/events/${targetId}/feedback`;

  async function submitFeedback() {
    if (!mensagem.trim()) {
      setStatusMsg("Descreva o problema antes de enviar.");
      return;
    }
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem, autor }),
      });
      if (!response.ok) {
        throw new Error(`Falha ao enviar feedback (${response.status})`);
      }
      setMensagem("");
      setAutor("");
      setStatusMsg("Feedback enviado com sucesso.");
    } catch (error) {
      setStatusMsg((error as Error).message);
    }
  }

  if (!open) {
    return (
      <button type="button" className="s12-feedback-button" onClick={() => setOpen(true)}>
        Reportar problema
      </button>
    );
  }

  return (
    <div className="s12-feedback-form">
      <textarea
        placeholder="Descreva o problema encontrado"
        value={mensagem}
        onChange={(event) => setMensagem(event.target.value)}
      />
      <input placeholder="Seu nome (opcional)" value={autor} onChange={(event) => setAutor(event.target.value)} />
      <div className="actions">
        <button type="button" onClick={submitFeedback}>
          Enviar feedback
        </button>
        <button type="button" onClick={() => setOpen(false)}>
          Cancelar
        </button>
      </div>
      {statusMsg && <small className="status-message">{statusMsg}</small>}
    </div>
  );
}
