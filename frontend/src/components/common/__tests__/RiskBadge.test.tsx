import { render, screen } from '@testing-library/react';

import { RiskBadge } from '../RiskBadge';

describe('RiskBadge', () => {
  it.each([
    ['NORMAL', 'NORMAL', 'Normal'],
    ['ATENCAO', 'ATENÇÃO', 'Atenção'],
    ['ALERTA', 'ALERTA', 'Alerta'],
    ['EMERGENCIA', 'EMERGÊNCIA', 'Emergência'],
  ] as const)(
    'renderiza %s com texto e nome acessível',
    (nivel, texto, nome) => {
      render(<RiskBadge nivel={nivel} />);

      const badge = screen.getByRole('status');
      expect(badge).toHaveTextContent(texto);
      expect(badge).toHaveAccessibleName(
        expect.stringContaining(`Classificação de risco: ${nome}`),
      );
    },
  );

  it('aplica pulso somente ao estado de emergência', () => {
    const { rerender } = render(<RiskBadge nivel="NORMAL" />);
    expect(screen.getByRole('status')).not.toHaveClass('animate-pulse');

    rerender(<RiskBadge nivel="EMERGENCIA" />);
    expect(screen.getByRole('status')).toHaveClass(
      'animate-pulse',
      'motion-reduce:animate-none',
    );
  });

  it('aceita os três tamanhos', () => {
    const { rerender } = render(<RiskBadge nivel="NORMAL" size="sm" />);
    expect(screen.getByRole('status')).toHaveClass('text-[10px]');

    rerender(<RiskBadge nivel="NORMAL" size="md" />);
    expect(screen.getByRole('status')).toHaveClass('text-xs');

    rerender(<RiskBadge nivel="NORMAL" size="lg" />);
    expect(screen.getByRole('status')).toHaveClass('text-sm');
  });
});
