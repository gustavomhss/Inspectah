function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-6 text-center text-slate-200">
      <p className="text-lg font-semibold text-white">{title}</p>
      {description && <p className="mt-2 text-sm text-slate-300">{description}</p>}
    </div>
  );
}

export default EmptyState;
