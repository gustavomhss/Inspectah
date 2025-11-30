import type { ReactNode } from 'react';
import { colors, radius, shadows } from '../tokens';

interface TableProps {
  headers?: string[];
  children: ReactNode;
  emptyState?: ReactNode;
  isEmpty?: boolean;
}

export function Table({ headers, children, emptyState, isEmpty = false }: TableProps) {
  return (
    <div
      className="overflow-hidden border border-slate-800/70 bg-slate-900/50"
      style={{ borderRadius: radius.lg, boxShadow: shadows.soft, color: colors.textPrimary }}
    >
      <table className="min-w-full text-left text-sm">
        {headers && (
          <thead className="bg-slate-900/60 text-slate-300">
            <tr>
              {headers.map((header) => (
                <th key={header} className="px-4 py-3 font-semibold">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody className="divide-y divide-slate-800/70">
          {children}
          {isEmpty && emptyState && (
            <tr>
              <td className="px-4 py-3 text-slate-400" colSpan={headers?.length ?? 1}>
                {emptyState}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
