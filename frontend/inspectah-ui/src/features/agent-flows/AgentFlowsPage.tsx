import { useEffect, useMemo, useState } from 'react';
import PageContainer from '@/shared/layout/PageContainer';
import PageHeader from '@/shared/layout/PageHeader';
import LoadingState from '@/modules/admin/components/LoadingState';
import ErrorState from '@/modules/admin/components/ErrorState';
import { Toast } from '@/ui/admin/components/Toast';
import { useToast } from '@/ui/admin/hooks';
import { useAgentFlowsList, useSaveAgentFlow } from './agentFlowsHooks';
import type { AgentFlowConfig, AgentFlowConfigForm } from './agentFlowsTypes';
import AgentFlowEditor from './components/AgentFlowEditor';
import AgentFlowList from './components/AgentFlowList';

export default function AgentFlowsPage() {
  const { items, loading, error, reload } = useAgentFlowsList();
  const { save, saving, error: saveError, setError: setSaveError } = useSaveAgentFlow(onSaved);
  const [selected, setSelected] = useState<AgentFlowConfig | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);
  const { toasts, pushToast, dismissToast, clear } = useToast();

  const fallbackFlow: AgentFlowConfigForm = useMemo(
    () => ({
      domain_key: '',
      name: '',
      description: '',
      is_active: true,
      change_reason: '',
      steps: [
        { position: 1, agent_role: 'interpreter', params: { strict_mode: true } },
        { position: 2, agent_role: 'classifier', params: { threshold: 0.5 } },
        { position: 3, agent_role: 'decision_maker', params: { threshold: 0.7 } },
      ],
    }),
    [],
  );

  useEffect(() => {
    if (!selected && items.length > 0 && !creatingNew) {
      setSelected(items[0]);
    }
  }, [items, selected, creatingNew]);

  function onSaved(flow: AgentFlowConfig) {
    void reload();
    setCreatingNew(false);
    setSelected(flow);
    pushToast({
      title: 'Fluxo salvo',
      description: `Fluxo ${flow.name || flow.domain_key} salvo com sucesso`,
      variant: 'success',
    });
  }

  const handleSave = async (form: AgentFlowConfigForm) => {
    await save(form);
  };

  if (loading) return <LoadingState label="Carregando fluxos de agentes..." />;
  if (error) return <ErrorState message={error} onRetry={() => void reload()} />;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Fluxos de agentes por domínio"
        subtitle="Configure a ordem linear de agentes por domínio. Toda mudança precisa de justificativa e respeita invariantes. Selecione agentes reais e mantenha Decision Maker como última etapa."
      />
      {toasts.length ? (
        <div className="fixed right-4 top-20 z-[90] space-y-2">
          {toasts.map((toast) => (
            <Toast
              key={toast.id}
              title={toast.title}
              description={toast.description}
              variant={toast.variant}
              onClose={() => dismissToast(toast.id)}
            />
          ))}
        </div>
      ) : null}
      <PageContainer>
        <div className="flex flex-col gap-6 lg:flex-row">
          <div className="w-full lg:w-5/12">
            <AgentFlowList
              flows={items}
              selectedId={selected?.id || (creatingNew ? 'new' : null)}
              onSelect={(flow) => {
                setCreatingNew(false);
                setSelected(flow);
                clear();
              }}
              onCreateNew={() => {
                setCreatingNew(true);
                setSelected(null);
                clear();
              }}
            />
          </div>
          <div className="w-full lg:w-7/12">
            <AgentFlowEditor
              key={selected?.id || (creatingNew ? 'new-flow' : 'existing-flow')}
              initialFlow={selected || fallbackFlow}
              onSave={handleSave}
              saving={saving}
              error={saveError}
              clearError={() => setSaveError(null)}
            />
          </div>
        </div>
      </PageContainer>
    </div>
  );
}
