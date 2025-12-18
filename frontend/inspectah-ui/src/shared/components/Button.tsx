import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'xs' | 'sm' | 'md';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
}

const variantClass: Record<Variant, string> = {
  primary: 'bg-sky-500 text-white hover:bg-sky-400 focus-visible:outline-sky-200',
  secondary: 'bg-white/10 text-white hover:bg-white/20 focus-visible:outline-white',
  ghost: 'bg-transparent text-white hover:bg-white/10 focus-visible:outline-white',
  danger: 'bg-red-600 text-white hover:bg-red-500 focus-visible:outline-red-200',
};

const sizeClass: Record<Size, string> = {
  xs: 'px-2 py-1 text-xs',
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2 text-sm font-semibold',
};

function Button({ children, variant = 'primary', size = 'md', iconLeft, iconRight, className = '', ...props }: ButtonProps) {
  return (
    <button
      type="button"
      className={`inline-flex items-center gap-2 rounded-md transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${variantClass[variant]} ${sizeClass[size]} ${className}`}
      {...props}
    >
      {iconLeft}
      {children}
      {iconRight}
    </button>
  );
}

export default Button;
