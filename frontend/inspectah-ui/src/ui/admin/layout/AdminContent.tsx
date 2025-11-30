import type { ReactNode } from 'react';
import { colors, shadows } from '../tokens';

interface AdminContentProps {
  children: ReactNode;
  maxWidth?: number;
  padded?: boolean;
}

export function AdminContent({ children, maxWidth, padded = true }: AdminContentProps) {
  return (
    <div className="flex-1">
      <div
        className="rounded-xl border border-slate-800/70 bg-slate-900/60"
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
