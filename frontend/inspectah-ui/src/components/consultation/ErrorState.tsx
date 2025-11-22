interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-6 text-slate-50 shadow-card" role="alert">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-red-200">Algo não deu certo</p>
      <h2 className="mt-2 text-xl font-bold text-white">Não conseguimos concluir a consulta.</h2>
      <p className="mt-2 text-sm text-slate-100">{message}</p>
      <div className="mt-4 flex flex-wrap items-center gap-3 text-sm text-slate-200">
        <span>Tente ajustar a pergunta ou aguarde alguns segundos.</span>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/10 px-3 py-2 font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-200"
          >
            Tentar novamente
          </button>
        )}
      </div>
    </div>
  );
}

export default ErrorState;
