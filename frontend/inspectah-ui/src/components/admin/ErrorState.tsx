interface Props {
  message?: string;
  onRetry?: () => void;
}

function ErrorState({ message, onRetry }: Props) {
  return (
    <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-rose-50 shadow-card">
      <p className="font-semibold">Não foi possível carregar os dados de admin.</p>
      <p className="mt-1 text-sm opacity-80">{message || 'Tente novamente ou verifique o backend.'}</p>
      {onRetry && (
        <button
          type="button"
          className="mt-3 rounded-md border border-rose-300/40 bg-rose-500/20 px-3 py-2 text-sm font-semibold text-rose-50 hover:bg-rose-500/30"
          onClick={onRetry}
        >
          Tentar novamente
        </button>
      )}
    </div>
  );
}

export default ErrorState;
