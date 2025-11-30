import type { ReactNode } from 'react';

interface FormFieldProps {
  label: string;
  description?: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
}

export function FormField({ label, description, error, required = false, children }: FormFieldProps) {
  return (
    <label className="flex flex-col gap-1 text-sm text-slate-200">
      <span className="font-semibold text-slate-100">
        {label}
        {required && <span className="ml-1 text-red-400">*</span>}
      </span>
      {description && <span className="text-xs text-slate-400">{description}</span>}
      {children}
      {error && <span className="text-xs text-red-400">{error}</span>}
    </label>
  );
}
