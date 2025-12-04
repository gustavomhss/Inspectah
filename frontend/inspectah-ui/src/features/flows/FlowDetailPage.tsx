import { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AdminContent, AdminHeader, Banner, Button } from '@/ui/admin';
import { FlowCreateFromTemplateDialog } from './FlowCreateFromTemplateDialog';
import { FlowExecutionDetailDrawer } from './FlowExecutionDetailDrawer';
import { FlowStateBadge } from './FlowStateBadge';
import { useFlowActions, useFlowDetail, useFlowExecutions } from './hooks';
import type { FlowExecution, FlowExecutionDetail } from './types';

export function FlowDetailPage() {
  const params = useParams();
  const navigate = useNavigate();
  const flowId = params.flowId || params.id || null;
  const { flow, loading, error, setFlow } = useFlowDetail(flowId);
  const { executions } = useFlowExecutions(flowId);
  const { updateStateAction, replaceAgentAction, saving, error: actionError } = useFlowActions(
    flowId,
    (updated) => setFlow(updated),
  );
  const [selectedExec, setSelectedExec] = useState<FlowExecution | null>(null);

  const steps = useMemo(() => flow?.steps || [], [flow]);

  if (!flowId) {
    return <Banner tone="warning" title="FlowId não informado" description="Use rota /flows/:flowId" />;
  }

  return (
    <div className="flex flex-col gap-4">
      <AdminHeader
        title={flow?.nome || 'Fluxo'}
        subtitle={flow?.slug || ''}
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => navigate(-1)}>
              Voltar
            </Button>
            <Button
              onClick={() => {
                if (!flowId) return;
                void updateStateAction({ novo_estado: 'em_teste' });
              }}
              disabled={saving}
            >
              Marcar em teste
            </Button>
            <Button
              onClick={() => {
                if (!flowId) return;
                void updateStateAction({ novo_estado: 'ativo' });
              }}
              disabled={saving}
            >
              Ativar
            </Button>
          </div>
        }
      />

      {loading && <p className="text-sm text-slate-600">Carregando fluxo...</p>}
      {error && <Banner tone="danger" title="Erro" description={error} />}
      {actionError && <Banner tone="danger" title="Erro de operação" description={actionError} />}

      {flow && (
        <div className="grid gap-4 md:grid-cols-[1fr_360px]">
          <AdminContent>
            <div className="flex items-center gap-2 mb-3">
              <FlowStateBadge state={flow.estado} />
              <span className="text-sm text-slate-600">Tipo de entrada: {flow.tipo_entrada}</span>
            </div>
            <h4 className="text-sm font-semibold mb-2">Etapas</h4>
            <div className="space-y-2">
              {steps.map((step) => (
                <div key={step.id} className="rounded border border-slate-200 p-2">
                  <div className="flex justify-between">
                    <div>
                      <p className="text-sm font-semibold">
                        {step.ordem}. {step.tipo_etapa}
                      </p>
                      <p className="text-xs text-slate-600">Papel: {step.agent_role}</p>
                      {step.agent_binding && <p className="text-xs text-slate-500">Agente: {step.agent_binding}</p>}
                    </div>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() =>
                        void replaceAgentAction({ step_id: step.id, agent_binding: `${step.agent_role}_novo` }).catch(() => undefined)
                      }
                    >
                      Trocar agente
                    </Button>
                  </div>
                </div>
              ))}
              {steps.length === 0 && <p className="text-sm text-slate-500">Nenhuma etapa cadastrada.</p>}
            </div>
          </AdminContent>

          <div className="flex flex-col gap-3">
            <AdminContent>
              <h4 className="text-sm font-semibold mb-2">Execuções recentes</h4>
              <div className="space-y-2">
                {executions.map((exec) => (
                  <button
                    key={exec.id}
                    className="w-full text-left border rounded p-2 hover:border-slate-400"
                    onClick={() => setSelectedExec(exec)}
                  >
                    <div className="flex justify-between">
                      <span className="text-sm font-semibold">{exec.id}</span>
                      <span className="text-xs text-slate-600">{exec.status}</span>
                    </div>
                    <p className="text-xs text-slate-500">Item: {exec.item_id}</p>
                  </button>
                ))}
                {executions.length === 0 && <p className="text-xs text-slate-500">Nenhuma execução registrada.</p>}
              </div>
            </AdminContent>

            <AdminContent>
              <FlowCreateFromTemplateDialog
                onCreated={(createdId) => {
                  navigate(`/flows/${createdId}`);
                }}
              />
            </AdminContent>
          </div>
        </div>
      )}

      {selectedExec && (
        <FlowExecutionDetailDrawer
          execution={{ ...selectedExec, steps: [] } as FlowExecutionDetail}
          onClose={() => setSelectedExec(null)}
        />
      )}
    </div>
  );
}

export default FlowDetailPage;
