import { useEffect, useState } from 'react';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Button from '../../../shared/components/Button';
import LoadingState from '../../admin/components/LoadingState';
import ErrorState from '../../admin/components/ErrorState';
import { useModelPolicy } from '../hooks/useModelPolicy';

export default function ModelPolicyPage() {
  const { policy, loading, error, reload, save } = useModelPolicy();
  const [buffer, setBuffer] = useState<number>(15);
  const [autoUpgrade, setAutoUpgrade] = useState<boolean>(true);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    if (policy) {
      setBuffer(policy.adoption_delay_days);
      setAutoUpgrade(policy.auto_upgrade_enabled);
    }
  }, [policy]);

  if (loading) return <LoadingState label="Carregando política de modelos..." />;
  if (error || !policy) return <ErrorState message={error || 'Política não encontrada'} onRetry={reload} />;

  const handleSave = async () => {
    try {
      const updated = await save({ adoption_delay_days: buffer, auto_upgrade_enabled: autoUpgrade });
      setFeedback(`Política atualizada (buffer ${updated.adoption_delay_days} dias)`);
    } catch (err) {
      setFeedback((err as Error).message);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Política global de modelos"
        subtitle="Controle de rollout/buffer para adotar novas versões do modelo com transparência."
      />
      <PageContainer>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">Status atual</p>
            <ul className="mt-2 text-sm text-slate-200">
              <li>Modelo padrão: {policy.global_default_model}</li>
              <li>Auto-upgrade: {policy.auto_upgrade_enabled ? 'Ativo' : 'Desativado'}</li>
              <li>Buffer (dias): {policy.adoption_delay_days}</li>
              {policy.next_upgrade_at && <li>Próximo upgrade: {policy.next_upgrade_at}</li>}
            </ul>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">Atualizar</p>
            <div className="mt-3 space-y-2 text-sm text-white">
              <label className="flex items-center gap-2 text-slate-200">
                <input
                  type="checkbox"
                  checked={autoUpgrade}
                  onChange={(e) => setAutoUpgrade(e.target.checked)}
                  className="h-4 w-4 rounded border-white/20 bg-white/5"
                />
                Ativar auto-upgrade do modelo mais recente
              </label>
              <label className="flex flex-col gap-1 text-slate-200">
                Buffer (dias)
                <input
                  type="number"
                  value={buffer}
                  onChange={(e) => setBuffer(Number(e.target.value))}
                  className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                />
              </label>
              <Button variant="primary" onClick={handleSave}>
                Salvar política
              </Button>
              {feedback && <p className="text-xs text-slate-200">{feedback}</p>}
            </div>
          </div>
        </div>
      </PageContainer>
    </div>
  );
}
