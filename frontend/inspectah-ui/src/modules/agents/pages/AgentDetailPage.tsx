import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useLogger } from '../../../app/providers/LoggerProvider';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Button from '../../../shared/components/Button';
import LoadingState from '../../admin/components/LoadingState';
import ErrorState from '../../admin/components/ErrorState';
import type { AgentProfile } from '../../../core/api/api-types';
import { useAgentDetail } from '../hooks/useAgentDetail';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-2 rounded-xl border border-white/5 bg-white/5 p-4">
      <span className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">{label}</span>
      {children}
    </label>
  );
}

export default function AgentDetailPage() {
  const params = useParams<{ agentId: string }>();
  const agentId = params.agentId!;
  const { agent, versions, loading, error, reload, saveAgent, addVersion } = useAgentDetail(agentId);
  const { logEvent } = useLogger();
  const [draft, setDraft] = useState<Partial<AgentProfile>>({});
  const [feedback, setFeedback] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [newVersionNote, setNewVersionNote] = useState('Ajuste de diretrizes');

  if (loading) return <LoadingState label="Carregando agente..." />;
  if (error || !agent) return <ErrorState message={error || 'Agente não encontrado'} onRetry={reload} />;

  const handleSave = async () => {
    try {
      setSaving(true);
      setFeedback(null);
      const updated = await saveAgent(draft);
      setDraft({});
      setFeedback('Agente atualizado');
      logEvent('admin.agent_saved', { id: updated.id, role: updated.role, layer: updated.layer });
    } catch (err) {
      setFeedback((err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const handleNewVersion = async () => {
    try {
      const version = await addVersion({ changelog: newVersionNote, instructions: draft.instructions || agent.instructions });
      setFeedback(`Versão ${version.version_number} registrada`);
      setNewVersionNote('Ajuste de diretrizes');
    } catch (err) {
      setFeedback((err as Error).message);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader title={agent.name} subtitle="Perfil do agente e ajustes de diretrizes/modelo." />
      <PageContainer>
        <div className="grid gap-4 lg:grid-cols-2">
          <Field label="Nome">
            <input
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              defaultValue={agent.name}
              onChange={(e) => setDraft((prev) => ({ ...prev, name: e.target.value }))}
            />
          </Field>
          <Field label="Descrição">
            <textarea
              className="min-h-[80px] rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              defaultValue={agent.description}
              onChange={(e) => setDraft((prev) => ({ ...prev, description: e.target.value }))}
            />
          </Field>
          <Field label="Instruções">
            <textarea
              className="min-h-[140px] rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              defaultValue={agent.instructions}
              onChange={(e) => setDraft((prev) => ({ ...prev, instructions: e.target.value }))}
            />
          </Field>
          <Field label="Modelo recomendado">
            <input
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              defaultValue={agent.recommended_model_name || ''}
              onChange={(e) => setDraft((prev) => ({ ...prev, recommended_model_name: e.target.value }))}
            />
            <p className="text-xs text-slate-300">Padrão: modelo mais atual do plano Plus.</p>
          </Field>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <Button variant="primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Salvando...' : 'Salvar alterações'}
          </Button>
          <Button variant="secondary" onClick={handleNewVersion}>
            Registrar nova versão
          </Button>
          {feedback && <span className="text-sm text-slate-200">{feedback}</span>}
        </div>

        <div className="mt-8 rounded-xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">Histórico de versões</p>
          <ul className="mt-2 space-y-2 text-sm text-slate-100">
            {versions.length === 0 && <li className="text-slate-300">Nenhuma versão registrada.</li>}
            {versions.map((ver) => (
              <li key={ver.id} className="rounded-lg border border-white/10 bg-white/5 px-3 py-2">
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span>Versão {ver.version_number}</span>
                  <span>{new Date(ver.created_at).toLocaleString()}</span>
                </div>
                <p className="font-semibold text-white">{ver.changelog}</p>
                {ver.instructions && <p className="text-sm text-slate-200">{ver.instructions.slice(0, 160)}...</p>}
              </li>
            ))}
          </ul>
        </div>
      </PageContainer>
    </div>
  );
}
