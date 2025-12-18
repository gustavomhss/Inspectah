import { useState } from 'react';
import { Routes, Route, Outlet, Navigate, useNavigate } from 'react-router-dom';
import { SpThemeProvider } from './context/ThemeContext';
import { SpHeader, SpDashboardHeader, SpFooter, SpSidebar } from './components/layout';
import {
  SpHomePage,
  SpAboutPage,
  SpHowToPlayPage,
  SpFaqPage,
  SpContactPage,
  SpLoginPage,
  SpSignupPage,
  SpDashboardPage,
  SpTradePage,
  SpPlayerProfilePage,
  SpAffiliatePage,
} from './pages';
import {
  SpAdminOverviewPage,
  SpCasesPage,
  SpCaseDetailPage,
  SpSourcesPage,
  SpSourceDetailPage,
  SpAgentsPage,
  SpAgentDetailPage,
  SpIngestionPage,
  SpTruthConsolePage,
  SpOpsPage,
  SpGuardianPage,
  SpConsultPage,
} from './pages/admin';
import type { SpUser } from './types';
import './styles/spovest.css';

// Mock user for demo
const mockUser: SpUser = {
  id: '1',
  username: 'Ed Walsh',
  email: 'ed.walsh@example.com',
  balance: 500.0,
  portfolioValue: 1500.0,
  earnings: 450.0,
  followers: 125,
  following: 89,
  createdAt: '2023-01-15',
};

// Public Layout (with header and footer)
function PublicLayout() {
  const navigate = useNavigate();

  return (
    <div className="spovest-app spovest-theme-dark min-h-screen flex flex-col">
      <SpHeader
        onLogin={() => navigate('/spovest/login')}
        onSignup={() => navigate('/spovest/signup')}
      />
      <main className="flex-1">
        <Outlet />
      </main>
      <SpFooter />
    </div>
  );
}

// Auth Layout (minimal, no header/footer)
function AuthLayout() {
  return (
    <div className="spovest-app spovest-theme-dark min-h-screen">
      <Outlet />
    </div>
  );
}

// Dashboard Layout (with sidebar)
function DashboardLayout({ user, onLogout }: { user: SpUser; onLogout: () => void }) {
  return (
    <div className="spovest-app spovest-theme-dark min-h-screen flex flex-col">
      <SpDashboardHeader user={user} onLogout={onLogout} />
      <div className="flex flex-1">
        <SpSidebar />
        <main className="flex-1 overflow-auto bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

// Admin Layout (with sidebar, for admin pages)
function AdminLayout({ user, onLogout }: { user: SpUser; onLogout: () => void }) {
  return (
    <div className="spovest-app spovest-theme-dark min-h-screen flex flex-col">
      <SpDashboardHeader user={user} onLogout={onLogout} />
      <div className="flex flex-1">
        <SpSidebar variant="admin" />
        <main className="flex-1 overflow-auto bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

// Protected Route wrapper
function ProtectedRoute({ user, children }: { user: SpUser | null; children: React.ReactNode }) {
  if (!user) {
    return <Navigate to="/spovest/login" replace />;
  }
  return <>{children}</>;
}

export function SpovestApp() {
  // Start logged in for demo purposes
  const [user, setUser] = useState<SpUser | null>(mockUser);
  const navigate = useNavigate();

  const handleLogin = (email: string, password: string) => {
    // Mock login
    console.log('Login:', email, password);
    setUser(mockUser);
    navigate('/spovest/dashboard');
  };

  const handleSignup = (email: string, password: string) => {
    // Mock signup
    console.log('Signup:', email, password);
    setUser({ ...mockUser, email });
    navigate('/spovest/dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    navigate('/spovest');
  };

  return (
    <SpThemeProvider>
      <Routes>
        {/* Public Routes */}
        <Route element={<PublicLayout />}>
          <Route index element={<SpHomePage />} />
          <Route path="about" element={<SpAboutPage />} />
          <Route path="how-to-play" element={<SpHowToPlayPage />} />
          <Route path="faq" element={<SpFaqPage />} />
          <Route path="contact" element={<SpContactPage />} />
        </Route>

        {/* Auth Routes */}
        <Route element={<AuthLayout />}>
          <Route path="login" element={<SpLoginPage onLogin={handleLogin} />} />
          <Route path="signup" element={<SpSignupPage onSignup={handleSignup} />} />
        </Route>

        {/* Dashboard Routes (Protected) */}
        <Route
          element={
            <ProtectedRoute user={user}>
              <DashboardLayout user={user!} onLogout={handleLogout} />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<SpDashboardPage />} />
          <Route path="trade" element={<SpTradePage />} />
          <Route path="trade/:sport" element={<SpTradePage />} />
          <Route path="player/:playerId" element={<SpPlayerProfilePage />} />
          <Route path="affiliate" element={<SpAffiliatePage />} />
        </Route>

        {/* Admin Routes (Protected) */}
        <Route
          element={
            <ProtectedRoute user={user}>
              <AdminLayout user={user!} onLogout={handleLogout} />
            </ProtectedRoute>
          }
        >
          <Route path="admin" element={<SpAdminOverviewPage />} />
          <Route path="admin/cases" element={<SpCasesPage />} />
          <Route path="admin/cases/:caseId" element={<SpCaseDetailPage />} />
          <Route path="admin/sources" element={<SpSourcesPage />} />
          <Route path="admin/sources/:sourceId" element={<SpSourceDetailPage />} />
          <Route path="admin/agents" element={<SpAgentsPage />} />
          <Route path="admin/agents/:agentId" element={<SpAgentDetailPage />} />
          <Route path="admin/agents/flow" element={<SpAgentsPage />} />
          <Route path="admin/ingestion" element={<SpIngestionPage />} />
          <Route path="admin/console/truth" element={<SpTruthConsolePage />} />
          <Route path="admin/ops" element={<SpOpsPage />} />
          <Route path="admin/guardian" element={<SpGuardianPage />} />
        </Route>

        {/* Public Consult Route */}
        <Route element={<AuthLayout />}>
          <Route path="consult" element={<SpConsultPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/spovest" replace />} />
      </Routes>
    </SpThemeProvider>
  );
}
