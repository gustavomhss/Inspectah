import { useState, useRef, useEffect, ReactNode } from 'react';
import { clsx } from 'clsx';

interface DropdownProps {
  trigger: ReactNode;
  children: ReactNode;
  align?: 'left' | 'right';
  className?: string;
}

export function SpDropdown({ trigger, children, align = 'left', className }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={dropdownRef} className={clsx('relative', className)}>
      <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>
      {isOpen && (
        <div
          className={clsx(
            'absolute z-50 mt-2 min-w-[200px] py-2',
            'bg-slate-800 border border-slate-700 rounded-lg shadow-xl',
            'animate-fade-in',
            align === 'right' ? 'right-0' : 'left-0'
          )}
        >
          {children}
        </div>
      )}
    </div>
  );
}

interface DropdownItemProps {
  children: ReactNode;
  onClick?: () => void;
  icon?: ReactNode;
  danger?: boolean;
  disabled?: boolean;
}

export function SpDropdownItem({ children, onClick, icon, danger = false, disabled = false }: DropdownItemProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'w-full flex items-center gap-3 px-4 py-2 text-sm text-left transition-colors',
        danger
          ? 'text-red-400 hover:bg-red-400/10'
          : 'text-slate-300 hover:bg-slate-700 hover:text-white',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      {icon && <span className="w-5 h-5 flex-shrink-0">{icon}</span>}
      {children}
    </button>
  );
}

export function SpDropdownDivider() {
  return <div className="my-2 border-t border-slate-700" />;
}

// Language Selector Dropdown
interface Language {
  code: string;
  name: string;
  flag?: string;
}

interface LanguageSelectorProps {
  languages: Language[];
  selected: string;
  onChange: (code: string) => void;
}

export function SpLanguageSelector({ languages, selected, onChange }: LanguageSelectorProps) {
  const selectedLang = languages.find((l) => l.code === selected);

  return (
    <SpDropdown
      align="right"
      trigger={
        <button className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-white transition-colors">
          {selectedLang?.flag && <span>{selectedLang.flag}</span>}
          <span>{selectedLang?.name || selected}</span>
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      }
    >
      {languages.map((lang) => (
        <SpDropdownItem key={lang.code} onClick={() => onChange(lang.code)}>
          <span className="flex items-center gap-2">
            {lang.flag && <span>{lang.flag}</span>}
            <span>{lang.name}</span>
          </span>
        </SpDropdownItem>
      ))}
    </SpDropdown>
  );
}

// User Menu Dropdown
interface UserMenuProps {
  user: {
    name: string;
    email: string;
    avatar?: string;
    balance: number;
  };
  onProfile: () => void;
  onSettings: () => void;
  onLogout: () => void;
}

export function SpUserMenu({ user, onProfile, onSettings, onLogout }: UserMenuProps) {
  return (
    <SpDropdown
      align="right"
      trigger={
        <button className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors">
          {user.avatar ? (
            <img src={user.avatar} alt={user.name} className="w-9 h-9 rounded-full" />
          ) : (
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center text-white text-sm font-bold">
              {user.name[0]}
            </div>
          )}
          <div className="text-left hidden sm:block">
            <p className="text-sm font-medium text-white">{user.name}</p>
            <p className="text-xs text-slate-400">${user.balance.toFixed(2)}</p>
          </div>
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      }
    >
      <div className="px-4 py-3 border-b border-slate-700">
        <p className="text-sm font-medium text-white">{user.name}</p>
        <p className="text-xs text-slate-400">{user.email}</p>
      </div>
      <div className="py-1">
        <SpDropdownItem
          onClick={onProfile}
          icon={
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          }
        >
          Profile
        </SpDropdownItem>
        <SpDropdownItem
          onClick={onSettings}
          icon={
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          }
        >
          Settings
        </SpDropdownItem>
      </div>
      <SpDropdownDivider />
      <SpDropdownItem
        onClick={onLogout}
        danger
        icon={
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        }
      >
        Log Out
      </SpDropdownItem>
    </SpDropdown>
  );
}
