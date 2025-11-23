import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import EmptyState from '../../admin/components/EmptyState';
import ErrorState from '../../admin/components/ErrorState';
import LoadingState from '../../admin/components/LoadingState';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import { useCaseTimeline } from '../hooks/useCaseTimeline';
import Timeline from '../components/timeline/Timeline';
import TimelineFilters from '../components/timeline/TimelineFilters';

function CaseTimelinePage() {
  const { caseId } = useParams<{ caseId: string }>();
  const { timeline, load, loading, error } = useCaseTimeline(caseId);
  const [filters, setFilters] = useState<{ type: string; severity: string }>({ type: 'all', severity: 'all' });

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
      <PageHeader
        title={`Timeline do caso ${timeline.case_id}`}
        subtitle="Eventos ordenados do Sistema de Blocos e Debunker para acompanhar a evolução."
        actions={
          <Link
            to={`/admin/cases/${timeline.case_id}/xray`}
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm font-semibold text-sky-200 hover:border-white/20"
          >
            Ver raio-X →
          </Link>
        }
      />

      <PageContainer>
        <div className="flex flex-wrap items-center gap-3 text-sm font-semibold text-sky-200">
          <Link to="/admin/cases" className="hover:underline">
            ← Voltar para Casos/Temas
          </Link>
          <span className="text-slate-400">/</span>
          <Link to={`/admin/cases/${timeline.case_id}`} className="hover:underline">
            Detalhe do caso
          </Link>
        </div>

        <p className="mt-4 text-sm text-slate-200">Histórico do caso com eventos ordenados e filtráveis.</p>

        <div className="mt-4 space-y-4">
          <TimelineFilters
            availableTypes={availableTypes}
            selectedType={filters.type}
            selectedSeverity={filters.severity}
            onChange={setFilters}
          />
          <Timeline events={filteredEvents} />
        </div>
      </PageContainer>
    </div>
  );
}

export default CaseTimelinePage;
