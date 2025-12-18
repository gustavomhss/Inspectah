import { useState } from 'react';

type FeedbackKind = 'errado' | 'enviesado' | 'incompleto' | 'falta_evidencia' | 'outro';
type Severity = 'low' | 'medium' | 'high' | 'blocker';

type Props = {
  targetId: string;
  targetType: 'trace' | 'decision';
  onSubmit: (payload: {
    target_id: string;
    target_type: 'trace' | 'decision';
    feedback_kind: FeedbackKind;
    severity: Severity;
    comment: string;
  }) => Promise<void>;
  disabled?: boolean;
};

export default function TraceFeedbackForm({ targetId, targetType, onSubmit, disabled }: Props) {
  const [feedbackKind, setFeedbackKind] = useState<FeedbackKind>('errado');
  const [severity, setSeverity] = useState<Severity>('medium');
  const [comment, setComment] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const submit = async () => {
    if (!comment.trim()) {
      setError('Descreva brevemente o problema.');
      return;
    }
    setError(null);
    setBusy(true);
    try {
      await onSubmit({
        target_id: targetId,
        target_type: targetType,
        feedback_kind: feedbackKind,
        severity,
        comment: comment.trim(),
      });
      setSent(true);
      setComment('');
    } catch (e) {
      setError('Falha ao enviar feedback. Tente novamente.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
      <div className="flex flex-wrap gap-3 items-center">
        <label className="space-y-1">
          <span className="block text-xs uppercase tracking-[0.2em] text-slate-400">Tipo</span>
          <select
            className="rounded bg-white/10 px-2 py-1 text-white"
            value={feedbackKind}
            onChange={(e) => setFeedbackKind(e.target.value as FeedbackKind)}
            disabled={busy || disabled}
          >
            <option value="errado">Raciocínio errado</option>
            <option value="enviesado">Enviesado</option>
            <option value="incompleto">Incompleto</option>
            <option value="falta_evidencia">Falta evidência</option>
            <option value="outro">Outro</option>
          </select>
        </label>

        <label className="space-y-1">
          <span className="block text-xs uppercase tracking-[0.2em] text-slate-400">Severidade</span>
          <select
            className="rounded bg-white/10 px-2 py-1 text-white"
            value={severity}
            onChange={(e) => setSeverity(e.target.value as Severity)}
            disabled={busy || disabled}
          >
            <option value="low">Baixa</option>
            <option value="medium">Média</option>
            <option value="high">Alta</option>
            <option value="blocker">Crítica</option>
          </select>
        </label>
      </div>

      <div className="mt-3 space-y-1">
        <span className="block text-xs uppercase tracking-[0.2em] text-slate-400">Comentário</span>
        <textarea
          className="w-full rounded bg-white/5 px-3 py-2 text-white"
          rows={3}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Explique o erro, viés ou falta de evidência"
          disabled={busy || disabled}
        />
      </div>

      {error && <p className="mt-2 text-red-400 text-xs">{error}</p>}
      {sent && <p className="mt-2 text-green-400 text-xs">Feedback registrado.</p>}

      <div className="mt-3 flex justify-end">
        <button
          className="rounded bg-sky-600 px-4 py-2 text-white hover:bg-sky-500 disabled:opacity-50"
          onClick={submit}
          disabled={busy || disabled}
        >
          Enviar feedback
        </button>
      </div>
    </div>
  );
}
