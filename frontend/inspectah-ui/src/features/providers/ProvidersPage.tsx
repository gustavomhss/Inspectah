import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import PageContainer from '@/shared/layout/PageContainer';
import PageHeader from '@/shared/layout/PageHeader';
import LoadingState from '@/modules/admin/components/LoadingState';
import ErrorState from '@/modules/admin/components/ErrorState';
import { Toast } from '@/ui/admin/components/Toast';
import { useToast } from '@/ui/admin/hooks';
import { useProvidersList, useProviderDetail, useSaveProfile, useSaveProvider, useRunProfile } from './providersHooks';
import type { IngestionProfile, Provider } from './providersTypes';

const PROVIDER_HELP = 'Perfis de fonte representam integrações externas (news/social). Mantenha limites e status coerentes antes de ativar perfis.';
const PROFILE_HELP =
  'Perfis definem filtros e budgets. Só ative perfis com budgets e escopo claros. Use "Rodar agora" para testar ingestão.';

function buildEmptyProvider(): Provider {
  return {
    id: '',
    name: '',
    kind: 'news_provider',
    description: '',
    status: 'inactive',
    limits: {},
  };
}

function buildEmptyProfile(providerId: string): IngestionProfile {
  return {
    id: '',
    provider_id: providerId,
    name: '',
    slug: '',
    kind: 'news',
    country: '',
    language: '',
    categories: [],
    keywords: [],
    filters: {},
    frequency_minutes: 60,
    budget_daily_calls: 10,
    budget_monthly_calls: 200,
    enabled: true,
    status: 'inactive',
    metadata: {},
  };
}

