import { HTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'gradient' | 'bordered';
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const variantStyles = {
  default: 'bg-slate-900/80',
  glass: 'bg-slate-900/40 backdrop-blur-xl',
  gradient: 'bg-gradient-to-br from-slate-900 via-slate-900/95 to-violet-900/20',
  bordered: 'bg-slate-900/60 border border-slate-700/50',
};

const paddingStyles = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const SpCard = forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', hover = false, padding = 'md', className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          'rounded-xl',
          variantStyles[variant],
          paddingStyles[padding],
          hover && 'transition-all duration-300 hover:shadow-xl hover:shadow-violet-500/10 hover:-translate-y-1',
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

SpCard.displayName = 'SpCard';

// Stat Card
interface StatCardProps {
  label: string;
  value: string | number;
  change?: number;
  changePercent?: number;
  icon?: React.ReactNode;
  prefix?: string;
}

export function SpStatCard({ label, value, change, changePercent, icon, prefix = '$' }: StatCardProps) {
  const isPositive = (change ?? 0) >= 0;
  const formattedValue = typeof value === 'number'
    ? `${prefix}${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : value;

  return (
    <SpCard variant="gradient" className="relative overflow-hidden">
      {icon && (
        <div className="absolute top-4 right-4 text-violet-500/20">
          {icon}
        </div>
      )}
      <p className="text-sm text-slate-400 mb-1">{label}</p>
      <p className="text-2xl font-bold text-white mb-2">{formattedValue}</p>
      {(change !== undefined || changePercent !== undefined) && (
        <div className={clsx('flex items-center gap-1 text-sm', isPositive ? 'text-emerald-400' : 'text-red-400')}>
          <svg
            className={clsx('w-4 h-4', !isPositive && 'rotate-180')}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
          <span>
            {changePercent !== undefined ? `${changePercent.toFixed(2)}%` : change?.toFixed(2)}
          </span>
        </div>
      )}
    </SpCard>
  );
}

// Player Card
import type { SpPlayer } from '../../types';

interface PlayerCardProps {
  player: SpPlayer;
  onClick?: () => void;
  showActions?: boolean;
}

export function SpPlayerCard({ player, onClick, showActions = false }: PlayerCardProps) {
  const isPositive = player.priceChange >= 0;

  return (
    <SpCard
      variant="bordered"
      hover
      padding="none"
      className="cursor-pointer overflow-hidden"
      onClick={onClick}
    >
      <div className="relative">
        {/* Player Image */}
        <div className="h-48 bg-gradient-to-br from-violet-600/20 to-cyan-600/20 flex items-end justify-center">
          {player.avatar ? (
            <img src={player.avatar} alt={player.name} className="h-40 object-contain" />
          ) : (
            <div className="h-40 w-32 bg-slate-700 rounded-t-lg flex items-center justify-center text-4xl text-slate-500">
              {player.firstName[0]}{player.lastName[0]}
            </div>
          )}
        </div>

        {/* Price Badge */}
        <div className="absolute top-3 right-3 bg-slate-900/90 backdrop-blur px-3 py-1 rounded-full">
          <span className="text-white font-bold">${player.price.toFixed(2)}</span>
        </div>
      </div>

      <div className="p-4">
        {/* Team */}
        <p className="text-xs text-violet-400 uppercase tracking-wide mb-1">{player.team}</p>

        {/* Name */}
        <h3 className="text-lg font-bold text-white mb-2">{player.name}</h3>

        {/* Price Change */}
        <div className={clsx('flex items-center gap-1 text-sm', isPositive ? 'text-emerald-400' : 'text-red-400')}>
          <svg
            className={clsx('w-3 h-3', !isPositive && 'rotate-180')}
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 4l-8 8h5v8h6v-8h5z" />
          </svg>
          <span>
            {isPositive ? '+' : ''}{player.priceChange.toFixed(2)} ({player.priceChangePercent.toFixed(1)}%)
          </span>
        </div>

        {/* Actions */}
        {showActions && (
          <div className="flex gap-2 mt-4">
            <button className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors">
              Buy
            </button>
            <button className="flex-1 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-lg transition-colors">
              Sell
            </button>
          </div>
        )}
      </div>
    </SpCard>
  );
}

// Testimonial Card
import type { SpTestimonial } from '../../types';

interface TestimonialCardProps {
  testimonial: SpTestimonial;
}

export function SpTestimonialCard({ testimonial }: TestimonialCardProps) {
  return (
    <SpCard variant="glass" className="relative">
      {/* Quote Icon */}
      <svg
        className="absolute top-4 right-4 w-8 h-8 text-violet-500/20"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
      </svg>

      {/* Content */}
      <p className="text-slate-300 mb-6 leading-relaxed">{testimonial.text}</p>

      {/* Author */}
      <div className="flex items-center gap-3">
        {testimonial.avatar ? (
          <img
            src={testimonial.avatar}
            alt={testimonial.name}
            className="w-12 h-12 rounded-full object-cover"
          />
        ) : (
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center text-white font-bold">
            {testimonial.name[0]}
          </div>
        )}
        <div>
          <p className="font-semibold text-white">{testimonial.name}</p>
          <p className="text-sm text-slate-400">{testimonial.location}</p>
        </div>
      </div>

      {/* Rating */}
      <div className="flex gap-1 mt-4">
        {[...Array(5)].map((_, i) => (
          <svg
            key={i}
            className={clsx('w-4 h-4', i < testimonial.rating ? 'text-yellow-400' : 'text-slate-600')}
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        ))}
      </div>
    </SpCard>
  );
}

// Team Member Card
import type { SpTeamMember } from '../../types';

interface TeamMemberCardProps {
  member: SpTeamMember;
}

export function SpTeamMemberCard({ member }: TeamMemberCardProps) {
  return (
    <SpCard variant="bordered" hover className="text-center">
      {member.avatar ? (
        <img
          src={member.avatar}
          alt={member.name}
          className="w-24 h-24 rounded-full mx-auto mb-4 object-cover"
        />
      ) : (
        <div className="w-24 h-24 rounded-full mx-auto mb-4 bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center text-3xl text-white font-bold">
          {member.name.split(' ').map(n => n[0]).join('')}
        </div>
      )}
      <h3 className="text-lg font-bold text-white mb-1">{member.name}</h3>
      <p className="text-sm text-violet-400">{member.role}</p>
      {member.bio && <p className="text-sm text-slate-400 mt-3">{member.bio}</p>}
    </SpCard>
  );
}
