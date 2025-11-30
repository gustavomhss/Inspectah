import type { ReactNode } from 'react';
import { colors, radius } from '../tokens';

type BannerTone = 'info' | 'success' | 'warning' | 'danger';

interface BannerProps {
  tone?: BannerTone;
  title: string;
  description?: string;
  actions?: ReactNode;
}

const toneClasses: Record<BannerTone, string> = {
  info: 'bg-sky-900/40 border-sky-800 text-sky-100',
  success: 'bg-emerald-900/40 border-emerald-800 text-emerald-100',
  warning: 'bg-amber-900/40 border-amber-800 text-amber-50',
  danger: 'bg-red-900/40 border-red-800 text-red-50',
};

export function Banner({ tone = 'info', title, description, actions }: BannerProps) {
  return (
    <div
      className={`flex flex-col gap-2 rounded-lg border px-4 py-3 text-sm ${toneClasses[tone]}`}
      style={{ borderRadius: radius.md, color: colors.textPrimary }}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="font-semibold">{title}</div>
        {actions}
      </div>
      {description && <div className="text-xs text-slate-200">{description}</div>}
    </div>
  );
}
