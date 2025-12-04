import { useEffect, useMemo, useState } from 'react';
import PageContainer from '@/shared/layout/PageContainer';
import PageHeader from '@/shared/layout/PageHeader';
import LoadingState from '@/modules/admin/components/LoadingState';
import ErrorState from '@/modules/admin/components/ErrorState';
import { useAgentFlowsList, useSaveAgentFlow } from './agentFlowsHooks';
import type { AgentFlowConfig, AgentFlowConfigForm } from './agentFlowsTypes';
import AgentFlowEditor from './components/AgentFlowEditor';
import AgentFlowList from './components/AgentFlowList';

export default function AgentFlowsPage() {
  const { items, loading, error, reload } = useAgentFlowsList();
  const { save, saving, error: saveError, setError: setSaveError } = useSaveAgentFlow(onSaved);
  const [selected, setSelected] = useState<AgentFlowConfig | null>(null);

  const fallbackFlow: AgentFlowConfigForm = useMemo(
    () => ({
      domain_key: '',
      name: '',
      description: '',
      is_active: true,
      change_reason: '',
      steps: [],
    }),
    [],
  );

  useEffect(() => {
    if (!selected && items.length > 0) {
      setSelected(items[0]);
    }
  }, [items, selected]);

  function onSaved(flow: AgentFlowConfig) {
    void reload();
    setSelected(flow);
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
        subtitle="Configure a ordem linear de agentes por domínio. Toda mudança precisa de justificativa e respeita invariantes."
      />
      <PageContainer>
        <div className="flex flex-col gap-6 lg:flex-row">
          <div className="w-full lg:w-5/12">
            <AgentFlowList
              flows={items}
              selectedId={selected?.id || null}
              onSelect={(flow) => setSelected(flow)}
              onCreateNew={() => setSelected(null)}
            />
          </div>
          <div className="w-full lg:w-7/12">
            <AgentFlowEditor
              key={selected?.id || 'new-flow'}
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
