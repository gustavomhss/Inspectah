import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { radius } from '../tokens';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'xs' | 'sm' | 'md';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: 'bg-sky-500 text-white hover:bg-sky-400 focus-visible:outline-sky-200',
  secondary: 'bg-white/10 text-white hover:bg-white/20 focus-visible:outline-white',
  ghost: 'bg-transparent text-slate-200 hover:bg-white/5 focus-visible:outline-slate-300',
  danger: 'bg-red-600 text-white hover:bg-red-500 focus-visible:outline-red-200',
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2 text-sm font-semibold',
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  iconLeft,
  iconRight,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  const disabledClasses = disabled ? 'opacity-60 cursor-not-allowed' : '';

  return (
    <button
      type="button"
      className={`inline-flex items-center gap-2 rounded-md transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${variantStyles[variant]} ${sizeStyles[size]} ${disabledClasses} ${className}`}
      style={{ borderRadius: radius.md }}
      disabled={disabled}
      {...props}
    >
      {iconLeft}
      {children}
      {iconRight}
    </button>
  );
}
