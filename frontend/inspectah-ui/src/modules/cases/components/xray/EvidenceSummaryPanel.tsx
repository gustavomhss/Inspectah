import type { AdminEvidenceSection } from '../../../../core/api/api-types';

function EvidenceSummaryPanel({ evidences }: { evidences: AdminEvidenceSection }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Evidências</p>
      <h4 className="text-lg font-semibold text-white">Principais evidências</h4>
      <p className="mt-2 text-sm text-slate-200">{evidences.summary}</p>
      <div className="mt-3 space-y-2">
        {evidences.evidences.length === 0 && <p className="text-sm text-slate-300">Nenhuma evidência listada.</p>}
        {evidences.evidences.map((evidence) => (
          <div key={evidence.id} className="rounded-xl border border-white/5 bg-white/5 p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-semibold text-white">{evidence.title || evidence.id}</p>
              <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-200">
                {evidence.type} {evidence.source ? `• ${evidence.source}` : ''}
              </span>
            </div>
            {evidence.snippet && <p className="mt-2 text-sm text-slate-200">{evidence.snippet}</p>}
            {evidence.captured_at && (
              <p className="mt-2 text-xs text-slate-300">
                Coletada em {new Date(evidence.captured_at).toLocaleString('pt-BR')}
              </p>
            )}
            {evidence.url && (
              <a className="mt-2 inline-block text-xs font-semibold text-sky-200 hover:underline" href={evidence.url}>
                Abrir evidência
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default EvidenceSummaryPanel;
