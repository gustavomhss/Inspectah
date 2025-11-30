import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { colors } from '../tokens';

export interface SidebarNavItemProps {
  label: string;
  to?: string;
  icon?: ReactNode;
  active?: boolean;
  onClick?: () => void;
}

export function SidebarNavItem({ label, to, icon, active = false, onClick }: SidebarNavItemProps) {
  const baseClasses =
    'flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2';
  const stateClasses = (isActive: boolean) =>
    isActive || active
      ? 'bg-slate-800/80 text-white'
      : 'text-slate-200 hover:bg-slate-800/60 hover:text-white focus-visible:outline-sky-500';

  if (to) {
    return (
      <NavLink to={to} onClick={onClick} className={({ isActive }) => `no-underline ${baseClasses} ${stateClasses(isActive)}`} style={{ borderColor: colors.border }}>
        {icon}
        <span>{label}</span>
      </NavLink>
    );
  }

  return (
    <button type="button" onClick={onClick} className={`${baseClasses} ${stateClasses(false)} w-full text-left`}>
      {icon}
      <span>{label}</span>
    </button>
  );
}
