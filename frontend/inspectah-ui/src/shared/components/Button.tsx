import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
}

const variantClass: Record<Variant, string> = {
  primary: 'bg-sky-500 text-white hover:bg-sky-400 focus-visible:outline-sky-200',
  secondary: 'bg-white/10 text-white hover:bg-white/20 focus-visible:outline-white',
  ghost: 'bg-transparent text-white hover:bg-white/10 focus-visible:outline-white',
};

function Button({ children, variant = 'primary', iconLeft, iconRight, className = '', ...props }: ButtonProps) {
  return (
    <button
      type="button"
      className={`inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${variantClass[variant]} ${className}`}
      {...props}
    >
      {iconLeft}
      {children}
      {iconRight}
    </button>
  );
}

export default Button;
