import { clsx } from 'clsx';
import { useSpTheme } from '../../context/ThemeContext';

interface ThemeToggleProps {
  className?: string;
}

export function SpThemeToggle({ className }: ThemeToggleProps) {
  const { theme, toggleTheme } = useSpTheme();

  return (
    <button
      onClick={toggleTheme}
      className={clsx(
        'flex items-center gap-2 px-3 py-2 rounded-lg',
        'text-sm text-slate-400 hover:text-white',
        'bg-slate-800/50 hover:bg-slate-800',
        'transition-colors',
        className
      )}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {/* Sun Icon */}
      <svg
        className={clsx(
          'w-4 h-4 transition-all',
          theme === 'light' ? 'text-yellow-400' : 'text-slate-500'
        )}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
        />
      </svg>

      <span className="text-xs font-medium uppercase tracking-wide">
        {theme === 'dark' ? 'Light' : 'Dark'}
      </span>

      {/* Moon Icon */}
      <svg
        className={clsx(
          'w-4 h-4 transition-all',
          theme === 'dark' ? 'text-violet-400' : 'text-slate-500'
        )}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
        />
      </svg>
    </button>
  );
}

// Simple Icon-only toggle
export function SpThemeToggleIcon({ className }: ThemeToggleProps) {
  const { theme, toggleTheme } = useSpTheme();

  return (
    <button
      onClick={toggleTheme}
      className={clsx(
        'p-2 rounded-lg',
        'text-slate-400 hover:text-white',
        'hover:bg-slate-800',
        'transition-colors',
        className
      )}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      )}
    </button>
  );
}
