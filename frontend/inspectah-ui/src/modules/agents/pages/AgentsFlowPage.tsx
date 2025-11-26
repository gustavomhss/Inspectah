import { useMemo } from 'react';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import LoadingState from '../../admin/components/LoadingState';
import ErrorState from '../../admin/components/ErrorState';
import { useAgents } from '../hooks/useAgents';
import { useAgentsFlow } from '../hooks/useAgentsFlow';
import AgentFlowEditor from '../components/AgentFlowEditor';

export default function AgentsFlowPage() {
  const { agents, loading: loadingAgents, error: errorAgents, reload: reloadAgents } = useAgents();
  const {
    layers,
    loading: loadingFlow,
    error: errorFlow,
    reload: reloadFlow,
    addIntermediateLayer,
    removeLayer,
    updateLayerAgents,
    setMediator,
    validationErrors,
    save,
    allowedRolesForLayer,
    saving,
  } = useAgentsFlow();

  const isLoading = loadingAgents || loadingFlow;
  const error = errorAgents || errorFlow;

  const sortedLayers = useMemo(() => [...layers].sort((a, b) => a.layer_index - b.layer_index), [layers]);

  if (isLoading) return <LoadingState label="Carregando fluxo de agentes..." />;
  if (error) return <ErrorState message={error} onRetry={() => { void reloadAgents(); void reloadFlow(); }} />;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Fluxo de agentes"
        subtitle="Configure camadas fixas e intermediárias com mediador e agentes por camada."
      />
      <PageContainer>
        <AgentFlowEditor
          layers={sortedLayers}
          agents={agents}
          validationErrors={validationErrors}
          onAddIntermediate={addIntermediateLayer}
          onRemove={removeLayer}
          onChangeAgents={updateLayerAgents}
          onSetMediator={setMediator}
          onSave={save}
          allowedRolesForLayer={allowedRolesForLayer}
          saving={saving}
        />
      </PageContainer>
    </div>
  );
}
