import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthGuard } from '../core/auth/auth-guard';
import MainLayout from './layout/MainLayout';
import PublicLayout from './layout/PublicLayout';
import LoginPage from '../modules/admin/pages/LoginPage';
import AdminCasesPage from '../modules/admin/pages/AdminCasesPage';
import AdminCaseDetailPage from '../modules/admin/pages/AdminCaseDetailPage';
import AdminOverviewPage from '../modules/admin/pages/AdminOverviewPage';
import TruthConsolePage from '../modules/console/pages/TruthConsolePage';
import AgentStudioPage from '../modules/console/pages/AgentStudioPage';
import IncidentConsolePage from '../modules/console/pages/IncidentConsolePage';
import IngestionListPage from '../modules/ingestion/pages/IngestionListPage';
import IngestionSourceDetailPage from '../modules/ingestion/pages/IngestionSourceDetailPage';
import AgentsListPage from '../modules/agents/pages/AgentsListPage';
import AgentDetailPage from '../modules/agents/pages/AgentDetailPage';
import AgentCommitteesPage from '../modules/agents/pages/AgentCommitteesPage';
import ModelPolicyPage from '../modules/agents/pages/ModelPolicyPage';
import AgentsFlowPage from '../modules/agents/pages/AgentsFlowPage';
import CaseTimelinePage from '../modules/cases/pages/CaseTimelinePage';
import CaseXrayPage from '../modules/cases/pages/CaseXrayPage';
import ConsultPage from '../modules/consult/pages/ConsultPage';
import { SourceEditPage, SourcesListPage } from '../features/sources';
import SourcesLayout from '../features/sources/pages/SourcesLayout';
import SourcesIngestionPage from '../features/sources/pages/SourcesIngestionPage';
import SourcesDebunkerPage from '../features/sources/pages/SourcesDebunkerPage';
import SourcesNotFoundPage from '../features/sources/pages/SourcesNotFoundPage';
import AgentFlowsPage from '../features/agent-flows/AgentFlowsPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<ConsultPage />} />
        <Route path="/consult" element={<ConsultPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Route>

      <Route
        element={
          <AuthGuard>
            <MainLayout />
          </AuthGuard>
        }
      >
        <Route path="/admin" element={<AdminOverviewPage />} />
        <Route path="/admin/cases" element={<AdminCasesPage />} />
        <Route path="/admin/cases/:caseId" element={<AdminCaseDetailPage />} />
        <Route path="/admin/cases/:caseId/timeline" element={<CaseTimelinePage />} />
        <Route path="/admin/cases/:caseId/xray" element={<CaseXrayPage />} />
        <Route path="/admin/ingestion" element={<IngestionListPage />} />
        <Route path="/admin/ingestion/sources/:sourceId" element={<IngestionSourceDetailPage />} />
        <Route path="/admin/agents" element={<AgentsListPage />} />
        <Route path="/admin/agents/:agentId" element={<AgentDetailPage />} />
        <Route path="/admin/agents/:agentId/committees" element={<AgentCommitteesPage />} />
        <Route path="/admin/agents/model-policy" element={<ModelPolicyPage />} />
        <Route path="/admin/agents/flow" element={<AgentsFlowPage />} />
        <Route path="/admin/agent-flows" element={<AgentFlowsPage />} />
        <Route path="/admin/console/truth" element={<TruthConsolePage />} />
        <Route path="/admin/console/agents" element={<AgentStudioPage />} />
        <Route path="/admin/console/incidents" element={<IncidentConsolePage />} />
        <Route path="/admin/sources" element={<SourcesLayout />}>
          <Route index element={<SourcesListPage />} />
          <Route path="new" element={<SourceEditPage />} />
          <Route path=":sourceId" element={<SourceEditPage />} />
          <Route path="ingestao" element={<SourcesIngestionPage />} />
          <Route path="debunker" element={<SourcesDebunkerPage />} />
          <Route path="*" element={<SourcesNotFoundPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
