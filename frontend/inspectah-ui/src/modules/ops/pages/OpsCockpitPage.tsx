import { useCallback, useEffect, useMemo, useState } from 'react';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Table from '../../../shared/components/Table';
import Badge from '../../../shared/components/Badge';
import Input from '../../../shared/components/Input';
import { env } from '../../../core/config/env';

const API_BASE = env.apiBaseUrl;

type Component = {
  id: string;
  tipo?: string;
  criticidade?: string;
  descricao?: string;
  slos?: (string | { id?: string; slo_id?: string })[];
};

type Incident = {
  id: string;
  title: string;
  severity: string;
  state: string;
  component_id?: string;
};

type SloState = {
  slo_id: string;
  status: string;
  metrica: string;
  janela: string;
  limiar: string;
};

type Overview = {
  components: number;
  incidents: number;
  slos?: SloState[];
};

type ComponentStatus = 'OK' | 'DEGRADED' | 'UNKNOWN';

const severityTone: Record<string, 'danger' | 'warning' | 'info' | 'default'> = {
  CRITICAL: 'danger',
  HIGH: 'danger',
  MEDIUM: 'warning',
  LOW: 'info',
};

const stateTone: Record<string, 'danger' | 'warning' | 'info' | 'default'> = {
  OPEN: 'danger',
  TRIAGE: 'warning',
  MITIGATING: 'warning',
  RESOLVED: 'info',
  CLOSED: 'default',
};

function useCockpitData() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [components, setComponents] = useState<Component[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewRes, compsRes, incsRes] = await Promise.all([
        fetch(`${API_BASE}/api/ops/cockpit/overview`),
        fetch(`${API_BASE}/api/ops/cockpit/components`),
        fetch(`${API_BASE}/api/ops/cockpit/incidents`),
      ]);

      if (!overviewRes.ok || !compsRes.ok || !incsRes.ok) {
        throw new Error('Falha ao carregar dados do cockpit');
      }

      const overviewData = (await overviewRes.json()) as Overview;
      const compsData = (await compsRes.json()) as Component[] | unknown;
      const incsData = (await incsRes.json()) as Incident[] | unknown;

      setOverview(overviewData && typeof overviewData === 'object' ? overviewData : null);
      setComponents(Array.isArray(compsData) ? compsData : []);
      setIncidents(Array.isArray(incsData) ? incsData : []);
    } catch (err) {
      setError((err as Error).message);
      setOverview(null);
      setComponents([]);
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  }, []);

  return { overview, components, incidents, loading, error, reload: load };
}

