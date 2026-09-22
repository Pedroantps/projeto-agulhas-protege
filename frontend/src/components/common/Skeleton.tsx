interface SkeletonProps {
  width?: string;
  height?: string;
  rounded?: 'sm' | 'md' | 'lg' | 'full' | 'xl';
  className?: string;
}

const ROUNDED_CLASSES = {
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  full: 'rounded-full',
  xl: 'rounded-xl',
};

export function Skeleton({
  width = 'w-full',
  height = 'h-4',
  rounded = 'md',
  className = '',
}: SkeletonProps) {
  return (
    <div
      className={`${width} ${height} ${ROUNDED_CLASSES[rounded]} animate-pulse bg-slate-200 motion-reduce:animate-none dark:bg-slate-700 ${className}`}
      aria-hidden="true"
    />
  );
}

export function CardSkeleton() {
  return (
    <div
      className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800"
      role="status"
      aria-label="Carregando informações do cartão"
      aria-busy="true"
    >
      <div className="flex justify-between">
        <div className="space-y-2">
          <Skeleton width="w-40" height="h-5" />
          <Skeleton width="w-24" height="h-3" />
        </div>
        <Skeleton width="w-20" height="h-6" rounded="full" />
      </div>
      <Skeleton width="w-28" height="h-10" />
      <div className="border-t border-slate-100 pt-4 dark:border-slate-700">
        <Skeleton width="w-32" height="h-3" />
      </div>
    </div>
  );
}

export function PageSkeleton() {
  return (
    <main
      className="min-h-screen space-y-6 bg-slate-50 p-6 dark:bg-slate-900"
      role="status"
      aria-label="Carregando página"
      aria-busy="true"
    >
      <Skeleton width="w-48" height="h-8" />
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <CardSkeleton key={index} />
        ))}
      </div>
    </main>
  );
}
