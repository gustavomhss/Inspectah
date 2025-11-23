import type { AdminAnchorsSection } from '../../../../core/api/api-types';

const statusColor: Record<string, string> = {
  healthy: 'bg-emerald-500/20 text-emerald-100 border border-emerald-500/30',
  degraded: 'bg-amber-400/20 text-amber-100 border border-amber-400/30',
  failed: 'bg-rose-500/20 text-rose-100 border border-rose-500/30',
};

function AnchorsPanel({ anchors }: { anchors: AdminAnchorsSection }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Âncoras</p>
      <h4 className="text-lg font-semibold text-white">Estado das âncoras</h4>
      <p className="mt-2 text-sm text-slate-200">{anchors.summary}</p>
      <div className="mt-3 space-y-2">
        {anchors.anchors.length === 0 && <p className="text-sm text-slate-300">Sem dados de âncoras.</p>}
        {anchors.anchors.map((anchor) => {
          const className = statusColor[anchor.status] || 'bg-white/5 text-slate-100 border border-white/10';
          return (
            <div key={`${anchor.name}-${anchor.status}`} className="rounded-xl border border-white/5 bg-white/5 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-white">{anchor.name}</p>
                <span className={`rounded-full px-3 py-1 text-xs ${className}`}>{anchor.status}</span>
              </div>
              {anchor.reliability && <p className="mt-1 text-xs text-slate-300">Confiança: {anchor.reliability}</p>}
              {anchor.issues?.length > 0 && (
                <ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-200">
                  {anchor.issues.map((issue) => (
                    <li key={issue}>{issue}</li>
                  ))}
                </ul>
              )}
              {anchor.last_check && (
                <p className="mt-2 text-xs text-slate-300">
                  Última checagem: {new Date(anchor.last_check).toLocaleString('pt-BR')}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AnchorsPanel;
