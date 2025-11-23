import RiskBadge from '../RiskBadge';
import type { AdminDebunkerSection } from '../../../types/admin';

interface Props {
  debunker: AdminDebunkerSection;
  risk?: string | null;
}

function DebunkerPanel({ debunker, risk }: Props) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Debunker</p>
          <h4 className="text-lg font-semibold text-white">Avaliação e flags</h4>
        </div>
        <RiskBadge risk={risk || debunker.risk_level} />
      </div>
      <p className="mt-2 text-sm text-slate-200">{debunker.explanation}</p>
      {debunker.flags?.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {debunker.flags.map((flag) => (
            <span key={flag} className="rounded-full bg-white/5 px-3 py-1 text-xs text-amber-100">
              {flag}
            </span>
          ))}
        </div>
      )}
      {debunker.last_evaluated_at && (
        <p className="mt-3 text-xs text-slate-300">Última avaliação: {new Date(debunker.last_evaluated_at).toLocaleString('pt-BR')}</p>
      )}
    </div>
  );
}

export default DebunkerPanel;
