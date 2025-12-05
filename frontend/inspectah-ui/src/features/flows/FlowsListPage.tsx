import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminContent, AdminHeader, Badge, Banner, Button, Input, Select, Table } from '@/ui/admin';
import FlowCreateFromTemplateDialog from './FlowCreateFromTemplateDialog';
import { FlowStateBadge } from './FlowStateBadge';
import { useFlowsList, useFlowTemplates } from './hooks';
import { upsertFlowTemplate } from './api';
import type { Flow, FlowTemplate } from './types';

type TemplateStep = { ordem: number; tipo_etapa: string; agent_role: string };
type TemplateForm = {
  slug: string;
  version: string;
  domain: string;
  entry_type: string;
  description: string;
  steps: TemplateStep[];
};

export function FlowsListPage() {
  const navigate = useNavigate();
  const { items, loading, error, reload } = useFlowsList();
  const { templates, reload: reloadTemplates } = useFlowTemplates();
  const flows = items as Flow[];
  const [query, setQuery] = useState('');
  const [estado, setEstado] = useState<string>('');
  const [showCreate, setShowCreate] = useState(false);
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [tplError, setTplError] = useState<string | null>(null);
  const [tplSaving, setTplSaving] = useState(false);
  const [tplForm, setTplForm] = useState<TemplateForm>({
    slug: '',
    version: '1',
    domain: '',
    entry_type: '',
    description: '',
    steps: [{ ordem: 1, tipo_etapa: 'interprete', agent_role: 'agent_role_exemplo' }],
  });
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [newStep, setNewStep] = useState<Pick<TemplateStep, 'tipo_etapa' | 'agent_role'>>({
    tipo_etapa: 'interprete',
    agent_role: '',
  });
  const stepTypes = ['interprete', 'classificador', 'analista', 'debunker', 'decision_maker'];

  const applyTemplateToForm = (tpl: FlowTemplate) => {
    const estrutura = (tpl.estrutura || {}) as {
      steps?: TemplateStep[];
      version?: string;
      domain?: string;
      entry_type?: string;
      description?: string;
      slug?: string;
    };
    const steps = estrutura.steps || [];
    setTplForm({
      slug: tpl.slug || estrutura.slug || '',
      version: estrutura.version || tpl.versao || '1',
      domain: estrutura.domain || '',
      entry_type: estrutura.entry_type || tpl.tipo_entrada || '',
      description: estrutura.description || '',
      steps: steps.length
        ? steps.map((s, idx) => ({ ordem: s.ordem || idx + 1, tipo_etapa: s.tipo_etapa, agent_role: s.agent_role }))
        : [{ ordem: 1, tipo_etapa: 'interprete', agent_role: 'agent_role_exemplo' }],
    });
  };

  const stats = useMemo(() => {
    const total = flows.length;
    const ativos = flows.filter((f) => f.estado === 'ativo').length;
    const emTeste = flows.filter((f) => f.estado === 'em_teste').length;
    const pausados = flows.filter((f) => f.estado === 'pausado').length;
    return { total, ativos, emTeste, pausados };
  }, [flows]);

  const filtered = useMemo(() => {
    return flows.filter((f) => {
      const matchesQuery =
        !query ||
        f.nome?.toLowerCase().includes(query.toLowerCase()) ||
        f.tipo_entrada?.toLowerCase().includes(query.toLowerCase()) ||
        f.slug?.toLowerCase().includes(query.toLowerCase());
      const matchesEstado = !estado || f.estado === estado;
      return matchesQuery && matchesEstado;
    });
  }, [flows, query, estado]);

  return (
    <div className="flex flex-col gap-5">
      <AdminHeader
        title="Fluxos"
        subtitle="Console de Fluxos — visibilidade de estados, versões e operações."
        actions={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => reload()} disabled={loading}>
              {loading ? 'Atualizando...' : 'Atualizar'}
            </Button>
            <Button onClick={() => setShowCreate(true)}>Criar fluxo</Button>
          </div>
        }
      />

      {error && <Banner tone="danger" title="Erro ao carregar fluxos" description={error} />}

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <AdminContent className="bg-white text-slate-900 rounded-2xl border border-slate-200 shadow-sm">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
              <p className="text-sm font-semibold text-emerald-900 uppercase tracking-wide">Fluxos ativos</p>
              <p className="text-3xl font-bold text-emerald-800">{stats.ativos}</p>
              <p className="text-sm text-emerald-900">Prontos para produção</p>
            </div>
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-sm font-semibold text-amber-900 uppercase tracking-wide">Em teste</p>
              <p className="text-3xl font-bold text-amber-800">{stats.emTeste}</p>
              <p className="text-sm text-amber-900">Percentual de teste habilitado</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-900 uppercase tracking-wide">Total / Pausados</p>
              <p className="text-3xl font-bold text-slate-900">
                {stats.total} <span className="text-lg font-semibold text-slate-700">({stats.pausados} pausados)</span>
              </p>
              <p className="text-sm text-slate-800">Panorama geral</p>
            </div>
          </div>
        </AdminContent>

        <AdminContent className="bg-white text-slate-900 rounded-2xl border border-slate-200 shadow-sm">
          <div className="mb-3">
            <h4 className="text-lg font-semibold text-slate-900">Mini glossário</h4>
            <p className="text-base text-slate-800">
              Fluxo = etapas operadas pelo motor. Estado = rascunho/em_teste/ativo/pausado/deprecado.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h5 className="text-base font-semibold text-slate-900 mb-2">Como usar esta tela</h5>
            <ol className="text-base text-slate-800 space-y-1 list-decimal list-inside">
              <li>Atualize ou filtre por nome/slug/estado para achar o fluxo.</li>
              <li>Clique no fluxo para abrir o detalhe e ver execuções/versões.</li>
              <li>Para criar fluxo novo, use “Criar fluxo” e escolha um template.</li>
              <li>Para criar/editar templates, abra “Templates de fluxo” e monte as etapas no construtor visual (sem JSON).</li>
              <li>Use o painel de operações dentro do detalhe do fluxo para ir ao cockpit e acompanhar SLOs/saúde.</li>
            </ol>
          </div>
        </AdminContent>
      </div>

      <AdminContent className="bg-slate-50 rounded-2xl border border-slate-200 shadow-sm">
        <div className="mb-3 flex flex-wrap gap-2">
          <Input
            placeholder="Buscar por nome, slug ou tipo"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="min-w-[240px]"
          />
          <Select aria-label="Estado" value={estado} onChange={(e) => setEstado(e.target.value)}>
            <option value="">Todos os estados</option>
            <option value="draft">Rascunho</option>
            <option value="em_teste">Em teste</option>
            <option value="ativo">Ativo</option>
            <option value="pausado">Pausado</option>
            <option value="deprecado">Deprecado</option>
          </Select>
          {(query || estado) && (
            <Button variant="secondary" size="sm" onClick={() => { setQuery(''); setEstado(''); }}>
              Limpar filtros
            </Button>
          )}
        </div>
        <Table
          headers={['Nome', 'Tipo', 'Domínio', 'Versão', 'Estado', 'Template']}
          isEmpty={filtered.length === 0}
          emptyState={<span className="text-sm text-slate-500 py-4">Nenhum fluxo cadastrado.</span>}
        >
          {filtered.map((flow) => (
            <tr
              key={flow.id}
              className="cursor-pointer bg-white hover:bg-slate-100 border-b border-slate-200"
              onClick={() => navigate(`/flows/${flow.id}`)}
            >
              <td className="px-4 py-3 text-base font-semibold text-slate-900">{flow.nome}</td>
              <td className="text-sm text-slate-900 px-4 py-3">{flow.tipo_entrada}</td>
              <td className="text-sm text-slate-900 px-4 py-3">{flow.domain || '—'}</td>
              <td className="text-sm text-slate-900 px-4 py-3">
                <div className="flex gap-1 items-center">
                  <Badge tone="info">{flow.flow_version_id || '—'}</Badge>
                  {flow.test_version_id && <Badge tone="warning">teste: {flow.test_version_id}</Badge>}
                </div>
              </td>
              <td className="px-4 py-3">
                <FlowStateBadge state={flow.estado} />
              </td>
              <td className="text-sm text-slate-900 px-4 py-3">{flow.template_origem_id || '-'}</td>
            </tr>
          ))}
        </Table>
      </AdminContent>

      {showCreate && (
        <AdminContent className="bg-white rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-base font-semibold text-slate-900">Criar fluxo a partir de template</h4>
            <Button variant="secondary" size="sm" onClick={() => setShowCreate(false)}>
              Fechar
            </Button>
          </div>
          <FlowCreateFromTemplateDialog
            onCreated={(flowId) => {
              setShowCreate(false);
              navigate(`/flows/${flowId}`);
            }}
          />
        </AdminContent>
      )}

      <AdminContent className="bg-slate-900 text-white rounded-2xl border border-slate-800 shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-lg font-semibold text-white">Templates de fluxo</h4>
          <Button variant="secondary" size="sm" onClick={() => setShowTemplateForm((v) => !v)}>
            {showTemplateForm ? 'Fechar' : 'Novo/editar template'}
          </Button>
        </div>
        <div className="mb-3">
          <p className="text-sm font-semibold text-white mb-2">Templates disponíveis:</p>
          <div className="flex flex-wrap gap-2">
            {(templates as FlowTemplate[]).map((t) => (
              <button
                key={t.slug}
                className={`rounded-full px-3 py-1 text-sm border transition ${
                  selectedTemplate === t.slug
                    ? 'border-sky-400 text-sky-100 bg-sky-900/40'
                    : 'border-slate-500 text-white bg-slate-800'
                }`}
                onClick={() => {
                  setSelectedTemplate(t.slug);
                  applyTemplateToForm(t);
                  setShowTemplateForm(true);
                }}
              >
                {t.slug} v{t.versao}
              </button>
            )) || <span className="text-sm text-slate-500">—</span>}
          </div>
        </div>
        {showTemplateForm && (
          <div className="space-y-2 text-white">
            {tplError && <Banner tone="danger" title="Erro ao salvar template" description={tplError} />}
            <div className="grid gap-3 md:grid-cols-2">
              <label className="flex flex-col gap-1" htmlFor="tpl-slug">
                <span className="text-sm font-semibold text-white">Slug</span>
                <Input
                  id="tpl-slug"
                  value={tplForm.slug}
                  onChange={(e) => setTplForm({ ...tplForm, slug: e.target.value })}
                />
              </label>
              <label className="flex flex-col gap-1" htmlFor="tpl-version">
                <span className="text-sm font-semibold text-white">Versão</span>
                <Input
                  id="tpl-version"
                  value={tplForm.version}
                  onChange={(e) => setTplForm({ ...tplForm, version: e.target.value })}
                />
              </label>
              <label className="flex flex-col gap-1" htmlFor="tpl-domain">
                <span className="text-sm font-semibold text-white">Domínio</span>
                <Input
                  id="tpl-domain"
                  value={tplForm.domain}
                  onChange={(e) => setTplForm({ ...tplForm, domain: e.target.value })}
                />
              </label>
              <label className="flex flex-col gap-1" htmlFor="tpl-entry">
                <span className="text-sm font-semibold text-white">Tipo de entrada</span>
                <Input
                  id="tpl-entry"
                  value={tplForm.entry_type}
                  onChange={(e) => setTplForm({ ...tplForm, entry_type: e.target.value })}
                  placeholder="ex.: noticia_texto"
                />
              </label>
            </div>
            <label className="flex flex-col gap-1" htmlFor="tpl-description">
              <span className="text-sm font-semibold text-white">Descrição</span>
              <Input
                id="tpl-description"
                value={tplForm.description}
                onChange={(e) => setTplForm({ ...tplForm, description: e.target.value })}
              />
            </label>
            <div className="rounded-xl border border-slate-700 bg-slate-800 p-3 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">Steps do template</p>
                  <p className="text-xs text-slate-200">Adicione, reordene e remova etapas (sem JSON).</p>
                </div>
                <div className="flex flex-wrap gap-2 items-center">
                  <Select
                    aria-label="Tipo de etapa"
                    value={newStep.tipo_etapa}
                    onChange={(e) => setNewStep({ ...newStep, tipo_etapa: e.target.value })}
                    className="text-sm"
                  >
                    {stepTypes.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </Select>
                  <Input
                    placeholder="agent_role"
                    value={newStep.agent_role}
                    onChange={(e) => setNewStep({ ...newStep, agent_role: e.target.value })}
                    className="w-44"
                  />
                  <Button
                    size="sm"
                    onClick={() => {
                      if (!newStep.agent_role.trim()) {
                        setTplError('Informe o agent_role para adicionar um step.');
                        return;
                      }
                      const next = [...tplForm.steps, { ...newStep, ordem: tplForm.steps.length + 1 }];
                      setTplForm({ ...tplForm, steps: next });
                      setNewStep({ tipo_etapa: 'interprete', agent_role: '' });
                      setTplError(null);
                    }}
                  >
                    Adicionar etapa
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                {tplForm.steps.map((step, idx) => (
                  <div
                    key={`${step.agent_role}-${idx}`}
                    className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2"
                  >
                    <div>
                      <p className="text-sm font-semibold text-slate-900">
                        {idx + 1}. {step.tipo_etapa}
                      </p>
                      <p className="text-xs text-slate-700">Agent role: {step.agent_role}</p>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="secondary"
                        size="sm"
                        disabled={idx === 0}
                        onClick={() => {
                          const next = [...tplForm.steps];
                          [next[idx - 1], next[idx]] = [next[idx], next[idx - 1]];
                          next.forEach((s, i) => (s.ordem = i + 1));
                          setTplForm({ ...tplForm, steps: next });
                        }}
                      >
                        ↑
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        disabled={idx === tplForm.steps.length - 1}
                        onClick={() => {
                          const next = [...tplForm.steps];
                          [next[idx + 1], next[idx]] = [next[idx], next[idx + 1]];
                          next.forEach((s, i) => (s.ordem = i + 1));
                          setTplForm({ ...tplForm, steps: next });
                        }}
                      >
                        ↓
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          const next = tplForm.steps.filter((_, i) => i !== idx);
                          next.forEach((s, i) => (s.ordem = i + 1));
                          setTplForm({ ...tplForm, steps: next });
                        }}
                      >
                        Remover
                      </Button>
                    </div>
                  </div>
                ))}
                {tplForm.steps.length === 0 && <p className="text-sm text-slate-600">Nenhuma etapa adicionada. Adicione acima.</p>}
              </div>
            </div>
            <div className="flex justify-end">
              <Button
                onClick={async () => {
                  if (!tplForm.slug.trim() || !tplForm.version.trim() || !tplForm.domain.trim() || !tplForm.entry_type.trim()) {
                    setTplError('Preencha slug, versão, domínio e tipo de entrada.');
                    return;
                  }
                  if (!tplForm.steps.length) {
                    setTplError('Adicione pelo menos uma etapa.');
                    return;
                  }
                  const steps = tplForm.steps.map((step, idx) => ({
                    ordem: idx + 1,
                    tipo_etapa: step.tipo_etapa,
                    agent_role: step.agent_role.trim(),
                  }));
                  if (steps.some((s) => !s.agent_role)) {
                    setTplError('Todas as etapas precisam de agent_role.');
                    return;
                  }
                  try {
                    setTplSaving(true);
                    setTplError(null);
                    await upsertFlowTemplate({
                      slug: tplForm.slug.trim(),
                      version: tplForm.version.trim(),
                      domain: tplForm.domain.trim(),
                      entry_type: tplForm.entry_type.trim(),
                      description: tplForm.description,
                      steps,
                    });
                    setTplSaving(false);
                    setShowTemplateForm(false);
                    setSelectedTemplate(tplForm.slug.trim());
                    void reloadTemplates();
                    void reload();
                  } catch (err) {
                    setTplSaving(false);
                    setTplError((err as Error).message);
                  }
                }}
                disabled={tplSaving}
              >
                {tplSaving ? 'Salvando...' : 'Salvar template'}
              </Button>
            </div>
          </div>
        )}
      </AdminContent>
    </div>
  );
}

export default FlowsListPage;
