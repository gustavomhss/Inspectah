import { FormEvent, useState } from 'react';
import type { ConsultationStatus } from '../../types/inspectah';

interface ConsultationFormProps {
  status: ConsultationStatus;
  onSubmit: (question: string) => Promise<void> | void;
}

const exampleQuestions = [
  'O projeto X realmente foi aprovado na última sessão?',
  'Há indícios confiáveis de atraso no cronograma Y?',
  'Qual o risco associado ao anúncio recente sobre o caso Z?',
];

function ConsultationForm({ status, onSubmit }: ConsultationFormProps) {
  const [question, setQuestion] = useState('');
  const isSubmitting = status.kind === 'submitting';

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit(question);
  };

  return (
    <form onSubmit={handleSubmit} aria-label="Formulário de consulta" className="space-y-4">
      <div className="flex flex-col gap-2">
        <label htmlFor="question" className="text-sm font-semibold text-white">
          Pergunta em linguagem natural
        </label>
        <p className="text-xs text-slate-200">
          Seja direto sobre o fato, evento ou caso. O Inspectah cruza fontes, indica o nível de risco e destaca evidências principais.
        </p>
        <textarea
          id="question"
          name="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ex.: O contrato da obra Y foi suspenso pelo tribunal?"
          className="min-h-[96px] w-full resize-none rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-base text-white shadow-inner transition focus:border-sky-300 focus:bg-white/10"
          required
          aria-required="true"
          disabled={isSubmitting}
        />
      </div>
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="text-xs text-slate-300">
          <p className="font-semibold text-slate-100">Exemplos rápidos:</p>
          <ul className="mt-1 flex flex-wrap gap-2" aria-label="Sugestões de perguntas">
            {exampleQuestions.map((example) => (
              <li key={example}>
                <button
                  type="button"
                  onClick={() => setQuestion(example)}
                  className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] text-slate-100 transition hover:border-sky-400 hover:text-white"
                >
                  {example}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div className="flex items-center gap-3 self-start md:self-center">
          <span className="text-xs text-slate-200">Pressione Enter ou clique em &ldquo;Consultar&rdquo;</span>
          <button
            type="submit"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-500 px-4 py-2 text-sm font-semibold text-white shadow-card transition hover:bg-sky-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-200 disabled:cursor-not-allowed disabled:bg-slate-500"
            disabled={isSubmitting}
            aria-busy={isSubmitting}
          >
            {isSubmitting ? 'Consultando…' : 'Consultar'}
          </button>
        </div>
      </div>
    </form>
  );
}

export default ConsultationForm;
