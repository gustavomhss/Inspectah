function RiskBadge({ risk }: { risk?: string | null }) {
  if (!risk) {
    return <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">Sem risco declarado</span>;
  }
  const normalized = risk.toLowerCase();
  const isHigh = normalized.includes('high') || normalized.includes('alto');
  const color = isHigh ? 'border-rose-400/60 bg-rose-500/15 text-rose-100' : 'border-amber-400/50 bg-amber-500/15 text-amber-100';
  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${color}`}>{risk}</span>;
}

export default RiskBadge;
