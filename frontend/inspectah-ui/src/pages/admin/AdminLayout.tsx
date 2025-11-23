import { NavLink, Outlet } from 'react-router-dom';

function AdminLayout() {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-full px-4 py-2 text-sm font-semibold transition ${
      isActive ? 'bg-white/20 text-white' : 'text-slate-200 hover:bg-white/10'
    }`;

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-white/5 bg-white/5 p-6 shadow-card">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Inspectah — Console de Admin</p>
        <h2 className="mt-2 text-2xl font-bold text-white">Health, Fontes e Casos/Temas</h2>
        <p className="mt-2 max-w-2xl text-sm text-slate-200">
          Visão operacional do Inspectah. Leia estados consolidados de fontes, casos/temas e saúde do sistema. Nenhuma mutação direta é
          permitida.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <NavLink to="/admin" end className={navLinkClass}>
            Visão Geral
          </NavLink>
          <NavLink to="/admin/sources" className={navLinkClass}>
            Fontes
          </NavLink>
          <NavLink to="/admin/cases" className={navLinkClass}>
            Casos/Temas
          </NavLink>
        </div>
      </section>
      <Outlet />
    </div>
  );
}

export default AdminLayout;
