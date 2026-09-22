import { fireEvent, render, screen } from '@testing-library/react';
import { vi } from 'vitest';

import { ErrorBoundary } from '../ErrorBoundary';

describe('ErrorBoundary', () => {
  let shouldThrow = true;
  const preventExpectedError = (event: ErrorEvent) => event.preventDefault();

  function UnstableContent() {
    if (shouldThrow) throw new Error('Falha controlada');
    return <p>Conteúdo restaurado</p>;
  }

  beforeEach(() => {
    shouldThrow = true;
    window.addEventListener('error', preventExpectedError);
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
  });

  afterEach(() => {
    window.removeEventListener('error', preventExpectedError);
    vi.restoreAllMocks();
  });

  it('captura o erro e permite tentar novamente', () => {
    render(
      <ErrorBoundary>
        <UnstableContent />
      </ErrorBoundary>,
    );

    expect(screen.getByRole('alert')).toHaveTextContent('Falha controlada');
    shouldThrow = false;
    fireEvent.click(screen.getByRole('button', { name: 'Tentar novamente' }));
    expect(screen.getByText('Conteúdo restaurado')).toBeInTheDocument();
  });

  it('aceita fallback personalizado', () => {
    render(
      <ErrorBoundary fallback={<p>Fallback seguro</p>}>
        <UnstableContent />
      </ErrorBoundary>,
    );

    expect(screen.getByText('Fallback seguro')).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
