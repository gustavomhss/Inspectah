import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import { SpButton } from '../ui/Button';
import { SpThemeToggle } from '../ui/ThemeToggle';
import { SpUserMenu } from '../ui/Dropdown';
import type { SpUser, SpNavItem } from '../../types';

interface HeaderProps {
  user?: SpUser | null;
  onLogin?: () => void;
  onSignup?: () => void;
  onLogout?: () => void;
}

const publicNavItems: SpNavItem[] = [
  { label: 'Home', href: '/spovest' },
  { label: 'About Us', href: '/spovest/about' },
  { label: 'How to Play', href: '/spovest/how-to-play' },
  { label: 'FAQ', href: '/spovest/faq' },
  { label: 'Contact Us', href: '/spovest/contact' },
];

export function SpHeader({ user, onLogin, onSignup, onLogout }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const isActive = (href: string) => location.pathname === href;

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/spovest" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 flex items-center justify-center">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <span className="text-xl font-bold text-white hidden sm:block">
              Spovest
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1">
            {publicNavItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={clsx(
                  'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                  isActive(item.href)
                    ? 'text-white bg-slate-800'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Right Side */}
          <div className="flex items-center gap-3">
            <SpThemeToggle className="hidden sm:flex" />

            {user ? (
              <SpUserMenu
                user={{
                  name: user.username,
                  email: user.email,
                  avatar: user.avatar,
                  balance: user.balance,
                }}
                onProfile={() => {}}
                onSettings={() => {}}
                onLogout={onLogout || (() => {})}
              />
            ) : (
              <div className="hidden sm:flex items-center gap-2">
                <SpButton variant="ghost" size="sm" onClick={onLogin}>
                  Log In
                </SpButton>
                <SpButton variant="primary" size="sm" onClick={onSignup}>
                  Sign Up
                </SpButton>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-slate-400 hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-700/50 bg-slate-900">
          <nav className="px-4 py-4 space-y-1">
            {publicNavItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={clsx(
                  'block px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                  isActive(item.href)
                    ? 'text-white bg-slate-800'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                )}
              >
                {item.label}
              </Link>
            ))}
            {!user && (
              <div className="flex gap-2 pt-4 border-t border-slate-700/50 mt-4">
                <SpButton variant="ghost" size="md" fullWidth onClick={onLogin}>
                  Log In
                </SpButton>
                <SpButton variant="primary" size="md" fullWidth onClick={onSignup}>
                  Sign Up
                </SpButton>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}

// Dashboard Header (for logged-in users)
interface DashboardHeaderProps {
  user: SpUser;
  onLogout: () => void;
}

export function SpDashboardHeader({ user, onLogout }: DashboardHeaderProps) {
  return (
    <header className="sticky top-0 z-40 w-full h-16 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-xl">
      <div className="flex items-center justify-between h-full px-6">
        {/* Logo */}
        <Link to="/spovest/dashboard" className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 flex items-center justify-center">
            <span className="text-white font-bold text-xl">S</span>
          </div>
          <span className="text-xl font-bold text-white hidden sm:block">
            Spovest
          </span>
        </Link>

        {/* Sports Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {['NBA', 'NFL', 'MLB', 'NHL', 'Soccer', 'Golf', 'ESports'].map((sport) => (
            <Link
              key={sport}
              to={`/spovest/trade/${sport.toLowerCase()}`}
              className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              {sport}
            </Link>
          ))}
        </nav>

        {/* Right Side */}
        <div className="flex items-center gap-3">
          <SpThemeToggle className="hidden sm:flex" />

          {/* Balance */}
          <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg">
            <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-medium text-white">${user.balance.toFixed(2)}</span>
          </div>

          <SpUserMenu
            user={{
              name: user.username,
              email: user.email,
              avatar: user.avatar,
              balance: user.balance,
            }}
            onProfile={() => {}}
            onSettings={() => {}}
            onLogout={onLogout}
          />
        </div>
      </div>
    </header>
  );
}
