import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLogger } from '../../../app/providers/LoggerProvider';
import type { AgentLayer, AgentRole, AgentStatus } from '../../../core/api/api-types';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Button from '../../../shared/components/Button';
import LoadingState from '../../admin/components/LoadingState';
import ErrorState from '../../admin/components/ErrorState';
import EmptyState from '../../admin/components/EmptyState';
import { useAgents } from '../hooks/useAgents';

const roleLabels: Record<AgentRole, string> = {
  interpreter: 'Interpreter',
  classifier: 'Classifier',
  analyst: 'Analyst',
  debunker: 'Debunker',
  decision_maker: 'Decision Maker',
  librarian: 'Librarian',
};

const layerLabels: Record<AgentLayer, string> = {
  interpretation: 'Interpretação',
  classification: 'Classificação',
  debunk: 'Debunk',
};

export default function AgentsListPage() {
  const { logEvent } = useLogger();
  const [layerFilter, setLayerFilter] = useState<AgentLayer | 'all'>('all');
  const [roleFilter, setRoleFilter] = useState<AgentRole | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<AgentStatus | 'all'>('all');
  const { agents, loading, error, reload, createAgent } = useAgents({
    layer: layerFilter === 'all' ? undefined : layerFilter,
    role: roleFilter === 'all' ? undefined : roleFilter,
    status: statusFilter === 'all' ? undefined : statusFilter,
  });
  const [createName, setCreateName] = useState('');
  const [createRole, setCreateRole] = useState<AgentRole>('debunker');
  const [createLayer, setCreateLayer] = useState<AgentLayer>('interpretation');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const filtered = useMemo(() => {
    return agents.filter((agent) => {
      if (layerFilter !== 'all' && agent.layer !== layerFilter) return false;
      if (roleFilter !== 'all' && agent.role !== roleFilter) return false;
      if (statusFilter !== 'all' && agent.status !== statusFilter) return false;
      return true;
    });
  }, [agents, layerFilter, roleFilter, statusFilter]);

  const handleCreate = async () => {
    if (!createName.trim()) {
      setFeedback('Preencha um nome para criar o agente');
      return;
    }
    try {
      setSaving(true);
      setFeedback(null);
      const created = await createAgent({
        name: createName.trim(),
        description: '',
        instructions: '',
        role: createRole,
        layer: createLayer,
        status: 'active',
        kb_refs: [],
      });
      setCreateName('');
      logEvent('admin.agent_created', { id: created.id, role: created.role, layer: created.layer });
      setFeedback('Agente criado com sucesso');
    } catch (err) {
      setFeedback((err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingState label="Carregando agentes..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Agentes & Comitês"
        subtitle="Configure agentes com redundância tripla e visualize suas camadas."
      />
      <PageContainer>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Filtros</p>
            <div className="flex flex-wrap gap-2 pt-2 text-sm text-slate-200">
              <select
                className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                value={layerFilter}
                onChange={(e) => setLayerFilter(e.target.value as AgentLayer | 'all')}
              >
                <option value="all">Camadas: Todas</option>
                <option value="interpretation">Interpretação</option>
                <option value="classification">Classificação</option>
                <option value="debunk">Debunk</option>
              </select>
              <select
                className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value as AgentRole | 'all')}
              >
                <option value="all">Papéis: Todos</option>
                <option value="interpreter">Interpreter</option>
                <option value="classifier">Classifier</option>
                <option value="analyst">Analyst</option>
                <option value="debunker">Debunker</option>
                <option value="decision_maker">Decision Maker</option>
                <option value="librarian">Librarian</option>
              </select>
              <select
                className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as AgentStatus | 'all')}
              >
                <option value="all">Status: Todos</option>
                <option value="active">Ativo</option>
                <option value="paused">Pausado</option>
                <option value="deprecated">Legado</option>
              </select>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              placeholder="Nome do novo agente"
              value={createName}
              onChange={(e) => setCreateName(e.target.value)}
            />
            <select
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={createRole}
              onChange={(e) => setCreateRole(e.target.value as AgentRole)}
            >
              <option value="debunker">Debunker</option>
              <option value="interpreter">Interpreter</option>
              <option value="classifier">Classifier</option>
              <option value="analyst">Analyst</option>
              <option value="decision_maker">Decision Maker</option>
              <option value="librarian">Librarian</option>
            </select>
            <select
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={createLayer}
              onChange={(e) => setCreateLayer(e.target.value as AgentLayer)}
            >
              <option value="interpretation">Interpretação</option>
              <option value="classification">Classificação</option>
              <option value="debunk">Debunk</option>
            </select>
            <Button variant="primary" disabled={saving} onClick={handleCreate}>
              {saving ? 'Salvando...' : 'Novo agente'}
            </Button>
          </div>
        </div>
        {feedback && <p className="mt-2 text-sm text-slate-200">{feedback}</p>}

        <div className="mt-4 space-y-2">
          {filtered.length === 0 ? (
            <EmptyState title="Nenhum agente" description="Crie novos agentes ou ajuste os filtros aplicados." />
          ) : (
            <div className="overflow-hidden rounded-xl border border-white/10">
              <table className="min-w-full divide-y divide-white/10">
                <thead className="bg-white/5 text-left text-xs uppercase tracking-wide text-slate-300">
                  <tr>
                    <th className="px-4 py-3">Nome</th>
                    <th className="px-4 py-3">Camada</th>
                    <th className="px-4 py-3">Papel</th>
                    <th className="px-4 py-3">Modelo</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 bg-white/2 text-sm">
                  {filtered.map((agent) => (
                    <tr key={agent.id}>
                      <td className="px-4 py-3 font-semibold text-white">{agent.name}</td>
                      <td className="px-4 py-3 text-slate-200">{layerLabels[agent.layer]}</td>
                      <td className="px-4 py-3 text-slate-200">{roleLabels[agent.role]}</td>
                      <td className="px-4 py-3 text-slate-200">{agent.model_name || agent.recommended_model_name || 'default'}</td>
                      <td className="px-4 py-3 text-slate-200">{agent.status}</td>
                      <td className="px-4 py-3">
                        <Link
                          to={`/admin/agents/${encodeURIComponent(agent.id)}`}
                          className="text-sm font-semibold text-sky-200 hover:text-white"
                        >
                          Ver detalhes
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </PageContainer>
    </div>
  );
}