export default function OpsCockpitPage() {
  const { overview, components, incidents, loading, error, reload } = useCockpitData();
  const [componentSearch, setComponentSearch] = useState('');
  const [incidentSeverity, setIncidentSeverity] = useState<string>('all');
  const [incidentState, setIncidentState] = useState<string>('all');
  const [componentType, setComponentType] = useState<string>('all');

  useEffect(() => {
    void reload();
  }, [reload]);

  const sloIndex = useMemo(() => {
    const index = new Map<string, SloState>();
    (overview?.slos || []).forEach((s) => index.set(s.slo_id, s));
    return index;
  }, [overview]);

  const componentIncidents = useMemo(() => {
    return incidents.reduce<Record<string, Incident[]>>((acc, inc) => {
      const key = inc.component_id || 'desconhecido';
      if (!acc[key]) acc[key] = [];
      acc[key].push(inc);
      return acc;
    }, {});
  }, [incidents]);

  const componentsWithStatus = useMemo(() => {
    return components.map((c) => {
      const slosForComponent = (c.slos || []).map((sloId) => sloIndex.get(sloId)).filter(Boolean) as SloState[];
      const status: ComponentStatus = slosForComponent.some((s) => s.status !== 'OK')
        ? 'DEGRADED'
        : slosForComponent.length
          ? 'OK'
          : 'UNKNOWN';
      return { ...c, status };
    });
  }, [components, sloIndex]);

  const filteredComponents = useMemo(() => {
    return componentsWithStatus.filter((c) => {
      const matchesSearch = componentSearch
        ? c.id.toLowerCase().includes(componentSearch.toLowerCase()) ||
          (c.descricao || '').toLowerCase().includes(componentSearch.toLowerCase())
        : true;
      const matchesType = componentType === 'all' ? true : (c.tipo || '').toLowerCase() === componentType;
      return matchesSearch && matchesType;
    });
  }, [componentsWithStatus, componentSearch, componentType]);

  const filteredIncidents = useMemo(() => {
    return incidents.filter((i) => {
      const matchesSeverity = incidentSeverity === 'all' ? true : i.severity === incidentSeverity;
      const matchesState = incidentState === 'all' ? true : i.state === incidentState;
      return matchesSeverity && matchesState;
    });
  }, [incidents, incidentSeverity, incidentState]);

  const totalComponents =
    typeof overview?.components === 'number'
      ? overview.components
      : Array.isArray(overview?.components)
        ? overview.components.length
        : components.length;
  const totalIncidents =
    typeof overview?.incidents === 'number'
      ? overview.incidents
      : Array.isArray(overview?.incidents)
        ? overview.incidents.length
        : incidents.length;
  const sloStates = overview?.slos || [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="OracleOps Cockpit v1"
        subtitle="Saúde operacional do recorte da S33: componentes, SLOs e incidentes com filtros para larga escala."
        actions={
          <button
            type="button"
            onClick={() => reload()}
            className="rounded-full bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400"
          >
            Atualizar agora
          </button>
        }
      />

      {error ? (
        <PageContainer className="border-rose-500/30">
          <p className="text-sm text-rose-100">Falha ao carregar cockpit: {error}</p>
        </PageContainer>
      ) : null}

      <PageContainer className="border-white/10 bg-white/5">
        <h3 className="text-lg font-semibold text-white">Como usar esta tela</h3>
        <ul className="mt-2 space-y-1 text-sm text-slate-100 list-disc list-inside">
          <li>Use os filtros de incidentes para priorizar (severidade/estado).</li>
          <li>Filtre componentes por ID/descrição ou tipo (fonte/pipeline/api).</li>
          <li>Badges de SLO indicam status; clique nos componentes para checar SLOs ligados.</li>
          <li>Cards de métricas no topo dão visão rápida de volume de componentes/incidentes/SLOs.</li>
          <li>Leve qualquer fluxo ao cockpit pela tela de detalhes do fluxo (botão “Abrir painel de operações”).</li>
        </ul>
      </PageContainer>

      <PageContainer>
        <div className="grid gap-4 md:grid-cols-3">
          <MetricCard label="Componentes do recorte" value={totalComponents} tone="info" />
          <MetricCard label="Incidentes" value={totalIncidents} tone={totalIncidents > 0 ? 'danger' : 'success'} />
          <MetricCard label="SLOs monitorados" value={sloStates.length} tone="info" />
        </div>
      </PageContainer>

      <div className="grid gap-6 lg:grid-cols-2">
        <PageContainer className="h-full">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-300">Fluxo</p>
              <h3 className="text-lg font-semibold text-white">Incidentes</h3>
              <p className="text-sm text-slate-300">Filtre por severidade/estado para operar volumes maiores.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <select
                className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                value={incidentSeverity}
                onChange={(e) => setIncidentSeverity(e.target.value)}
              >
                <option value="all">Todas severidades</option>
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
              </select>
              <select
                className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                value={incidentState}
                onChange={(e) => setIncidentState(e.target.value)}
              >
                <option value="all">Todos estados</option>
                <option value="OPEN">OPEN</option>
                <option value="TRIAGE">TRIAGE</option>
                <option value="MITIGATING">MITIGATING</option>
                <option value="RESOLVED">RESOLVED</option>
                <option value="CLOSED">CLOSED</option>
              </select>
            </div>
          </div>

          <Table className="mt-4">
            <thead>
              <tr className="border-b border-white/10 text-left text-xs uppercase tracking-wide text-slate-300">
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Título</th>
                <th className="px-4 py-3">Severidade</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3">Componente</th>
              </tr>
            </thead>
            <tbody>
              {filteredIncidents.map((i) => (
                <tr key={i.id} className="border-b border-white/5 last:border-0">
                  <td className="px-4 py-3 font-mono text-sm text-slate-100">{i.id}</td>
                  <td className="px-4 py-3 text-sm text-white">{i.title}</td>
                  <td className="px-4 py-3">
                    <Badge tone={severityTone[i.severity] ?? 'default'}>{i.severity}</Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={stateTone[i.state] ?? 'default'}>{i.state}</Badge>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-200">{i.component_id || '—'}</td>
                </tr>
              ))}
              {!filteredIncidents.length ? (
                <tr>
                  <td className="px-4 py-4 text-sm text-slate-300" colSpan={5}>
                    Nenhum incidente encontrado com os filtros atuais.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </Table>
        </PageContainer>

        <PageContainer className="h-full">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-300">Inventário</p>
              <h3 className="text-lg font-semibold text-white">Componentes e pipelines</h3>
              <p className="text-sm text-slate-300">
                Filtros de texto e tipo para operar volumes maiores (newsdata.io, webz.io, etc).
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Input
                label="Buscar"
                placeholder="filtrar por ID ou descrição"
                value={componentSearch}
                onChange={(e) => setComponentSearch(e.target.value)}
                className="min-w-[220px]"
              />
              <select
                className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                value={componentType}
                onChange={(e) => setComponentType(e.target.value)}
              >
                <option value="all">Todos os tipos</option>
                <option value="fonte">Fontes</option>
                <option value="pipeline">Pipelines</option>
                <option value="api">APIs</option>
              </select>
            </div>
          </div>

          <Table className="mt-4">
            <thead>
              <tr className="border-b border-white/10 text-left text-xs uppercase tracking-wide text-slate-300">
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3">Criticidade</th>
                <th className="px-4 py-3">SLOs</th>
                <th className="px-4 py-3">Incidentes</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredComponents.map((c) => (
                <tr key={c.id} className="border-b border-white/5 last:border-0">
                  <td className="px-4 py-3 font-mono text-sm text-slate-100">{c.id}</td>
                  <td className="px-4 py-3 text-sm capitalize text-slate-200">{c.tipo || '—'}</td>
                  <td className="px-4 py-3 text-sm text-slate-200">{c.criticidade || '—'}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      {(c.slos || []).map((raw) => {
                        const sloId = typeof raw === 'string' ? raw : (raw as any)?.id || (raw as any)?.slo_id || 'slo';
                        const slo = sloIndex.get(sloId);
                        return (
                          <Badge key={sloId} tone={slo ? (slo.status === 'OK' ? 'success' : 'warning') : 'default'}>
                            {sloId}
                          </Badge>
                        );
                      })}
                      {(c.slos || []).length === 0 ? <span className="text-sm text-slate-400">Sem SLO</span> : null}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-200">
                    {componentIncidents[c.id]?.length || 0}
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={c.status === 'OK' ? 'success' : c.status === 'DEGRADED' ? 'warning' : 'default'}>
                      {c.status}
                    </Badge>
                  </td>
                </tr>
              ))}
              {!filteredComponents.length ? (
                <tr>
                  <td className="px-4 py-4 text-sm text-slate-300" colSpan={6}>
                    Nenhum componente encontrado com os filtros atuais.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </Table>
        </PageContainer>
      </div>

      <PageContainer>
        <div className="flex flex-col gap-2">
          <h3 className="text-lg font-semibold text-white">SLOs monitorados</h3>
          <p className="text-sm text-slate-300">
            O que você monitora: cada SLO é uma meta (métrica + janela + limiar).
            Ideal (OK) = meta cumprida; Problema (DEGRADED) = em risco/fora do limiar; UNKNOWN = sem dado ou não mapeado.
          </p>
        </div>
        <Table className="mt-4">
          <thead>
            <tr className="border-b border-white/10 text-left text-xs uppercase tracking-wide text-slate-300">
              <th className="px-4 py-3">SLO</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Métrica</th>
              <th className="px-4 py-3">Janela</th>
              <th className="px-4 py-3">Limiar</th>
            </tr>
          </thead>
          <tbody>
            {sloStates.map((slo) => (
              <tr key={slo.slo_id} className="border-b border-white/5 last:border-0">
                <td className="px-4 py-3 font-mono text-sm text-slate-100">{slo.slo_id}</td>
                <td className="px-4 py-3">
                  <Badge tone={slo.status === 'OK' ? 'success' : slo.status === 'DEGRADED' ? 'warning' : 'default'}>
                    {slo.status}
                  </Badge>
                </td>
                <td className="px-4 py-3 font-mono text-sm text-slate-200">{slo.metrica}</td>
                <td className="px-4 py-3 text-sm text-slate-200">{slo.janela}</td>
                <td className="px-4 py-3 text-sm text-slate-200">{slo.limiar}</td>
              </tr>
            ))}
            {!sloStates.length ? (
              <tr>
                <td className="px-4 py-4 text-sm text-slate-300" colSpan={5}>
                  Nenhum SLO carregado.
                </td>
              </tr>
            ) : null}
          </tbody>
        </Table>
      </PageContainer>

      <PageContainer className="border-white/10 bg-white/5">
        <div className="flex flex-col gap-2">
          <h3 className="text-lg font-semibold text-white">Glossário rápido</h3>
          <p className="text-sm text-slate-300">
            Referência operacional para quem pluga novas fontes (ex.: newsdata.io, webz.io) e precisa entender campos.
          </p>
          <dl className="grid gap-3 md:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-400">Component ID</dt>
              <dd className="text-sm text-slate-100">Identificador estável do componente/pipeline conforme mapa da S33.</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-400">Tipo</dt>
              <dd className="text-sm text-slate-100">fonte | pipeline | api — usado para filtrar em cenários de grande volume.</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-400">Criticidade</dt>
              <dd className="text-sm text-slate-100">Importância declarada no mapa (alta/média/baixa) para priorização.</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-400">SLO</dt>
              <dd className="text-sm text-slate-100">Meta operacional associada ao componente. Badge herda estado OK/DEGRADED.</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-400">Status do componente</dt>
              <dd className="text-sm text-slate-100">
                OK (todos SLOs OK), DEGRADED (algum SLO violado), UNKNOWN (sem SLO mapeado).
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-400">Incidentes</dt>
              <dd className="text-sm text-slate-100">Contagem de incidentes ligados ao componente (abertos ou históricos).</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-400">Severidade</dt>
              <dd className="text-sm text-slate-100">CRITICAL/HIGH/MEDIUM/LOW — usada para ordenar a triagem.</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-400">Estado do incidente</dt>
              <dd className="text-sm text-slate-100">OPEN → TRIAGE → MITIGATING → RESOLVED → CLOSED (ciclo de vida).</dd>
            </div>
          </dl>
        </div>
      </PageContainer>

      {loading ? (
        <div className="text-sm text-slate-300">Carregando cockpit...</div>
      ) : null}
    </div>
  );
}

function MetricCard({ label, value, tone }: { label: string; value: number; tone: 'info' | 'success' | 'danger' }) {
  const toneClass =
    tone === 'success'
      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-100'
      : tone === 'danger'
        ? 'bg-rose-500/10 border-rose-500/30 text-rose-100'
        : 'bg-sky-500/10 border-sky-500/30 text-sky-100';
  return (
    <div className={`rounded-xl border px-4 py-3 ${toneClass}`}>
      <p className="text-xs uppercase tracking-wide text-white/80">{label}</p>
      <p className="mt-2 text-3xl font-bold text-white">{value}</p>
    </div>
  );
}
