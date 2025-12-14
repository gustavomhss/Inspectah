/**
 * GuardianCockpitPage — S37
 *
 * Main cockpit dashboard for Guardian decisions
 */

import { useEffect, useState } from 'react';
import EmptyState from '../../admin/components/EmptyState';
import ErrorState from '../../admin/components/ErrorState';
import LoadingState from '../../admin/components/LoadingState';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import Modal from '../../../shared/components/Modal';
import FactCard from '../components/FactCard';
import GuardianMetricsSummary from '../components/GuardianMetricsSummary';
import {
  useAwaitingReview,
  useGuardianDecisions,
  useGuardianMetrics,
  useGuardianPolicies,
} from '../hooks/useGuardian';
import { httpClient } from '../../../core/api/http-client';
import { endpoints } from '../../../core/api/endpoints';
import type { GuardianPolicy, PolicyDetail } from '../types';

type Tab = 'overview' | 'pending' | 'review' | 'completed';

function GuardianCockpitPage() {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [selectedPolicy, setSelectedPolicy] = useState<GuardianPolicy | null>(null);
  const [policyDetail, setPolicyDetail] = useState<PolicyDetail | null>(null);
  const [policyDetailLoading, setPolicyDetailLoading] = useState(false);
  const { metrics, loading: metricsLoading, error: metricsError, load: loadMetrics } = useGuardianMetrics();
  const { decisions, loading: decisionsLoading, error: decisionsError, load: loadDecisions } = useGuardianDecisions();
  const { decisions: awaitingReview, loading: reviewLoading, load: loadAwaitingReview } = useAwaitingReview();
  const { policies, loading: policiesLoading, load: loadPolicies } = useGuardianPolicies();

  useEffect(() => {
    void loadMetrics();
    void loadDecisions();
    void loadAwaitingReview();
    void loadPolicies();
  }, [loadMetrics, loadDecisions, loadAwaitingReview, loadPolicies]);

  // Fetch policy details when a policy is selected
  useEffect(() => {
    if (selectedPolicy) {
      setPolicyDetailLoading(true);
      setPolicyDetail(null);
      httpClient<PolicyDetail>(endpoints.admin.guardian.policyDetail(selectedPolicy.name))
        .then((data) => setPolicyDetail(data))
        .catch(() => setPolicyDetail(null))
        .finally(() => setPolicyDetailLoading(false));
    } else {
      setPolicyDetail(null);
    }
  }, [selectedPolicy]);

  const isLoading = metricsLoading || decisionsLoading || reviewLoading || policiesLoading;
  const error = metricsError || decisionsError;

  if (isLoading && !metrics) {
    return <LoadingState label="Carregando cockpit Guardian..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={loadMetrics} />;
  }

  const pendingDecisions = decisions.filter(
    (d) => !['approved', 'rejected', 'escalated', 'timed_out', 'cancelled'].includes(d.status)
  );
  const completedDecisions = decisions.filter((d) =>
    ['approved', 'rejected', 'escalated', 'timed_out', 'cancelled'].includes(d.status)
  );

  const tabs: { id: Tab; label: string; count?: number }[] = [
    { id: 'overview', label: 'Visão Geral' },
    { id: 'pending', label: 'Pendentes', count: pendingDecisions.length },
    { id: 'review', label: 'Aguardando Revisão', count: awaitingReview.length },
    { id: 'completed', label: 'Concluídas', count: completedDecisions.length },
  ];

  return (
    <div className="space-y-4">
      <PageHeader
        title="Guardian Cockpit"
        subtitle="Painel de controle do sistema de validação de claims"
      />

      <PageContainer>
        {/* Tabs */}
        <div className="flex items-center gap-1 border-b border-white/10 pb-2 mb-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-slate-700 text-white'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.label}
              {tab.count !== undefined && (
                <span
                  className={`ml-2 px-1.5 py-0.5 rounded-full text-xs ${
                    activeTab === tab.id ? 'bg-slate-600' : 'bg-slate-700'
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Metrics */}
            {metrics && <GuardianMetricsSummary metrics={metrics} />}

            {/* Policies */}
            <div>
              <h3 className="text-lg font-semibold text-slate-200 mb-3">Políticas Ativas</h3>
              {policies.length === 0 ? (
                <p className="text-sm text-slate-500">Nenhuma política carregada.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {policies.map((policy) => (
                    <button
                      type="button"
                      key={policy.name}
                      onClick={() => setSelectedPolicy(policy)}
                      className="rounded-lg bg-slate-800/50 border border-white/10 p-3 text-left hover:bg-slate-700/50 hover:border-sky-500/50 transition-colors cursor-pointer"
                    >
                      <p className="font-medium text-slate-200">{policy.name}</p>
                      <p className="text-xs text-slate-500">
                        {policy.domain} / {policy.gate} v{policy.version}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        {policy.requirements} requisitos, {policy.rules} regras
                      </p>
                      <p className="text-xs text-sky-400 mt-2">Clique para ver detalhes</p>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Recent decisions quick view */}
            <div>
              <h3 className="text-lg font-semibold text-slate-200 mb-3">Decisões Recentes</h3>
              {decisions.length === 0 ? (
                <EmptyState
                  title="Sem decisões"
                  description="Nenhuma decisão foi processada ainda."
                />
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {decisions.slice(0, 4).map((decision) => (
                    <FactCard key={decision.id} decision={decision} />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'pending' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-200">
              Decisões Pendentes ({pendingDecisions.length})
            </h3>
            {pendingDecisions.length === 0 ? (
              <EmptyState
                title="Nenhuma decisão pendente"
                description="Todas as decisões foram processadas."
              />
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {pendingDecisions.map((decision) => (
                  <FactCard key={decision.id} decision={decision} />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'review' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-200">
              Aguardando Revisão Humana ({awaitingReview.length})
            </h3>
            {awaitingReview.length === 0 ? (
              <EmptyState
                title="Nenhuma decisão aguardando revisão"
                description="Todas as revisões foram processadas."
              />
            ) : (
              <div className="space-y-4">
                {awaitingReview.map((decision) => (
                  <FactCard key={decision.id} decision={decision} showActions />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'completed' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-200">
              Decisões Concluídas ({completedDecisions.length})
            </h3>
            {completedDecisions.length === 0 ? (
              <EmptyState
                title="Nenhuma decisão concluída"
                description="Ainda não há decisões finalizadas."
              />
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {completedDecisions.map((decision) => (
                  <FactCard key={decision.id} decision={decision} showActions={false} />
                ))}
              </div>
            )}
          </div>
        )}
      </PageContainer>

      {/* Policy Details Modal */}
      <Modal
        open={selectedPolicy !== null}
        onClose={() => setSelectedPolicy(null)}
        title={selectedPolicy?.name || 'Detalhes da Política'}
      >
        {selectedPolicy && (
          <div className="space-y-4">
            {/* Summary Grid */}
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-lg bg-slate-800/50 p-3">
                <p className="text-xs text-slate-400 uppercase tracking-wide">Domínio</p>
                <p className="font-semibold text-white">{selectedPolicy.domain}</p>
              </div>
              <div className="rounded-lg bg-slate-800/50 p-3">
                <p className="text-xs text-slate-400 uppercase tracking-wide">Gate</p>
                <p className="font-semibold text-white">{selectedPolicy.gate}</p>
              </div>
              <div className="rounded-lg bg-slate-800/50 p-3">
                <p className="text-xs text-slate-400 uppercase tracking-wide">Versão</p>
                <p className="font-mono text-sky-300">{selectedPolicy.version}</p>
              </div>
            </div>

            {/* Loading state for details */}
            {policyDetailLoading && (
              <p className="text-sm text-slate-400 animate-pulse">Carregando detalhes...</p>
            )}

            {/* Requirements */}
            {policyDetail && policyDetail.requirements.length > 0 && (
              <div className="rounded-lg bg-green-500/10 border border-green-500/30 p-4">
                <p className="text-xs text-green-300 uppercase tracking-wide mb-3 font-semibold">
                  Requisitos (REQUIRE) — {policyDetail.requirements.length}
                </p>
                <div className="space-y-2">
                  {policyDetail.requirements.map((req, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2 bg-slate-800/50 rounded px-3 py-2 text-sm"
                    >
                      <span className="text-green-400 font-mono">{req.field}</span>
                      <span className="text-slate-500">{req.operator}</span>
                      <span className="text-white font-medium">{String(req.value)}</span>
                      {req.modifier && (
                        <span className="text-xs bg-green-500/20 text-green-300 px-2 py-0.5 rounded">
                          {req.modifier}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Rules */}
            {policyDetail && policyDetail.rules.length > 0 && (
              <div className="rounded-lg bg-amber-500/10 border border-amber-500/30 p-4">
                <p className="text-xs text-amber-300 uppercase tracking-wide mb-3 font-semibold">
                  Regras (ON...THEN) — {policyDetail.rules.length}
                </p>
                <div className="space-y-2">
                  {policyDetail.rules.map((rule, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2 bg-slate-800/50 rounded px-3 py-2 text-sm flex-wrap"
                    >
                      <span className="text-slate-500">ON</span>
                      <span className="text-amber-300 font-mono">{rule.condition_field}</span>
                      {rule.condition_operator !== '=' && (
                        <span className="text-slate-500">{rule.condition_operator}</span>
                      )}
                      {rule.condition_value !== true && (
                        <span className="text-white">{String(rule.condition_value)}</span>
                      )}
                      <span className="text-slate-500">THEN</span>
                      <span className="text-sky-400 font-semibold">{rule.action}</span>
                      {Object.keys(rule.action_params).length > 0 && (
                        <span className="text-xs bg-sky-500/20 text-sky-300 px-2 py-0.5 rounded">
                          {JSON.stringify(rule.action_params)}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Footer */}
            <div className="pt-3 border-t border-white/10">
              <p className="text-xs text-slate-500">
                Arquivo: <span className="font-mono text-slate-400">policies/{selectedPolicy.name}.policy</span>
              </p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default GuardianCockpitPage;
