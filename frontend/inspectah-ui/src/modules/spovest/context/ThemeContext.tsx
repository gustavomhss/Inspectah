import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { SpTheme } from '../types';

interface ThemeContextValue {
  theme: SpTheme;
  toggleTheme: () => void;
  setTheme: (theme: SpTheme) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

const STORAGE_KEY = 'spovest-theme';

export function SpThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<SpTheme>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'light' || stored === 'dark') {
        return stored;
      }
    }
    return 'dark';
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, theme);
    document.documentElement.setAttribute('data-spovest-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const setTheme = (newTheme: SpTheme) => {
    setThemeState(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useSpTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useSpTheme must be used within a SpThemeProvider');
  }
  return context;
}
