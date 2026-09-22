import { AlertTriangle } from 'lucide-react';
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      this.props.fallback ?? (
        <div
          className="flex min-h-52 flex-col items-center justify-center p-8 text-center"
          role="alert"
        >
          <AlertTriangle
            className="mb-4 size-12 text-red-600 dark:text-red-400"
            aria-hidden="true"
          />
          <h2 className="mb-2 text-xl font-bold text-slate-800 dark:text-slate-100">
            Algo deu errado
          </h2>
          <p className="mb-4 text-sm text-slate-600 dark:text-slate-300">
            {this.state.error?.message ??
              'Erro inesperado ao renderizar este componente.'}
          </p>
          <button
            type="button"
            onClick={() => this.setState({ hasError: false, error: null })}
            className="rounded-lg bg-brand-dark px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-800 focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 dark:focus:ring-offset-slate-900"
          >
            Tentar novamente
          </button>
        </div>
      )
    );
  }
}
