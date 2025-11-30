import type { ReactNode } from 'react';
import { colors, radius } from '../tokens';

type BadgeTone = 'neutral' | 'success' | 'warning' | 'danger' | 'info';

interface BadgeProps {
  tone?: BadgeTone;
  children: ReactNode;
}

const toneStyles: Record<BadgeTone, { bg: string; text: string; border: string }> = {
  neutral: { bg: 'bg-slate-800/80', text: 'text-slate-200', border: 'border-slate-700' },
  success: { bg: 'bg-emerald-900/60', text: 'text-emerald-200', border: 'border-emerald-700' },
  warning: { bg: 'bg-amber-900/60', text: 'text-amber-100', border: 'border-amber-700' },
  danger: { bg: 'bg-red-900/60', text: 'text-red-100', border: 'border-red-700' },
  info: { bg: 'bg-sky-900/60', text: 'text-sky-100', border: 'border-sky-700' },
};

export function Badge({ tone = 'neutral', children }: BadgeProps) {
  const styles = toneStyles[tone];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-semibold ${styles.bg} ${styles.text} ${styles.border}`}
      style={{ borderRadius: radius.pill, color: colors.textPrimary }}
    >
      {children}
    </span>
  );
}
