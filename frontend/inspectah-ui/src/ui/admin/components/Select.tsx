import type { SelectHTMLAttributes } from 'react';
import { colors, radius } from '../tokens';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
}

export function Select({ error, className = '', children, ...props }: SelectProps) {
  const errorClasses = error ? 'border-red-500 focus-visible:outline-red-300' : 'border-slate-700 focus-visible:outline-sky-200';

  return (
    <div className="flex flex-col gap-1">
      <select
        className={`w-full rounded-md border bg-slate-900/60 px-3 py-2 text-sm text-slate-50 shadow-sm transition ${errorClasses} ${className}`}
        style={{ borderRadius: radius.md, borderColor: colors.border }}
        {...props}
      >
        {children}
      </select>
      {error && <span className="text-xs text-red-400">{error}</span>}
    </div>
  );
}
