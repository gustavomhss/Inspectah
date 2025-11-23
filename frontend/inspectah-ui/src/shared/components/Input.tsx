import type { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
}

function Input({ label, helperText, className = '', ...props }: InputProps) {
  return (
    <label className="flex w-full flex-col gap-1 text-sm text-slate-200">
      {label ? <span className="font-semibold text-white">{label}</span> : null}
      <input
        className={`w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-white placeholder:text-slate-400 focus:border-sky-400 focus:outline-none ${className}`}
        {...props}
      />
      {helperText ? <span className="text-xs text-slate-300">{helperText}</span> : null}
    </label>
  );
}

export default Input;
