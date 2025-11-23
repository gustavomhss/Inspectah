import type { HTMLAttributes, ReactNode } from 'react';

interface TableProps extends HTMLAttributes<HTMLTableElement> {
  children: ReactNode;
}

function Table({ children, className = '', ...props }: TableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-white/10">
      <table className={`min-w-full bg-white/5 text-sm text-slate-100 ${className}`} {...props}>
        {children}
      </table>
    </div>
  );
}

export default Table;
