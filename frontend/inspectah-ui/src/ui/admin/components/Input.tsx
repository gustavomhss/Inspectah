import type { InputHTMLAttributes } from 'react';
import { colors, radius } from '../tokens';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

export function Input({ error, className = '', ...props }: InputProps) {
  const errorClasses = error ? 'border-red-500 focus-visible:outline-red-300' : 'border-slate-700 focus-visible:outline-sky-200';

  return (
    <div className="flex flex-col gap-1">
      <input
        className={`w-full rounded-md border bg-slate-900/60 px-3 py-2 text-sm text-slate-50 placeholder:text-slate-500 shadow-sm transition ${errorClasses} ${className}`}
        style={{ borderRadius: radius.md, borderColor: colors.border }}
        {...props}
      />
      {error && <span className="text-xs text-red-400">{error}</span>}
    </div>
  );
}
