import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getAdminCaseTimeline } from '../../api/admin';
import Timeline from '../../components/admin/timeline/Timeline';
import TimelineFilters from '../../components/admin/timeline/TimelineFilters';
import EmptyState from '../../components/admin/EmptyState';
import ErrorState from '../../components/admin/ErrorState';
import LoadingState from '../../components/admin/LoadingState';
import type { AdminTimelineResponse } from '../../types/admin';

function AdminCaseTimelinePage() {
  const { caseId } = useParams<{ caseId: string }>();
  const [timeline, setTimeline] = useState<AdminTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<{ type: string; severity: string }>({ type: 'all', severity: 'all' });

  const load = useCallback(async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getAdminCaseTimeline(caseId);
      setTimeline(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    void load();
  }, [load]);

  const availableTypes = useMemo(() => {
    const types = new Set<string>();
    (timeline?.events || []).forEach((event) => types.add(event.event_type));
    return Array.from(types).sort();
  }, [timeline]);

  const filteredEvents = useMemo(() => {
    let events = timeline?.events || [];
    if (filters.type !== 'all') {
      events = events.filter((event) => event.event_type === filters.type);
    }
    if (filters.severity !== 'all') {
      events = events.filter((event) => (event.severity || 'info') === filters.severity);
    }
    return events;
  }, [filters, timeline]);

  if (loading) {
    return <LoadingState label="Carregando timeline do caso..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  if (!timeline) {
    return <EmptyState title="Timeline indisponível" description="Não encontramos eventos para este caso." />;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3 text-sm font-semibold text-sky-200">
          <Link to="/admin/cases" className="hover:underline">
            ← Voltar para Casos/Temas
          </Link>
          <span className="text-slate-400">/</span>
          <Link to={`/admin/cases/${timeline.case_id}`} className="hover:underline">
            Detalhe do caso
          </Link>
        </div>
        <Link
          to={`/admin/cases/${timeline.case_id}/xray`}
          className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm font-semibold text-sky-200 hover:border-white/20"
        >
          Ver raio-X →
        </Link>
      </div>

      <div className="rounded-2xl border border-white/5 bg-white/5 p-5 shadow-card">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Timeline</p>
            <h3 className="text-xl font-bold text-white">Histórico do caso {timeline.case_id}</h3>
            <p className="text-sm text-slate-200">Eventos ordenados do Sistema de Blocos e Debunker.</p>
          </div>
        </div>

        <div className="mt-4 space-y-4">
          <TimelineFilters
            availableTypes={availableTypes}
            selectedType={filters.type}
            selectedSeverity={filters.severity}
            onChange={setFilters}
          />
          <Timeline events={filteredEvents} />
        </div>
      </div>
    </div>
  );
}

export default AdminCaseTimelinePage;
