import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  backLink?: string;
  children?: ReactNode;
}

function PageHeader({ title, subtitle, actions, backLink, children }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div>
        {backLink && (
          <Link to={backLink} className="mb-2 inline-flex items-center text-xs text-sky-300 hover:text-sky-200">
            ← Voltar
          </Link>
        )}
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Inspectah</p>
        <h2 className="mt-1 text-2xl font-bold text-white">{title}</h2>
        {subtitle ? <p className="mt-2 max-w-3xl text-sm text-slate-200">{subtitle}</p> : null}
        {children}
      </div>
      {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
    </div>
  );
}

export default PageHeader;
