import { Badge, Banner, Button, Table } from '@/ui/admin';
import type { Source } from '../types/Source';
import { SourceStatusBadge } from './SourceStatusBadge';

interface SourcesTableProps {
  sources: Source[];
  onSelect?: (source: Source) => void;
}

export function SourcesTable({ sources, onSelect }: SourcesTableProps) {
  const isEmpty = sources.length === 0;

  return (
    <Table
      headers={['Fonte', 'Tipo', 'Estado', 'Endpoint', 'Ações']}
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
            <div className="text-xs text-slate-300">{source.endpoint || source.url_base || '—'}</div>
            {source.category && <div className="text-[11px] uppercase text-slate-500">{source.category}</div>}
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
