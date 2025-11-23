import type { ReactNode } from 'react';

interface PageContainerProps {
  children: ReactNode;
  className?: string;
}

function PageContainer({ children, className }: PageContainerProps) {
  return (
    <section
      className={`rounded-2xl border border-white/10 bg-white/5 p-6 shadow-card ${className ? className : ''}`}
    >
      {children}
    </section>
  );
}

export default PageContainer;
