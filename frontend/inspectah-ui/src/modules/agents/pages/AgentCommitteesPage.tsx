import { useMemo, useState } from 'react';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Button from '../../../shared/components/Button';
import LoadingState from '../../admin/components/LoadingState';
import ErrorState from '../../admin/components/ErrorState';
import type { AgentLayer, AgentStatus } from '../../../core/api/api-types';
import { useAgents } from '../hooks/useAgents';
import { useCommittees } from '../hooks/useCommittees';

export default function AgentCommitteesPage() {
  const [layerFilter, setLayerFilter] = useState<AgentLayer | 'all'>('all');
  const { agents } = useAgents({});
  const { committees, loading, error, reload, createCommittee } = useCommittees(layerFilter === 'all' ? undefined : layerFilter);
  const [payload, setPayload] = useState({
    name: '',
    description: '',
    layer: 'interpretation' as AgentLayer,
    primary_agents: [] as string[],
    mediator_agent: '',
    status: 'active' as AgentStatus,
  });
  const [feedback, setFeedback] = useState<string | null>(null);
  const availableAgents = useMemo(() => agents.filter((a) => (layerFilter === 'all' ? true : a.layer === layerFilter)), [agents, layerFilter]);

  const handleCreate = async () => {
    if (!payload.name || payload.primary_agents.length !== 2 || !payload.mediator_agent) {
      setFeedback('Selecione dois debunkers e um mediador');
      return;
    }
    try {
      const created = await createCommittee({
        ...payload,
        policy: { required_agreement_ratio: 0.67, max_disagreement_tolerance: 0.34, resolve_ties_strategy: 'favor_cautious' },
      });
      setFeedback(`Comitê ${created.name} criado`);
      setPayload((prev) => ({ ...prev, name: '', primary_agents: [], mediator_agent: '' }));
    } catch (err) {
      setFeedback((err as Error).message);
    }
  };

  if (loading) return <LoadingState label="Carregando comitês..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;

  return (
    <div className="space-y-4">
      <PageHeader title="Comitês de Agentes" subtitle="Tripla redundância: Debunker A, Debunker B e Mediador." />
      <PageContainer>
        <div className="flex flex-wrap items-center gap-3">
          <select
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
            value={layerFilter}
            onChange={(e) => setLayerFilter(e.target.value as AgentLayer | 'all')}
          >
            <option value="all">Todas as camadas</option>
            <option value="interpretation">Interpretação</option>
            <option value="classification">Classificação</option>
            <option value="debunk">Debunk</option>
          </select>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border border-white/10 bg-white/5 p-4 lg:col-span-2">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">Comitês</p>
            {committees.length === 0 && <p className="pt-2 text-sm text-slate-200">Nenhum comitê configurado.</p>}
            <div className="mt-3 space-y-3">
              {committees.map((c) => (
                <div key={c.id} className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-white">{c.name}</p>
                      <p className="text-xs text-slate-300">{c.description || 'Sem descrição'}</p>
                    </div>
                    <span className="text-xs text-slate-200">{c.layer}</span>
                  </div>
                  <div className="mt-2 grid gap-2 text-sm text-slate-200 md:grid-cols-3">
                    <div>
                      <p className="text-xs uppercase text-slate-400">Debunker A</p>
                      <p>{c.primary_agents[0]}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase text-slate-400">Debunker B</p>
                      <p>{c.primary_agents[1]}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase text-slate-400">Mediador</p>
                      <p>{c.mediator_agent}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">Novo comitê</p>
            <div className="mt-3 space-y-2">
              <input
                className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                placeholder="Nome do comitê"
                value={payload.name}
                onChange={(e) => setPayload((prev) => ({ ...prev, name: e.target.value }))}
              />
              <textarea
                className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                placeholder="Descrição"
                value={payload.description}
                onChange={(e) => setPayload((prev) => ({ ...prev, description: e.target.value }))}
              />
              <select
                className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                value={payload.layer}
                onChange={(e) => setPayload((prev) => ({ ...prev, layer: e.target.value as AgentLayer }))}
              >
                <option value="interpretation">Interpretação</option>
                <option value="classification">Classificação</option>
                <option value="debunk">Debunk</option>
              </select>
              <div className="space-y-1 text-sm text-slate-200">
                <label className="text-xs uppercase text-slate-400">Debunker A</label>
                <select
                  className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                  value={payload.primary_agents[0] || ''}
                  onChange={(e) =>
                    setPayload((prev) => ({ ...prev, primary_agents: [e.target.value, prev.primary_agents[1] || ''] }))
                  }
                >
                  <option value="">Selecione</option>
                  {availableAgents.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name}
                    </option>
                  ))}
                </select>
                <label className="text-xs uppercase text-slate-400">Debunker B</label>
                <select
                  className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                  value={payload.primary_agents[1] || ''}
                  onChange={(e) =>
                    setPayload((prev) => ({ ...prev, primary_agents: [prev.primary_agents[0] || '', e.target.value] }))
                  }
                >
                  <option value="">Selecione</option>
                  {availableAgents.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name}
                    </option>
                  ))}
                </select>
                <label className="text-xs uppercase text-slate-400">Mediador</label>
                <select
                  className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                  value={payload.mediator_agent}
                  onChange={(e) => setPayload((prev) => ({ ...prev, mediator_agent: e.target.value }))}
                >
                  <option value="">Selecione</option>
                  {availableAgents.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name}
                    </option>
                  ))}
                </select>
              </div>
              <Button variant="primary" onClick={handleCreate}>
                Criar comitê
              </Button>
              {feedback && <p className="text-xs text-slate-200">{feedback}</p>}
            </div>
          </div>
        </div>
      </PageContainer>
    </div>
  );
}
