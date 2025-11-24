import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthGuard } from '../core/auth/auth-guard';
import MainLayout from './layout/MainLayout';
import PublicLayout from './layout/PublicLayout';
import LoginPage from '../modules/admin/pages/LoginPage';
import AdminCasesPage from '../modules/admin/pages/AdminCasesPage';
import AdminCaseDetailPage from '../modules/admin/pages/AdminCaseDetailPage';
import AdminOverviewPage from '../modules/admin/pages/AdminOverviewPage';
import AdminSourceDetailPage from '../modules/admin/pages/AdminSourceDetailPage';
import AdminSourcesPage from '../modules/admin/pages/AdminSourcesPage';
import AdminSourceFormPage from '../modules/admin/pages/AdminSourceFormPage';
import CaseTimelinePage from '../modules/cases/pages/CaseTimelinePage';
import CaseXrayPage from '../modules/cases/pages/CaseXrayPage';
import ConsultPage from '../modules/consult/pages/ConsultPage';

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
        <Route path="/admin/sources" element={<AdminSourcesPage />} />
        <Route path="/admin/sources/new" element={<AdminSourceFormPage />} />
        <Route path="/admin/sources/:sourceId" element={<AdminSourceDetailPage />} />
        <Route path="/admin/cases" element={<AdminCasesPage />} />
        <Route path="/admin/cases/:caseId" element={<AdminCaseDetailPage />} />
        <Route path="/admin/cases/:caseId/timeline" element={<CaseTimelinePage />} />
        <Route path="/admin/cases/:caseId/xray" element={<CaseXrayPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
