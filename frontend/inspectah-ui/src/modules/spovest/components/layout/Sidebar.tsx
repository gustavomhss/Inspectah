import { Link, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import type { SpNavItem } from '../../types';

interface SidebarProps {
  className?: string;
  variant?: 'default' | 'admin';
}

const mainNavItems: SpNavItem[] = [
  {
    label: 'My Portfolio',
    href: '/spovest/dashboard',
    icon: 'portfolio',
  },
  {
    label: 'About',
    href: '/spovest/about',
    icon: 'info',
  },
];

const tradingNavItems: SpNavItem[] = [
  { label: 'NBA', href: '/spovest/trade/nba', icon: 'basketball' },
  { label: 'NFL', href: '/spovest/trade/nfl', icon: 'football' },
  { label: 'MLB', href: '/spovest/trade/mlb', icon: 'baseball' },
  { label: 'NHL', href: '/spovest/trade/nhl', icon: 'hockey' },
  { label: 'Soccer', href: '/spovest/trade/soccer', icon: 'soccer' },
  { label: 'Golf', href: '/spovest/trade/golf', icon: 'golf' },
  { label: 'ESports', href: '/spovest/trade/esports', icon: 'esports' },
];

const otherNavItems: SpNavItem[] = [
  { label: 'Affiliate Program', href: '/spovest/affiliate', icon: 'gift' },
  { label: 'Support', href: '/spovest/support', icon: 'support' },
  { label: 'Rules', href: '/spovest/rules', icon: 'book' },
];

// Admin navigation items
const adminMainNavItems: SpNavItem[] = [
  { label: 'Overview', href: '/spovest/admin', icon: 'dashboard' },
  { label: 'Cases', href: '/spovest/admin/cases', icon: 'cases' },
  { label: 'Sources', href: '/spovest/admin/sources', icon: 'sources' },
  { label: 'Agents', href: '/spovest/admin/agents', icon: 'agents' },
  { label: 'Ingestion', href: '/spovest/admin/ingestion', icon: 'ingestion' },
];

const adminConsoleNavItems: SpNavItem[] = [
  { label: 'Truth Console', href: '/spovest/admin/console/truth', icon: 'truth' },
  { label: 'Operations', href: '/spovest/admin/ops', icon: 'ops' },
  { label: 'Guardian', href: '/spovest/admin/guardian', icon: 'guardian' },
];

const adminOtherNavItems: SpNavItem[] = [
  { label: 'Public Consult', href: '/spovest/consult', icon: 'consult' },
  { label: 'Back to Dashboard', href: '/spovest/dashboard', icon: 'back' },
];

const iconMap: Record<string, React.ReactNode> = {
  portfolio: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>
  ),
  info: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  basketball: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <circle cx="12" cy="12" r="9" strokeWidth={2} />
      <path strokeLinecap="round" strokeWidth={2} d="M12 3v18M3 12h18M5.5 5.5c2 2 4 6.5 0 13M18.5 5.5c-2 2-4 6.5 0 13" />
    </svg>
  ),
  football: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <ellipse cx="12" cy="12" rx="9" ry="6" strokeWidth={2} transform="rotate(45 12 12)" />
      <path strokeLinecap="round" strokeWidth={2} d="M8 8l8 8M9 11l6 2M11 9l2 6" />
    </svg>
  ),
  baseball: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <circle cx="12" cy="12" r="9" strokeWidth={2} />
      <path strokeLinecap="round" strokeWidth={2} d="M5 9c2 1 4 4 4 7M19 9c-2 1-4 4-4 7" />
    </svg>
  ),
  hockey: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <circle cx="12" cy="12" r="9" strokeWidth={2} />
      <path strokeLinecap="round" strokeWidth={2} d="M8 12h8M12 8v8" />
    </svg>
  ),
  soccer: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <circle cx="12" cy="12" r="9" strokeWidth={2} />
      <path strokeLinecap="round" strokeWidth={2} d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l3 3M15 15l3 3M6 18l3-3M15 9l3-3" />
    </svg>
  ),
  golf: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeWidth={2} d="M12 3v14M8 6l4-3 4 3M9 21h6" />
      <circle cx="12" cy="18" r="1" fill="currentColor" />
    </svg>
  ),
  esports: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <rect x="4" y="6" width="16" height="12" rx="2" strokeWidth={2} />
      <path strokeLinecap="round" strokeWidth={2} d="M8 10v4M6 12h4M16 10v.01M18 12v.01M16 14v.01" />
    </svg>
  ),
  gift: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
    </svg>
  ),
  support: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  book: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  ),
  // Admin icons
  dashboard: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
    </svg>
  ),
  cases: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  sources: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
    </svg>
  ),
  agents: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  ingestion: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
    </svg>
  ),
  truth: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  ops: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  guardian: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  ),
  consult: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  back: (
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 17l-5-5m0 0l5-5m-5 5h12" />
    </svg>
  ),
};

