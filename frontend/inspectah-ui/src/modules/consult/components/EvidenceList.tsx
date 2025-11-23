import type { EvidenceItemUi } from '../../../core/api/api-types';

interface EvidenceListProps {
  evidences: EvidenceItemUi[];
}

function EvidenceList({ evidences }: EvidenceListProps) {
  if (!evidences.length) {
    return (
      <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-6 text-slate-200 shadow-card">
        <p className="text-sm font-semibold text-white">Evidências principais</p>
        <p className="mt-2 text-sm text-slate-300">Não há evidências suficientes para exibir neste caso.</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-white">Evidências principais</p>
        <p className="text-xs text-slate-300">Mostrando {Math.min(evidences.length, 5)} de {evidences.length}</p>
      </div>
      <ul className="mt-4 space-y-3" aria-label="Lista de evidências">
        {evidences.slice(0, 5).map((evidence) => (
          <li key={evidence.id} className="rounded-xl border border-white/5 bg-white/5 p-4">
            <div className="flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-semibold text-white">{evidence.sourceName}</p>
                <p className="text-xs uppercase tracking-wide text-slate-300">{evidence.sourceType}</p>
              </div>
              {evidence.credibility && (
                <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-200">{evidence.credibility}</span>
              )}
            </div>
            <p className="mt-2 text-sm leading-relaxed text-slate-200">{evidence.description}</p>
            {evidence.link && (
              <a
                href={evidence.link}
                target="_blank"
                rel="noreferrer"
                className="mt-2 inline-flex items-center gap-2 text-sm font-semibold text-sky-300 underline-offset-4 hover:underline"
              >
                Ver fonte
                <span aria-hidden="true">↗</span>
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default EvidenceList;
