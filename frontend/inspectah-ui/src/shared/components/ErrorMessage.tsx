interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

function ErrorMessage({ title = 'Algo deu errado', message, onRetry }: ErrorMessageProps) {
  return (
    <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-50 shadow-card">
      <p className="text-base font-semibold">{title}</p>
      <p className="mt-1 text-rose-100">{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 inline-flex items-center gap-2 rounded-md bg-white/10 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-rose-200"
        >
          Tentar novamente
        </button>
      ) : null}
    </div>
  );
}

export default ErrorMessage;
