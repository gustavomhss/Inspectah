import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminContent, Badge, Button } from '@/ui/admin';
import { useOpsFlows } from './hooks';

interface Props {
  flowSlug?: string;
  flowVersionId?: string | null;
}

export function FlowOpsPanel({ flowSlug, flowVersionId }: Props) {
  const opsFlows = useOpsFlows();
  const navigate = useNavigate();
  const item = useMemo(() => opsFlows.find((f) => f.slug === flowSlug), [opsFlows, flowSlug]);

  if (!flowSlug) {
    return null;
  }

  return (
    <AdminContent>
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-slate-100">Ops / SLO</h4>
        {!item && (
          <div className="space-y-2">
            <p className="text-xs text-slate-200">Fluxo não encontrado no cockpit.</p>
            <Button variant="secondary" size="sm" onClick={() => navigate('/admin/ops/cockpit')}>
              Abrir painel de operações
            </Button>
          </div>
        )}
        {item && (
          <>
            <div className="flex items-center gap-2 text-sm text-slate-200">
              <span className="font-semibold">{item.slug}</span>
              <Badge tone="info">{item.domain || 'domínio'}</Badge>
              <Badge tone="success">versão atual: {item.flow_version_id || flowVersionId || '—'}</Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" size="sm" onClick={() => navigate('/admin/ops/cockpit')}>
                Abrir painel de operações
              </Button>
            </div>
            <div>
              <p className="text-xs text-slate-500">SLOs ligados:</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {(item.slos || []).map((slo) => (
                  <Badge key={slo.id} tone={slo.status === 'OK' ? 'success' : slo.status === 'DEGRADED' ? 'warning' : 'neutral'}>
                    {slo.id} · {slo.status || 'UNKNOWN'}
                  </Badge>
                ))}
                {(item.slos || []).length === 0 && <span className="text-xs text-slate-500">Nenhum SLO vinculado.</span>}
              </div>
            </div>
          </>
        )}
      </div>
    </AdminContent>
  );
}