function NavItem({ item, isActive }: { item: SpNavItem; isActive: boolean }) {
  return (
    <Link
      to={item.href}
      className={clsx(
        'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200',
        isActive
          ? 'bg-violet-600/20 text-violet-400'
          : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
      )}
    >
      <span className="w-5 h-5 flex-shrink-0">{iconMap[item.icon || ''] || null}</span>
      <span className="text-sm font-medium">{item.label}</span>
      {item.badge && (
        <span className="ml-auto px-2 py-0.5 text-xs font-medium bg-violet-600 text-white rounded-full">
          {item.badge}
        </span>
      )}
    </Link>
  );
}

export function SpSidebar({ className, variant = 'default' }: SidebarProps) {
  const location = useLocation();
  const isActive = (href: string) => location.pathname === href;

  if (variant === 'admin') {
    return (
      <aside
        className={clsx(
          'w-64 h-[calc(100vh-64px)] sticky top-16',
          'bg-slate-900/50 border-r border-slate-700/50',
          'overflow-y-auto',
          className
        )}
      >
        <nav className="p-4 space-y-6">
          {/* Admin Main Nav */}
          <div className="space-y-1">
            {adminMainNavItems.map((item) => (
              <NavItem key={item.href} item={item} isActive={isActive(item.href)} />
            ))}
          </div>

          {/* Console Section */}
          <div>
            <h3 className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Console
            </h3>
            <div className="space-y-1">
              {adminConsoleNavItems.map((item) => (
                <NavItem key={item.href} item={item} isActive={isActive(item.href)} />
              ))}
            </div>
          </div>

          {/* Other Section */}
          <div>
            <h3 className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Other
            </h3>
            <div className="space-y-1">
              {adminOtherNavItems.map((item) => (
                <NavItem key={item.href} item={item} isActive={isActive(item.href)} />
              ))}
            </div>
          </div>
        </nav>
      </aside>
    );
  }

  return (
    <aside
      className={clsx(
        'w-64 h-[calc(100vh-64px)] sticky top-16',
        'bg-slate-900/50 border-r border-slate-700/50',
        'overflow-y-auto',
        className
      )}
    >
      <nav className="p-4 space-y-6">
        {/* Main Nav */}
        <div className="space-y-1">
          {mainNavItems.map((item) => (
            <NavItem key={item.href} item={item} isActive={isActive(item.href)} />
          ))}
        </div>

        {/* Trading Section */}
        <div>
          <h3 className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Trading
          </h3>
          <div className="space-y-1">
            {tradingNavItems.map((item) => (
              <NavItem key={item.href} item={item} isActive={isActive(item.href)} />
            ))}
          </div>
        </div>

        {/* Other Section */}
        <div>
          <h3 className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Other
          </h3>
          <div className="space-y-1">
            {otherNavItems.map((item) => (
              <NavItem key={item.href} item={item} isActive={isActive(item.href)} />
            ))}
          </div>
        </div>
      </nav>
    </aside>
  );
}
