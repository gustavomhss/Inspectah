import { useCallback, useMemo, useState } from 'react';
import type { ToastVariant } from '../components/Toast';

export interface ToastMessage {
  id: string;
  title: string;
  description?: string;
  variant?: ToastVariant;
}

const buildId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

export function useToast() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const pushToast = useCallback((toast: Omit<ToastMessage, 'id'>) => {
    setToasts((current) => [...current, { ...toast, id: buildId() }]);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const api = useMemo(
    () => ({
      toasts,
      pushToast,
      dismissToast,
      clear: () => setToasts([]),
    }),
    [toasts, pushToast, dismissToast],
  );

  return api;
}
