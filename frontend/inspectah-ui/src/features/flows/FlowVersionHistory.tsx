import { AdminContent, Badge, Button } from '@/ui/admin';
import type { FlowOperation, FlowVersion } from './types';

interface Props {
  versions: FlowVersion[];
  operations: FlowOperation[];
  onRollback: (versionId: string) => Promise<void> | void;
  rollbackDisabled?: boolean;
}

export function FlowVersionHistory({ versions, operations, onRollback, rollbackDisabled }: Props) {
  return (
    <AdminContent>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold">Histórico de versões</h3>
            <p className="text-xs text-slate-400">Versionamento do fluxo e operações recentes.</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h4 className="text-sm font-semibold mb-1">Versões</h4>
            {versions.length === 0 && <p className="text-xs text-slate-500">Nenhuma versão registrada.</p>}
            <div className="flex flex-col gap-2">
              {versions.map((v) => (
                <div key={v.id} className="border border-slate-700 rounded p-3 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-slate-100">{v.version_id}</p>
                    <p className="text-xs text-slate-400">Template: {v.template_slug}</p>
                    <p className="text-xs text-slate-500">Estado: {v.estado}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge tone="info">{v.created_at ? new Date(v.created_at).toLocaleString() : '—'}</Badge>
                    <Button size="sm" variant="secondary" disabled={rollbackDisabled} onClick={() => void onRollback(v.version_id)}>
                      Rollback
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold mb-1">Operações recentes</h4>
            {operations.length === 0 && <p className="text-xs text-slate-500">Nenhuma operação registrada.</p>}
            <div className="space-y-1">
              {operations.map((op) => (
                <div key={op.id} className="border border-slate-700 rounded p-2">
                  <div className="flex justify-between">
                    <span className="text-xs font-semibold text-slate-100">{op.operacao}</span>
                    <span className="text-xs text-slate-500">{op.created_at ?? ''}</span>
                  </div>
                  <p className="text-xs text-slate-400">Versão: {op.flow_version_id || '—'}</p>
                  <p className="text-[11px] text-slate-500 break-words">Resultado: {op.resultado}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AdminContent>
  );
}
