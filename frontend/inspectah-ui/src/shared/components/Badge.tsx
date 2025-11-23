import type { ReactNode } from 'react';

type Tone = 'default' | 'success' | 'warning' | 'danger' | 'info';

const toneClass: Record<Tone, string> = {
  default: 'bg-white/10 text-white',
  success: 'bg-emerald-500/20 text-emerald-100 border border-emerald-400/40',
  warning: 'bg-amber-500/20 text-amber-100 border border-amber-400/40',
  danger: 'bg-rose-500/20 text-rose-100 border border-rose-400/40',
  info: 'bg-sky-500/20 text-sky-100 border border-sky-400/40',
};

interface BadgeProps {
  children: ReactNode;
  tone?: Tone;
}

function Badge({ children, tone = 'default' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${toneClass[tone]}`}>
      {children}
    </span>
  );
}

export default Badge;
