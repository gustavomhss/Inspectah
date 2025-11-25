import type { AdminSourceType, IngestionStatus } from '../../../core/api/api-types';

interface Props {
  types: AdminSourceType[];
  selectedType: AdminSourceType | 'all';
  onTypeChange: (value: AdminSourceType | 'all') => void;
  statusFilter: 'all' | IngestionStatus | 'NEVER' | 'RUNNING';
  onStatusChange: (value: 'all' | IngestionStatus | 'NEVER' | 'RUNNING') => void;
  search: string;
  onSearchChange: (value: string) => void;
}

function IngestionFiltersBar({ types, selectedType, onTypeChange, statusFilter, onStatusChange, search, onSearchChange }: Props) {
  const uniqueTypes = Array.from(new Set(types));
  return (
    <div className="flex flex-wrap items-center gap-3">
      <select
        aria-label="Filtrar por tipo"
        className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
        value={selectedType}
        onChange={(ev) => onTypeChange(ev.target.value as AdminSourceType | 'all')}
      >
        <option value="all">Tipo: Todos</option>
        {uniqueTypes.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>

      <select
        aria-label="Filtrar por status"
        className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
        value={statusFilter}
        onChange={(ev) => onStatusChange(ev.target.value as Props['statusFilter'])}
      >
        <option value="all">Status: Todos</option>
        <option value="SUCCESS">Saudáveis</option>
        <option value="FAIL">Falhando</option>
        <option value="RUNNING">Em andamento</option>
        <option value="NEVER">Nunca rodou</option>
      </select>

      <input
        aria-label="Buscar por nome"
        className="w-56 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-slate-400"
        placeholder="Buscar fonte..."
        value={search}
        onChange={(ev) => onSearchChange(ev.target.value)}
      />
    </div>
  );
}

export default IngestionFiltersBar;
