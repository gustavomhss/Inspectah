import type { ReactNode } from 'react';
import { colors, radius, shadows, zIndex } from '../tokens';
import { Button } from './Button';

export type ToastVariant = 'default' | 'success' | 'warning' | 'danger' | 'info';

interface ToastProps {
  title: string;
  description?: string;
  variant?: ToastVariant;
  action?: ReactNode;
  onClose?: () => void;
}

const toneStyles: Record<ToastVariant, string> = {
  default: 'bg-slate-900/90 border-slate-800',
  success: 'bg-emerald-900/80 border-emerald-700',
  warning: 'bg-amber-900/80 border-amber-700',
  danger: 'bg-red-900/80 border-red-700',
  info: 'bg-sky-900/80 border-sky-700',
};

export function Toast({ title, description, variant = 'default', action, onClose }: ToastProps) {
  const styleClasses = toneStyles[variant];

  return (
    <div
      className={`flex w-full max-w-sm items-start gap-3 rounded-lg border px-4 py-3 text-sm shadow-lg ${styleClasses}`}
      style={{ boxShadow: shadows.medium, borderRadius: radius.md, zIndex: zIndex.toast, color: colors.textPrimary }}
    >
      <div className="flex-1">
        <div className="font-semibold text-white">{title}</div>
        {description && <div className="text-slate-200">{description}</div>}
      </div>
      {action}
      {onClose && (
        <Button variant="ghost" size="sm" aria-label="Fechar toast" onClick={onClose}>
          ✕
        </Button>
      )}
    </div>
  );
}
