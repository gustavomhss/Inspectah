import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';

interface AuthGuardProps {
  children: ReactNode;
}

// Dev mode bypass - disable auth in development
const DEV_AUTH_BYPASS = import.meta.env.DEV;

export function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  // Bypass auth in development mode
  if (DEV_AUTH_BYPASS) {
    return <>{children}</>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
