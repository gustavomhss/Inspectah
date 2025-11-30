import type { ReactNode } from 'react';
import { colors, radius, shadows, zIndex } from '../tokens';
import { Button } from './Button';

interface ModalProps {
  isOpen: boolean;
  title: string;
  description?: string;
  children?: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
  destructive?: boolean;
}

export function Modal({
  isOpen,
  title,
  description,
  children,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  onConfirm,
  onCancel,
  destructive = false,
}: ModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm"
      style={{ zIndex: zIndex.overlay }}
    >
      <div
        className="w-full max-w-lg rounded-xl border border-slate-800/60 bg-slate-900/90 p-6 text-slate-50 shadow-xl"
        style={{ boxShadow: shadows.medium, borderRadius: radius.lg, backgroundColor: colors.surface }}
      >
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-white">{title}</h2>
          {description && <p className="text-sm text-slate-400">{description}</p>}
        </div>
        {children && <div className="mb-6 text-sm text-slate-200">{children}</div>}
        <div className="flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button variant={destructive ? 'danger' : 'primary'} onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
