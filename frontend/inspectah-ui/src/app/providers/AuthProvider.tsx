import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { setUnauthorizedHandler } from '../../core/api/http-client';
import { clearSession, loadSession, login as loginService, logout as logoutService, saveSession } from '../../core/auth/auth-service';
import type { AuthSession, LoginCredentials } from '../../core/auth/auth-types';

interface AuthContextValue {
  user: AuthSession['user'] | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<AuthSession>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(() => loadSession());

  const handleLogin = useCallback(async (credentials: LoginCredentials) => {
    const nextSession = await loginService(credentials);
    saveSession(nextSession);
    setSession(nextSession);
    return nextSession;
  }, []);

  const handleLogout = useCallback(async () => {
    await logoutService();
    clearSession();
    setSession(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(async () => {
      await logoutService();
      setSession(null);
    });
    return () => {
      setUnauthorizedHandler(null);
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: session?.user ?? null,
      token: session?.token ?? null,
      isAuthenticated: Boolean(session?.token),
      login: handleLogin,
      logout: handleLogout,
    }),
    [handleLogin, handleLogout, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return ctx;
}
