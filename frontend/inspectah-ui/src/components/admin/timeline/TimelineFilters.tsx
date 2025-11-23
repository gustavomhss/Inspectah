interface Props {
  availableTypes: string[];
  selectedType: string;
  selectedSeverity: string;
  onChange: (filters: { type: string; severity: string }) => void;
}

function TimelineFilters({ availableTypes, selectedType, selectedSeverity, onChange }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-white/5 bg-white/5 p-4 shadow-card">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Tipo de evento</p>
        <select
          className="mt-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
          value={selectedType}
          onChange={(event) => onChange({ type: event.target.value, severity: selectedSeverity })}
        >
          <option value="all">Todos</option>
          {availableTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Severidade</p>
        <select
          className="mt-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
          value={selectedSeverity}
          onChange={(event) => onChange({ type: selectedType, severity: event.target.value })}
        >
          <option value="all">Todas</option>
          <option value="critical">Crítica</option>
          <option value="warning">Atenção</option>
          <option value="info">Informativa</option>
        </select>
      </div>
    </div>
  );
}

export default TimelineFilters;
