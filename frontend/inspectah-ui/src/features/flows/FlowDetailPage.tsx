import { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AdminContent, AdminHeader, Banner, Button } from '@/ui/admin';
import { FlowCreateFromTemplateDialog } from './FlowCreateFromTemplateDialog';
import { FlowExecutionDetailDrawer } from './FlowExecutionDetailDrawer';
import { FlowOpsPanel } from './FlowOpsPanel';
import { FlowStateBadge } from './FlowStateBadge';
import { FlowVersionHistory } from './FlowVersionHistory';
import { useFlowActions, useFlowDetail, useFlowExecutions, useFlowOperations, useFlowVersions, useRollback } from './hooks';
import type { FlowExecution, FlowExecutionDetail } from './types';

export function FlowDetailPage() {
  const params = useParams();
  const navigate = useNavigate();
  const flowId = params.flowId || params.id || null;
  const isNewFlow = flowId === 'new';
  const { flow, loading, error, setFlow } = useFlowDetail(flowId);
  const { executions } = useFlowExecutions(flowId);
  const { versions } = useFlowVersions(flowId);
  const operations = useFlowOperations(flowId);
  const { updateStateAction, replaceAgentAction, deleteFlowAction, saving, deleting, error: actionError, setError } = useFlowActions(
    flowId,
    (updated) => setFlow(updated),
  );
  const { run: rollback, saving: rollbacking, error: rollbackError } = useRollback(flowId, setFlow);
  const [selectedExec, setSelectedExec] = useState<FlowExecution | null>(null);
  const [showCreateCard, setShowCreateCard] = useState(false);

  const steps = useMemo(() => flow?.steps || [], [flow]);

  if (!flowId) {
    return <Banner tone="warning" title="FlowId não informado" description="Use rota /flows/:flowId" />;
  }

  if (isNewFlow) {
    return (
      <div className="flex flex-col gap-6">
        <AdminHeader title="Criar fluxo" subtitle="Nova versão a partir de template" />
        <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900">
          <FlowCreateFromTemplateDialog
            onCreated={(createdId) => {
              navigate(`/flows/${createdId}`);
            }}
          />
          <p className="mt-2 text-sm text-slate-700">
            Preencha template, nome e slug para criar. Após criar, revise etapas, coloque em teste e promova para ativo.
          </p>
        </AdminContent>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <AdminHeader title="Fluxos" subtitle="Detalhe do fluxo e operações" />

      {loading && <p className="text-sm text-slate-600">Carregando fluxo...</p>}
      {error && <Banner tone="danger" title="Erro" description={error} />}
      {actionError && <Banner tone="danger" title="Erro de operação" description={actionError} />}
      {rollbackError && <Banner tone="danger" title="Erro de rollback" description={rollbackError} />}

      {flow && (
        <div className="space-y-5">
          <AdminContent className="bg-slate-900/80 text-white rounded-2xl border border-slate-800 shadow-lg">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-sm">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <FlowStateBadge state={flow.estado} />
                    <span className="text-sm text-white">Flow ID: {flow.id}</span>
                  </div>
                  <h3 className="text-2xl font-bold text-white">{flow.nome}</h3>
                  <p className="text-base text-white">
                    Slug: {flow.slug} · Domínio: {flow.domain || '—'} · Tipo: {flow.tipo_entrada}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button variant="secondary" onClick={() => navigate(-1)}>
                    Voltar
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={async () => {
                      if (!flowId) return;
                      try {
                        await deleteFlowAction();
                        navigate('/flows');
                      } catch (err) {
                        // erro já exibido via actionError
                      }
                    }}
                    disabled={deleting}
                  >
                    {deleting ? 'Removendo...' : 'Apagar fluxo'}
                  </Button>
                  <Button
                    onClick={() => flowId && updateStateAction({ novo_estado: 'em_teste' })}
                    disabled={saving}
                    variant="secondary"
                  >
                    Marcar em teste
                  </Button>
                  <Button onClick={() => flowId && updateStateAction({ novo_estado: 'ativo' })} disabled={saving}>
                    Ativar
                  </Button>
                </div>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                <div className="rounded-xl border border-emerald-500/40 bg-emerald-900/40 p-4">
                  <p className="text-sm font-semibold text-emerald-50 uppercase tracking-wide">Versão ativa</p>
                  <p className="text-2xl font-bold text-emerald-50">{flow.flow_version_id || '—'}</p>
                  {flow.test_version_id && <p className="text-sm text-amber-50">Teste: {flow.test_version_id}</p>}
                </div>
                <div className="rounded-xl border border-blue-500/40 bg-blue-900/40 p-4">
                  <p className="text-sm font-semibold text-blue-50 uppercase tracking-wide">Estado</p>
                  <p className="text-2xl font-bold text-blue-50 capitalize">{flow.estado}</p>
                  <p className="text-sm text-blue-50">Percentual teste: {flow.percentual_teste ?? 0}%</p>
                </div>
                <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-4">
                  <p className="text-sm font-semibold text-white uppercase tracking-wide">Execuções (últimas)</p>
                  <p className="text-2xl font-bold text-white">{executions.length}</p>
                  <p className="text-sm text-slate-100">Clique abaixo para detalhar</p>
                </div>
                <div className="rounded-xl border border-rose-500/40 bg-rose-900/40 p-4">
                  <p className="text-sm font-semibold text-rose-50 uppercase tracking-wide">Operações</p>
                  <p className="text-2xl font-bold text-rose-50">{operations.length}</p>
                  <p className="text-sm text-rose-50">Rollback, mudanças de estado, etc.</p>
                </div>
              </div>
            </div>
          </AdminContent>

          <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
            <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="text-base font-semibold text-slate-900">Etapas e agentes</h4>
                  <p className="text-sm text-slate-700">Revise a trilha de execução e ajuste bindings quando preciso.</p>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setShowCreateCard(true);
                    setTimeout(() => {
                      document.getElementById('flow-create-card')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 50);
                  }}
                >
                  Editar fluxo (nova versão)
                </Button>
              </div>
              <div className="space-y-2">
                {steps.map((step) => (
                  <div key={step.id} className="rounded border border-slate-200 p-3 hover:border-slate-300 bg-white">
                    <div className="flex justify-between">
                      <div>
                        <p className="text-base font-semibold text-slate-900">
                          {step.ordem}. {step.tipo_etapa}
                        </p>
                        <p className="text-sm text-slate-700">Papel: {step.agent_role}</p>
                        {step.agent_binding && <p className="text-sm text-slate-600">Agente: {step.agent_binding}</p>}
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

            <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3">
              <h5 className="text-base font-semibold text-slate-900 mb-1">Como editar a trilha de execução</h5>
              <ol className="list-decimal list-inside space-y-1 text-sm text-slate-700">
                <li>Use “Editar fluxo (nova versão)” para ir ao cartão de criação e gerar uma nova versão a partir de template.</li>
                <li>Revise etapas e use “Trocar agente” para ajustar bindings de cada passo.</li>
                <li>Para mudar ordem/estrutura, crie nova versão via template e ative-a (ou use rollback no histórico).</li>
                <li>Após ajustes, mantenha o fluxo em teste e promova para ativo quando validado.</li>
              </ol>
            </div>
          </AdminContent>

            <div className="flex flex-col gap-3">
              <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-base font-semibold text-slate-900">Execuções recentes</h4>
                  <span className="text-xs text-slate-700">Clique para abrir detalhes</span>
                </div>
                <div className="space-y-2">
                  {executions.map((exec) => (
                    <button
                      key={exec.id}
                      className="w-full text-left border rounded-lg p-3 hover:border-slate-400 bg-white"
                      onClick={() => setSelectedExec(exec)}
                    >
                      <div className="flex justify-between">
                        <span className="text-sm font-semibold text-slate-900">{exec.id}</span>
                        <span className="text-xs text-slate-800">{exec.status}</span>
                      </div>
                      <p className="text-sm text-slate-700">Item: {exec.item_id}</p>
                    </button>
                  ))}
                  {executions.length === 0 && <p className="text-sm text-slate-600">Nenhuma execução registrada.</p>}
                </div>
              </AdminContent>

              <div className="grid gap-3 md:grid-cols-1">
                <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-base font-semibold mb-0 text-slate-900">Painel de operações</h4>
                    <span className="text-xs text-slate-600">Acesso ao cockpit e SLOs</span>
                  </div>
                  <FlowOpsPanel flowSlug={flow.slug} flowVersionId={flow.flow_version_id} />
                </AdminContent>

                {showCreateCard && (
                  <AdminContent
                    id="flow-create-card"
                    className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900"
                  >
                    <h4 className="text-base font-semibold mb-2 text-slate-900">Criar nova versão a partir de template</h4>
                    <FlowCreateFromTemplateDialog
                      onCreated={(createdId) => {
                        navigate(`/flows/${createdId}`);
                      }}
                    />
                    <p className="mt-2 text-sm text-slate-700">
                      Dica: use o mesmo slug com sufixo de versão para duplicar este fluxo e ativá-lo após teste.
                    </p>
                  </AdminContent>
                )}
              </div>
            </div>
          </div>

          <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-base font-semibold text-slate-900">Histórico de versões e rollback</h4>
              <span className="text-xs text-slate-600">Mantém rastreabilidade e permite voltar versões</span>
            </div>
            <FlowVersionHistory
              versions={versions}
              operations={operations}
              onRollback={async (versionId) => {
                await rollback(versionId);
              }}
              rollbackDisabled={rollbacking}
            />
          </AdminContent>

          <div className="grid gap-3 md:grid-cols-2">
            <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900">
              <h4 className="text-base font-semibold mb-2 text-slate-900">Mini glossário</h4>
              <ul className="text-sm text-slate-700 space-y-1">
                <li><strong>Flow ID</strong>: identificador único do fluxo.</li>
                <li><strong>Flow Version</strong>: versão ativa/teste (`flow_version_id` / `test_version_id`).</li>
                <li><strong>Execução</strong>: processamento de um item de entrada.</li>
                <li><strong>Rollback</strong>: voltar para versão anterior, respeitando limites e políticas.</li>
              </ul>
            </AdminContent>
            <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm text-slate-900">
              <h4 className="text-base font-semibold mb-2 text-slate-900">Como usar esta tela</h4>
              <ol className="text-sm text-slate-700 space-y-1 list-decimal list-inside">
                <li>Cheque estado e versões ativas na faixa superior.</li>
                <li>Use os botões de estado para promover/colocar em teste conforme políticas.</li>
                <li>Revise etapas e bindings; troque agentes se necessário.</li>
                <li>Abra execuções recentes para confirmar resultados e itens processados.</li>
                <li>Use histórico para rollback quando permitido (limites horário/políticas).</li>
                <li>Para criar/configurar: clique “Editar fluxo (nova versão)”, crie, ajuste bindings, valide em teste e ative.</li>
                <li>Precisa monitorar saúde/SLO? No card “Painel de operações” clique em “Abrir painel de operações” para o cockpit.</li>
              </ol>
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
