import { Badge, Banner, Button, Table } from '@/ui/admin';
import type { Source } from '../types/Source';
import { SourceStatusBadge } from './SourceStatusBadge';
import { SourceHealthBadge } from './SourceHealthBadge';

interface SourcesTableProps {
  sources: Source[];
  onSelect?: (source: Source) => void;
}

export function SourcesTable({ sources, onSelect }: SourcesTableProps) {
  const isEmpty = sources.length === 0;

  return (
    <Table
      headers={['Fonte', 'Tipo', 'Estado', 'Saúde', 'Último run', 'Ações']}
      isEmpty={isEmpty}
      emptyState={
        <div className="flex flex-col gap-2">
          <Banner tone="info" title="Nenhuma fonte cadastrada" description="Use o botão acima para criar uma nova fonte." />
        </div>
      }
    >
      {sources.map((source) => (
        <tr key={source.id} className="hover:bg-slate-900/40">
          <td className="px-4 py-3">
            <div className="font-semibold text-white">{source.name}</div>
            {source.description && <div className="text-xs text-slate-400">{source.description}</div>}
          </td>
          <td className="px-4 py-3">
            <Badge tone="neutral">{source.type}</Badge>
          </td>
          <td className="px-4 py-3">
            <SourceStatusBadge status={source.state} />
          </td>
          <td className="px-4 py-3">
            <div className="flex flex-col gap-1">
              <SourceHealthBadge status={source.health_status || (source as Source & { last_health_status?: string }).last_health_status} />
              {source.health_reason && <div className="text-[11px] text-slate-400">{source.health_reason}</div>}
            </div>
          </td>
          <td className="px-4 py-3">
            <div className="text-xs text-slate-300">{source.endpoint || source.url_base || '—'}</div>
            {source.category && <div className="text-[11px] uppercase text-slate-500">{source.category}</div>}
            {source.last_run_status && (
              <div className="text-[11px] text-slate-400">
                {source.last_run_status} — {source.last_run_items ?? 0} itens — {source.last_run_latency_ms ?? 0} ms
              </div>
            )}
          </td>
          <td className="px-4 py-3">
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={() => onSelect?.(source)}>
                Detalhes
              </Button>
            </div>
          </td>
        </tr>
      ))}
    </Table>
  );
}
