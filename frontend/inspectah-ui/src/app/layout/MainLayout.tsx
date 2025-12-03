import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../providers/AuthProvider';

function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const isSourcesConsole = location.pathname.startsWith('/admin/sources');
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-full px-4 py-2 text-sm font-semibold transition ${
      isActive ? 'bg-white/20 text-white' : 'text-slate-200 hover:bg-white/10'
    }`;

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50">
      <header className="border-b border-white/5 bg-white/5 backdrop-blur">
        <div className="mx-auto flex max-w-5xl flex-col gap-2 px-4 py-6 md:px-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Inspectah — Área interna</p>
              <h1 className="text-2xl font-bold text-white md:text-3xl">Admin, Casos, Timeline e Raio-X</h1>
            </div>
            <div className="flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-100">
              <div className="flex flex-col text-left leading-tight">
                <span className="font-semibold">{user?.name || user?.email || user?.id || 'Usuário'}</span>
                <span className="text-[11px] text-slate-300">Acesso autenticado</span>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-full bg-white/10 px-3 py-1 font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
              >
                Sair
              </button>
            </div>
          </div>
          <p className="text-sm text-slate-200">
            Consolide fontes, acompanhe casos/temas e abra timeline/raio-X com navegação protegida e consistente.
          </p>
        </div>
      </header>
      <main
        className={`${isSourcesConsole ? 'w-full px-0' : 'mx-auto max-w-5xl px-4 md:px-8'} flex flex-col gap-6 pb-12 pt-6`}
      >
        <section className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
          <div className="flex flex-col gap-3">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Navegação principal</p>
            <div className="flex flex-wrap gap-2">
              <NavLink to="/admin" end className={navLinkClass}>
                Visão Geral
              </NavLink>
              <NavLink to="/admin/sources" className={navLinkClass}>
                Fontes
              </NavLink>
              <NavLink to="/admin/ingestion" className={navLinkClass}>
                Ingestão
              </NavLink>
              <NavLink to="/admin/agents" className={navLinkClass}>
                Agentes
              </NavLink>
              <NavLink to="/admin/agent-flows" className={navLinkClass}>
                Fluxos de agentes
              </NavLink>
              <NavLink to="/admin/agents/model-policy" className={navLinkClass}>
                Política de modelos
              </NavLink>
              <NavLink to="/admin/cases" className={navLinkClass}>
                Casos/Temas
              </NavLink>
            </div>
          </div>
        </section>
        <Outlet />
      </main>
    </div>
  );
}

export default MainLayout;
