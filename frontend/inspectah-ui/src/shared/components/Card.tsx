import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
}

function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`rounded-2xl border border-white/10 bg-white/5 p-4 shadow-card ${className}`}>
      {children}
    </div>
  );
}

export default Card;
