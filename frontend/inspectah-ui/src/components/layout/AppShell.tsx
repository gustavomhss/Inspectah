import Header from './Header';
import type { ReactNode } from 'react';

interface AppShellProps {
  children: ReactNode;
}

function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-transparent text-slate-50">
      <Header />
      <main className="mx-auto flex max-w-5xl flex-col gap-8 px-4 pb-16 pt-4 md:px-8" aria-live="polite">
        {children}
      </main>
    </div>
  );
}

export default AppShell;
