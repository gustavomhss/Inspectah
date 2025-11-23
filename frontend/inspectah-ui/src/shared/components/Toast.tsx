import type { ReactNode } from 'react';

interface ToastProps {
  title: string;
  description?: ReactNode;
  tone?: 'info' | 'success' | 'warning' | 'danger';
}

const toneClass = {
  info: 'border-sky-400/50 bg-sky-500/10 text-sky-100',
  success: 'border-emerald-400/50 bg-emerald-500/10 text-emerald-100',
  warning: 'border-amber-400/50 bg-amber-500/10 text-amber-100',
  danger: 'border-rose-400/50 bg-rose-500/10 text-rose-100',
};

function Toast({ title, description, tone = 'info' }: ToastProps) {
  return (
    <div className={`rounded-xl border px-4 py-3 text-sm shadow-card ${toneClass[tone]}`}>
      <p className="font-semibold">{title}</p>
      {description ? <div className="mt-1 text-slate-100/90">{description}</div> : null}
    </div>
  );
}

export default Toast;
