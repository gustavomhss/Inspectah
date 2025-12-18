import { useState, ReactNode } from 'react';
import { clsx } from 'clsx';

interface AccordionItemProps {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
}

export function SpAccordionItem({ title, children, defaultOpen = false }: AccordionItemProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-slate-700/50 last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between py-4 text-left hover:text-violet-400 transition-colors"
      >
        <span className="font-medium text-white">{title}</span>
        <svg
          className={clsx(
            'w-5 h-5 text-slate-400 transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div
        className={clsx(
          'overflow-hidden transition-all duration-200',
          isOpen ? 'max-h-96 pb-4' : 'max-h-0'
        )}
      >
        <div className="text-slate-400 leading-relaxed">{children}</div>
      </div>
    </div>
  );
}

interface AccordionProps {
  children: ReactNode;
  className?: string;
}

export function SpAccordion({ children, className }: AccordionProps) {
  return (
    <div className={clsx('bg-slate-900/50 rounded-xl p-4 border border-slate-700/50', className)}>
      {children}
    </div>
  );
}

// FAQ Accordion with categories
import type { SpFaqItem } from '../../types';

interface FaqAccordionProps {
  items: SpFaqItem[];
  category?: string;
}

export function SpFaqAccordion({ items, category }: FaqAccordionProps) {
  const filteredItems = category ? items.filter((item) => item.category === category) : items;

  return (
    <SpAccordion>
      {filteredItems.map((item) => (
        <SpAccordionItem key={item.id} title={item.question}>
          {item.answer}
        </SpAccordionItem>
      ))}
    </SpAccordion>
  );
}
