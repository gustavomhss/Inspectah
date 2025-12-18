import { clsx } from 'clsx';

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'primary';
type BadgeSize = 'sm' | 'md' | 'lg';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  dot?: boolean;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-slate-700 text-slate-300',
  success: 'bg-emerald-400/10 text-emerald-400',
  warning: 'bg-yellow-400/10 text-yellow-400',
  danger: 'bg-red-400/10 text-red-400',
  info: 'bg-cyan-400/10 text-cyan-400',
  primary: 'bg-violet-400/10 text-violet-400',
};

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
  lg: 'px-3 py-1.5 text-sm',
};

export function SpBadge({ children, variant = 'default', size = 'md', dot = false, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 font-medium rounded-full',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {dot && (
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full',
            variant === 'success' && 'bg-emerald-400',
            variant === 'warning' && 'bg-yellow-400',
            variant === 'danger' && 'bg-red-400',
            variant === 'info' && 'bg-cyan-400',
            variant === 'primary' && 'bg-violet-400',
            variant === 'default' && 'bg-slate-400'
          )}
        />
      )}
      {children}
    </span>
  );
}

// Sport Badge
import type { SpSport } from '../../types';

interface SportBadgeProps {
  sport: SpSport;
  size?: BadgeSize;
}

const sportColors: Record<SpSport, string> = {
  NBA: 'bg-orange-400/10 text-orange-400',
  NFL: 'bg-green-400/10 text-green-400',
  MLB: 'bg-red-400/10 text-red-400',
  NHL: 'bg-blue-400/10 text-blue-400',
  Soccer: 'bg-emerald-400/10 text-emerald-400',
  Golf: 'bg-lime-400/10 text-lime-400',
  ESports: 'bg-purple-400/10 text-purple-400',
};

export function SpSportBadge({ sport, size = 'md' }: SportBadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full',
        sportColors[sport],
        sizeStyles[size]
      )}
    >
      {sport}
    </span>
  );
}

// Price Change Badge
interface PriceChangeBadgeProps {
  change: number;
  changePercent: number;
  size?: BadgeSize;
  showIcon?: boolean;
}

export function SpPriceChangeBadge({ change, changePercent, size = 'md', showIcon = true }: PriceChangeBadgeProps) {
  const isPositive = change >= 0;

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 font-medium rounded-full',
        isPositive ? 'bg-emerald-400/10 text-emerald-400' : 'bg-red-400/10 text-red-400',
        sizeStyles[size]
      )}
    >
      {showIcon && (
        <svg
          className={clsx('w-3 h-3', !isPositive && 'rotate-180')}
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 4l-8 8h5v8h6v-8h5z" />
        </svg>
      )}
      <span>
        {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
      </span>
    </span>
  );
}
