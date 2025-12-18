import type { ReactNode } from 'react';
import { colors, shadows } from '../tokens';

export interface AdminContentProps {
  children: ReactNode;
  maxWidth?: number;
  padded?: boolean;
  className?: string;
  id?: string;
}

export function AdminContent({ children, maxWidth, padded = true, className, id }: AdminContentProps) {
  const baseClass = 'rounded-xl border border-slate-800/70 bg-slate-900/60';
  const finalClass = className ? `${baseClass} ${className}` : baseClass;

  return (
    <div className="flex-1">
      <div
        id={id}
        className={finalClass}
        style={{
          maxWidth: maxWidth ? `${maxWidth}px` : undefined,
          boxShadow: shadows.soft,
          color: colors.textPrimary,
        }}
      >
        <div className={padded ? 'p-6 lg:p-8' : undefined}>{children}</div>
      </div>
    </div>
  );
}
