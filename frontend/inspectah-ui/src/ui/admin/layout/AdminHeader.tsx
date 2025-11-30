import type { ReactNode } from 'react';
import { colors } from '../tokens';

interface AdminHeaderProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}

export function AdminHeader({ title, subtitle, actions }: AdminHeaderProps) {
  return (
    <div
      className="flex flex-col gap-2 px-6 py-4 lg:flex-row lg:items-center lg:justify-between"
      style={{ borderColor: colors.border }}
    >
      <div>
        <h1 className="text-xl font-semibold text-white">{title}</h1>
        {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}
