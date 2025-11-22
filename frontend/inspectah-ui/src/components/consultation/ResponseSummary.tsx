interface ResponseSummaryProps {
  answer: string;
  riskFlags?: string[];
  generatedAt?: string;
}

function ResponseSummary({ answer, riskFlags, generatedAt }: ResponseSummaryProps) {
  return (
    <div className="space-y-3">
      <p className="text-base leading-relaxed text-slate-50">{answer}</p>
      {riskFlags && riskFlags.length > 0 && (
        <div className="space-y-1 rounded-lg border border-white/10 bg-white/5 p-3 text-sm text-slate-200">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-300">Sinais de atenção</p>
          <ul className="list-disc space-y-1 pl-5">
            {riskFlags.map((flag) => (
              <li key={flag}>{flag}</li>
            ))}
          </ul>
        </div>
      )}
      {generatedAt && (
        <p className="text-xs text-slate-400">Resposta gerada em {new Date(generatedAt).toLocaleString('pt-BR')}</p>
      )}
    </div>
  );
}

export default ResponseSummary;
