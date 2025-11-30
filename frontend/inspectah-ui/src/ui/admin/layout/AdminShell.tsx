import type { ReactNode } from 'react';
import { colors } from '../tokens';

interface AdminShellProps {
  sidebar?: ReactNode;
  header?: ReactNode;
  children: ReactNode;
}

export function AdminShell({ sidebar, header, children }: AdminShellProps) {
  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: colors.background, color: colors.textPrimary, fontFamily: 'Manrope, Inter, system-ui, sans-serif' }}
    >
      <div className="flex min-h-screen">
        {sidebar && <aside className="w-64 border-r border-slate-800/70 bg-slate-900/50">{sidebar}</aside>}
        <div className="flex flex-1 flex-col">
          {header && <header className="border-b border-slate-800/70 bg-slate-900/40">{header}</header>}
          <main className="flex-1 p-6 lg:p-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
