import type { AdminCommitteesSection } from '../../../../core/api/api-types';

function CommitteesPanel({ committees }: { committees: AdminCommitteesSection }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Comitês</p>
      <h4 className="text-lg font-semibold text-white">Decisões e divergências</h4>
      <p className="mt-2 text-sm text-slate-200">{committees.summary}</p>
      <div className="mt-3 space-y-2">
        {committees.decisions.length === 0 && (
          <p className="text-sm text-slate-300">Nenhuma decisão detalhada disponível.</p>
        )}
        {committees.decisions.map((decision) => (
          <div key={`${decision.name}-${decision.decided_at || decision.verdict}`} className="rounded-xl border border-white/5 bg-white/5 p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-semibold text-white">{decision.name}</p>
              <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-200">
                {decision.verdict} {decision.confidence ? `• conf ${decision.confidence}` : ''}
              </span>
            </div>
            {decision.rationale && <p className="mt-2 text-sm text-slate-200">{decision.rationale}</p>}
            {decision.decided_at && (
              <p className="mt-2 text-xs text-slate-300">
                Decidido em {new Date(decision.decided_at).toLocaleString('pt-BR')}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default CommitteesPanel;
