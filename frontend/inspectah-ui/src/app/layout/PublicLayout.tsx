import { Outlet } from 'react-router-dom';
import PublicHeader from './PublicHeader';

function PublicLayout() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-50">
      <PublicHeader />
      <main className="mx-auto flex max-w-5xl flex-col gap-8 px-4 pb-16 pt-4 md:px-8" aria-live="polite">
        <Outlet />
      </main>
    </div>
  );
}

export default PublicLayout;
