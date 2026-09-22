import { useId, type ReactNode } from 'react';

interface PanelProps {
  children: ReactNode;
  title?: string;
  className?: string;
  id?: string;
}

export function Panel({ children, title, className = '', id }: PanelProps) {
  const generatedId = useId();
  const titleId = `${id ?? generatedId}-title`;

  return (
    <section
      id={id}
      aria-labelledby={title ? titleId : undefined}
      className={`rounded-xl border border-slate-200 bg-white p-6 shadow-card transition-colors duration-200 dark:border-slate-700 dark:bg-slate-800 ${className}`}
    >
      {title ? (
        <h2
          id={titleId}
          className="mb-4 text-lg font-semibold text-slate-800 dark:text-slate-100"
        >
          {title}
        </h2>
      ) : null}
      {children}
    </section>
  );
}