export default function ProvidersPage() {
  const params = useParams();
  const { providers, loading, error, reload } = useProvidersList();
  const [selectedProviderId, setSelectedProviderId] = useState<string | null>(null);
  const { detail, loading: loadingDetail, error: detailError, reload: reloadDetail } = useProviderDetail(
    selectedProviderId,
  );
  const { save: saveProvider, saving: savingProvider, error: providerError, setError: setProviderError } = useSaveProvider(
    (p, isNew) => {
      setSelectedProviderId(p.id);
      if (isNew) {
        setProviderForm(buildEmptyProvider());
      }
      void reload();
      void reloadDetail();
    },
  );
  const {
    save: saveProfile,
    saving: savingProfile,
    error: profileError,
    setError: setProfileError,
  } = useSaveProfile(async (_profile, isNew) => {
    if (isNew) {
      setProfileForm(null);
    }
    await reloadDetail();
    await reload();
  });
  const { run, running, error: runError, setError: setRunError } = useRunProfile(() => void reload());
  const { toasts, pushToast, dismissToast, clear } = useToast();

  const [providerForm, setProviderForm] = useState<Provider>(buildEmptyProvider());
  const [profileForm, setProfileForm] = useState<IngestionProfile | null>(null);
  const [search, setSearch] = useState('');
  const providerNameId = 'provider-name';
  const providerTypeId = 'provider-type';
  const providerStatusId = 'provider-status';
  const providerDescriptionId = 'provider-description';
  const profileFieldId = {
    name: 'profile-name',
    slug: 'profile-slug',
    kind: 'profile-kind',
    language: 'profile-language',
    country: 'profile-country',
    frequency: 'profile-frequency',
    budgetDaily: 'profile-budget-daily',
    budgetMonthly: 'profile-budget-monthly',
    status: 'profile-status',
    keywords: 'profile-keywords',
    enabled: 'profile-enabled',
  };

  useEffect(() => {
    if (params.providerId) {
      setSelectedProviderId(params.providerId);
    }
  }, [params.providerId]);

  useEffect(() => {
    if (!selectedProviderId && providers.length) {
      setSelectedProviderId(providers[0].id);
    }
  }, [providers, selectedProviderId]);

  useEffect(() => {
    if (detail) {
      setProfileForm(null);
    }
  }, [detail]);

  const filteredProviders = useMemo(() => {
    if (!search) return providers;
    return providers.filter((p) => p.name.toLowerCase().includes(search.toLowerCase()) || p.id.includes(search));
  }, [providers, search]);

  const handleProviderSubmit = async (evt: React.FormEvent) => {
    evt.preventDefault();
    try {
      const isNew = !providerForm.id;
      const payload = isNew
        ? { ...providerForm, id: providerForm.name.toLowerCase().replace(/\s+/g, '-').slice(0, 40) }
        : providerForm;
      const saved = await saveProvider(payload, isNew);
      pushToast({ title: 'Provider salvo', description: `Provider ${saved.name} salvo com sucesso`, variant: 'success' });
      setProviderForm(buildEmptyProvider());
    } catch (err) {
      pushToast({ title: 'Erro ao salvar provider', description: (err as Error).message, variant: 'danger' });
    }
  };

  const handleProfileSubmit = async (evt: React.FormEvent) => {
    evt.preventDefault();
    if (!profileForm) return;
    try {
      const isNew = !profileForm.id;
      const payload = isNew
        ? { ...profileForm, id: `${profileForm.slug || profileForm.name}`.toLowerCase().replace(/\s+/g, '-') }
        : profileForm;
      const saved = await saveProfile(payload, isNew);
      pushToast({ title: 'Perfil salvo', description: `Perfil ${saved.name} salvo`, variant: 'success' });
      setProfileForm(null);
    } catch (err) {
      pushToast({ title: 'Erro ao salvar perfil', description: (err as Error).message, variant: 'danger' });
    }
  };

  const handleToggleProviderStatus = async (provider: Provider) => {
    const nextStatus = provider.status === 'active' ? 'inactive' : 'active';
    try {
      const updated = await saveProvider({ ...provider, status: nextStatus }, false);
      pushToast({
        title: 'Status atualizado',
        description: `${updated.name} agora está ${updated.status}`,
        variant: 'success',
      });
      void reload();
      void reloadDetail();
    } catch (err) {
      pushToast({ title: 'Erro ao alternar status', description: (err as Error).message, variant: 'danger' });
    }
  };

  const handleRun = async (profileId: string) => {
    try {
      const result = await run(profileId, 3);
      pushToast({
        title: 'Execução enviada',
        description: `Run ${result.run_id} retornou ${result.persisted} items`,
        variant: 'success',
      });
    } catch (err) {
      pushToast({ title: 'Falha ao rodar perfil', description: (err as Error).message, variant: 'danger' });
    }
  };

  if (loading) return <LoadingState label="Carregando providers..." />;
  if (error) return <ErrorState message={error} onRetry={() => void reload()} />;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Perfis de Fonte"
        subtitle="Modele fontes externas e perfis de ingestão com budgets claros. Use as ajudas para entender cada parâmetro."
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
        <div className="grid gap-6 lg:grid-cols-12">
          <div className="lg:col-span-4 space-y-4">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between gap-2">
                <h3 className="text-lg font-semibold text-white">Perfis e fontes</h3>
                <span className="text-xs text-slate-300">{PROVIDER_HELP}</span>
              </div>
              <input
                className="mt-3 w-full rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-sm text-white placeholder:text-slate-400"
                placeholder="Buscar provider por nome ou ID"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <div className="mt-3 space-y-2">
                {filteredProviders.map((provider) => (
                  <div
                    key={provider.id}
                    role="button"
                    tabIndex={0}
                    onClick={() => {
                      clear();
                      setSelectedProviderId(provider.id);
                      setProviderForm({ ...provider });
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        clear();
                        setSelectedProviderId(provider.id);
                        setProviderForm({ ...provider });
                      }
                    }}
                    className={`w-full rounded-lg border px-3 py-3 text-left transition ${
                      provider.id === selectedProviderId
                        ? 'border-sky-400 bg-sky-500/20 text-white'
                        : 'border-white/10 bg-white/5 text-slate-100 hover:border-sky-300/60'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold">{provider.name}</p>
                        <p className="text-xs text-slate-300">{provider.description || 'Sem descrição'}</p>
                      </div>
                      <span className="rounded-full bg-white/10 px-2 py-1 text-[11px] uppercase tracking-wide text-slate-200">
                        {provider.kind === 'news_provider' ? 'News' : 'Social'}
                      </span>
                    </div>
                    <p className="mt-1 text-[11px] uppercase text-slate-300">
                      Status: <span className="font-semibold text-white">{provider.status}</span>
                    </p>
                    <div className="mt-2 flex flex-wrap gap-2 text-xs">
                      <button
                        type="button"
                        className="rounded-md border border-white/15 px-3 py-1 font-semibold text-white hover:border-sky-400"
                        onClick={(e) => {
                          e.stopPropagation();
                          setProviderForm({ ...provider });
                        }}
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        className="rounded-md border border-white/15 px-3 py-1 font-semibold text-white hover:border-amber-300/70"
                        onClick={(e) => {
                          e.stopPropagation();
                          void handleToggleProviderStatus(provider);
                        }}
                      >
                        {provider.status === 'active' ? 'Desativar' : 'Ativar'}
                      </button>
                    </div>
                  </div>
                ))}
                {!filteredProviders.length && (
                  <p className="text-sm text-slate-300">Nenhum provider encontrado. Cadastre abaixo.</p>
                )}
              </div>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <h4 className="text-lg font-semibold text-white">
                {providerForm.id ? 'Editar provider' : 'Novo provider'}
              </h4>
              {providerError ? <p className="text-sm text-rose-300">{providerError}</p> : null}
              <form className="mt-3 space-y-3" onSubmit={handleProviderSubmit}>
                <div>
                  <label className="text-sm font-semibold text-slate-100" htmlFor={providerNameId}>
                    Nome
                  </label>
                  <input
                    id={providerNameId}
                    className="mt-1 w-full rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-sm text-white"
                    value={providerForm.name}
                    required
                    onChange={(e) => setProviderForm((p) => ({ ...p, name: e.target.value }))}
                    placeholder="Ex.: NewsAPI piloto"
                  />
                  <p className="text-xs text-slate-400">Use um nome claro para o operador entender a origem.</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm font-semibold text-slate-100" htmlFor={providerTypeId}>
                      Tipo
                    </label>
                    <select
                      id={providerTypeId}
                      className="mt-1 w-full rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-sm text-white"
                      value={providerForm.kind}
                      onChange={(e) =>
                        setProviderForm((p) => ({ ...p, kind: e.target.value as Provider['kind'] }))
                      }
                    >
                      <option value="news_provider">News</option>
                      <option value="social_provider">Social</option>
                    </select>
                    <p className="text-xs text-slate-400">Escolha o domínio para carregar perfis coerentes.</p>
                  </div>
                  <div>
                    <label className="text-sm font-semibold text-slate-100" htmlFor={providerStatusId}>
                      Status
                    </label>
                    <select
                      id={providerStatusId}
                      className="mt-1 w-full rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-sm text-white"
                      value={providerForm.status}
                      onChange={(e) =>
                        setProviderForm((p) => ({ ...p, status: e.target.value as Provider['status'] }))
                      }
                    >
                      <option value="active">Ativo</option>
                      <option value="inactive">Inativo</option>
                      <option value="paused">Pausado</option>
                    </select>
                    <p className="text-xs text-slate-400">Ative somente quando tiver perfis e budgets definidos.</p>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-semibold text-slate-100" htmlFor={providerDescriptionId}>
                    Descrição
                  </label>
                  <textarea
                    id={providerDescriptionId}
                    className="mt-1 w-full rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-sm text-white"
                    rows={3}
                    value={providerForm.description}
                    onChange={(e) => setProviderForm((p) => ({ ...p, description: e.target.value }))}
                    placeholder="Propósito, limites e observações."
                  />
                </div>
                <button
                  type="submit"
                  disabled={savingProvider}
                  className="w-full rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:opacity-60"
                >
                  {savingProvider ? 'Salvando...' : 'Salvar provider'}
                </button>
              </form>
            </div>
          </div>

          <div className="lg:col-span-8 space-y-4">
            {loadingDetail && <LoadingState label="Carregando detalhes..." />}
            {detailError && <ErrorState message={detailError} onRetry={() => void reload()} />}
            {detail && (
              <div className="space-y-4">
                <div className="rounded-xl border border-white/10 bg-white/5 p-5">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Provider ativo</p>
                      <h3 className="text-xl font-bold text-white">{detail.provider.name}</h3>
                      <p className="text-sm text-slate-300">{detail.provider.description || 'Sem descrição'}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-300">Tipo</p>
                      <p className="font-semibold text-white">{detail.provider.kind}</p>
                      <p className="text-xs text-slate-300">Status</p>
                      <p className="font-semibold text-white">{detail.provider.status}</p>
                    </div>
                  </div>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/5 p-5">
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Perfis deste provider</p>
                      <h4 className="text-lg font-semibold text-white">Perfis e budgets</h4>
                      <p className="text-sm text-slate-300">{PROFILE_HELP}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setProfileForm(buildEmptyProfile(detail.provider.id))}
                      className="rounded-lg bg-sky-500 px-3 py-2 text-sm font-semibold text-white transition hover:bg-sky-400"
                    >
                      Novo perfil
                    </button>
                  </div>

                  <div className="mt-3 space-y-2">
                    {detail.profiles.map(({ profile, metrics, last_run }) => (
                      <div
                        key={profile.id}
                        className="rounded-lg border border-white/10 bg-slate-800/80 px-3 py-3 text-sm text-slate-100"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-base font-semibold text-white">{profile.name}</p>
                            <p className="text-xs text-slate-300">
                              {profile.slug} • {profile.kind} • {profile.language || 'idioma?'} / {profile.country || 'país?'}
                            </p>
                            <p className="text-xs text-slate-400">
                              Budget diário: {profile.budget_daily_calls || 0} • Budget mensal: {profile.budget_monthly_calls || 0}
                            </p>
                          </div>
                          <div className="text-right text-xs text-slate-200">
                            <p>Status: {profile.status}</p>
                            <p>Runs: {metrics.total_runs} (ok {metrics.success} / falha {metrics.fail})</p>
                            <p>Última: {metrics.last_run_at || '—'}</p>
                          </div>
                        </div>
                        <div className="mt-2 flex flex-wrap items-center gap-2">
                          <button
                            type="button"
                            onClick={() => setProfileForm(profile)}
                            className="rounded-md border border-white/10 px-3 py-1 text-xs font-semibold text-white hover:border-sky-400"
                          >
                            Editar
                          </button>
                          <button
                            type="button"
                            onClick={() => void handleRun(profile.id)}
                            className="rounded-md bg-emerald-500 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-400 disabled:opacity-60"
                            disabled={running}
                          >
                            {running ? 'Rodando...' : 'Rodar agora'}
                          </button>
                          {last_run ? (
                            <span className="rounded-md bg-white/5 px-2 py-1 text-[11px] text-slate-200">
                              Último run: {last_run.status} • {last_run.persisted} itens
                            </span>
                          ) : (
                            <span className="rounded-md bg-white/5 px-2 py-1 text-[11px] text-slate-200">Sem execuções ainda</span>
                          )}
                        </div>
                      </div>
                    ))}
                    {!detail.profiles.length && (
                      <p className="text-sm text-slate-300">Nenhum perfil cadastrado para este provider.</p>
                    )}
                  </div>
                </div>

                {profileForm && (
                  <div className="rounded-xl border border-sky-400/60 bg-slate-800/70 p-5">
                    <div className="flex items-center justify-between">
                      <h4 className="text-lg font-semibold text-white">
                        {profileForm.id ? 'Editar perfil' : 'Novo perfil'} — {detail.provider.name}
                      </h4>
                      <button
                        type="button"
                        onClick={() => setProfileForm(null)}
                        className="text-sm font-semibold text-slate-200 underline underline-offset-4"
                      >
                        Fechar
                      </button>
                    </div>
                    {profileError ? <p className="text-sm text-rose-300">{profileError}</p> : null}
                    <form className="mt-3 space-y-3" onSubmit={handleProfileSubmit}>
                      <div className="grid gap-3 md:grid-cols-2">
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.name}>
                            Nome
                          </label>
                          <input
                            id={profileFieldId.name}
                            required
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.name}
                            onChange={(e) => setProfileForm((p) => p && { ...p, name: e.target.value })}
                            placeholder="Perfil regional (ex.: BR/PT gov)"
                          />
                          <p className="text-xs text-slate-400">Nome para operadores reconhecerem o filtro.</p>
                        </div>
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.slug}>
                            Slug
                          </label>
                          <input
                            id={profileFieldId.slug}
                            required
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.slug}
                            onChange={(e) => setProfileForm((p) => p && { ...p, slug: e.target.value })}
                            placeholder="news-br-pt-gov"
                          />
                          <p className="text-xs text-slate-400">Slug estável para jobs e evidências.</p>
                        </div>
                      </div>
                      <div className="grid gap-3 md:grid-cols-3">
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.kind}>
                            Tipo
                          </label>
                          <select
                            id={profileFieldId.kind}
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.kind}
                            onChange={(e) =>
                              setProfileForm((p) => p && { ...p, kind: e.target.value as IngestionProfile['kind'] })
                            }
                          >
                            <option value="news">News</option>
                            <option value="social">Social</option>
                          </select>
                          <p className="text-xs text-slate-400">Escolha o tipo para roteamento correto.</p>
                        </div>
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.language}>
                            Idioma
                          </label>
                          <input
                            id={profileFieldId.language}
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.language || ''}
                            onChange={(e) => setProfileForm((p) => p && { ...p, language: e.target.value })}
                            placeholder="pt"
                          />
                          <p className="text-xs text-slate-400">Ajuda a calibrar filtros e dedupe.</p>
                        </div>
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.country}>
                            País
                          </label>
                          <input
                            id={profileFieldId.country}
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.country || ''}
                            onChange={(e) => setProfileForm((p) => p && { ...p, country: e.target.value })}
                            placeholder="BR"
                          />
                          <p className="text-xs text-slate-400">Usado para segmentar a coleta.</p>
                        </div>
                      </div>
                      <div className="grid gap-3 md:grid-cols-3">
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.frequency}>
                            Frequência (min)
                          </label>
                          <input
                            id={profileFieldId.frequency}
                            type="number"
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.frequency_minutes}
                            onChange={(e) =>
                              setProfileForm((p) => p && { ...p, frequency_minutes: Number(e.target.value) })
                            }
                            min={5}
                          />
                          <p className="text-xs text-slate-400">Tempo mínimo entre execuções.</p>
                        </div>
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.budgetDaily}>
                            Budget diário
                          </label>
                          <input
                            id={profileFieldId.budgetDaily}
                            type="number"
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.budget_daily_calls ?? 0}
                            onChange={(e) =>
                              setProfileForm((p) => p && { ...p, budget_daily_calls: Number(e.target.value) })
                            }
                            min={0}
                          />
                          <p className="text-xs text-slate-400">Limite de chamadas por dia.</p>
                        </div>
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.budgetMonthly}>
                            Budget mensal
                          </label>
                          <input
                            id={profileFieldId.budgetMonthly}
                            type="number"
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.budget_monthly_calls ?? 0}
                            onChange={(e) =>
                              setProfileForm((p) => p && { ...p, budget_monthly_calls: Number(e.target.value) })
                            }
                            min={0}
                          />
                          <p className="text-xs text-slate-400">Limite total no mês para evitar surpresas.</p>
                        </div>
                      </div>
                      <div className="grid gap-3 md:grid-cols-2">
                        <div>
                          <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.status}>
                            Status
                          </label>
                          <select
                            id={profileFieldId.status}
                            className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                            value={profileForm.status}
                            onChange={(e) =>
                              setProfileForm((p) => p && { ...p, status: e.target.value as IngestionProfile['status'] })
                            }
                          >
                            <option value="active">Ativo</option>
                            <option value="inactive">Inativo</option>
                            <option value="paused">Pausado</option>
                          </select>
                          <p className="text-xs text-slate-400">Perfis ativos consomem budget; pause quando necessário.</p>
                        </div>
                        <div className="flex items-end">
                          <label
                            className="flex items-center gap-2 text-sm font-semibold text-slate-100"
                            htmlFor={profileFieldId.enabled}
                          >
                            <input
                              type="checkbox"
                              id={profileFieldId.enabled}
                              className="h-4 w-4 rounded border border-white/20 bg-slate-900"
                              checked={profileForm.enabled}
                              onChange={(e) => setProfileForm((p) => p && { ...p, enabled: e.target.checked })}
                            />
                            Permitir execução imediata
                          </label>
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-semibold text-slate-100" htmlFor={profileFieldId.keywords}>
                          Palavras-chave
                        </label>
                        <input
                          id={profileFieldId.keywords}
                          className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                          value={(profileForm.keywords || []).join(', ')}
                          onChange={(e) =>
                            setProfileForm((p) => p && { ...p, keywords: e.target.value.split(',').map((v) => v.trim()) })}
                          placeholder="Separadas por vírgula"
                        />
                        <p className="text-xs text-slate-400">Ajuda a explicar o escopo do perfil para operadores.</p>
                      </div>
                      <div className="flex flex-wrap items-center gap-3">
                        <button
                          type="submit"
                          disabled={savingProfile}
                          className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-400 disabled:opacity-60"
                        >
                          {savingProfile ? 'Salvando...' : 'Salvar perfil'}
                        </button>
                        <button
                          type="button"
                          className="rounded-lg border border-white/10 px-4 py-2 text-sm font-semibold text-white hover:border-sky-400"
                          onClick={() => void handleRun(profileForm.id || '')}
                          disabled={!profileForm.id || running}
                        >
                          Rodar agora
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {(runError || providerError || profileError) && (
                  <div className="rounded-lg border border-rose-300/50 bg-rose-900/20 p-3 text-sm text-rose-100">
                    {runError && <p>Erro ao executar perfil: {runError}</p>}
                    {providerError && <p>Erro ao salvar provider: {providerError}</p>}
                    {profileError && <p>Erro ao salvar perfil: {profileError}</p>}
                    <button
                      type="button"
                      className="mt-2 text-xs font-semibold underline"
                      onClick={() => {
                        setRunError(null);
                        setProviderError(null);
                        setProfileError(null);
                      }}
                    >
                      Limpar alertas
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </PageContainer>
    </div>
  );
}
