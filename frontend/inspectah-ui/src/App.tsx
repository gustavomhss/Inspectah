import { BrowserRouter, Route, Routes } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import ConsultationRoute from './routes/ConsultationRoute';
import AdminLayout from './pages/admin/AdminLayout';
import AdminOverviewPage from './pages/admin/AdminOverviewPage';
import AdminSourcesPage from './pages/admin/AdminSourcesPage';
import AdminSourceDetailPage from './pages/admin/AdminSourceDetailPage';
import AdminCasesPage from './pages/admin/AdminCasesPage';
import AdminCaseDetailPage from './pages/admin/AdminCaseDetailPage';

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<ConsultationRoute />} />
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminOverviewPage />} />
            <Route path="sources" element={<AdminSourcesPage />} />
            <Route path="sources/:sourceId" element={<AdminSourceDetailPage />} />
            <Route path="cases" element={<AdminCasesPage />} />
            <Route path="cases/:caseId" element={<AdminCaseDetailPage />} />
          </Route>
          <Route path="*" element={<ConsultationRoute />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

export default App;
