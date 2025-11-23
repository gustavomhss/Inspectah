function LoadingState({ label }: { label?: string }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card" role="status" aria-live="polite">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-3 w-32 animate-pulse rounded bg-white/10" />
          <div className="h-4 w-56 animate-pulse rounded bg-white/10" />
        </div>
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-white/20 border-t-white/80" />
      </div>
      {label && <p className="mt-4 text-sm text-slate-200">{label}</p>}
    </div>
  );
}

export default LoadingState;
