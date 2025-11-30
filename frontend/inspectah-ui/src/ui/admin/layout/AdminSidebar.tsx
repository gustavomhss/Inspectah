import type { ReactNode } from 'react';
import { SidebarNavItem, type SidebarNavItemProps } from './SidebarNavItem';

interface AdminSidebarProps {
  title?: string;
  navItems?: SidebarNavItemProps[];
  footer?: ReactNode;
  children?: ReactNode;
}

export function AdminSidebar({ title, navItems = [], footer, children }: AdminSidebarProps) {
  return (
    <div className="flex h-full flex-col p-4 gap-4">
      {title && <div className="text-sm font-semibold uppercase tracking-wide text-slate-300/80">{title}</div>}
      <nav className="flex flex-col gap-1">
        {navItems.map((item) => (
          <SidebarNavItem key={item.to ?? item.label} {...item} />
        ))}
      </nav>
      {children}
      {footer && <div className="mt-auto pt-4 text-xs text-slate-400">{footer}</div>}
    </div>
  );
}
