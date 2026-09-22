import { render, screen } from '@testing-library/react';
import type { UseQueryResult } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { GraficoHistorico } from '../GraficoHistorico';
import * as hooks from '@/hooks/useLeituras';
import type { LeituraHistorico } from '@/services/api';

vi.mock('@/hooks/useLeituras');

function mockQueryResult<T>(
  partial: Partial<UseQueryResult<T, Error>>,
): UseQueryResult<T, Error> {
  return partial as UseQueryResult<T, Error>;
}

describe('GraficoHistorico', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('exibe skeleton enquanto carrega', () => {
    vi.spyOn(hooks, 'useLeituras').mockReturnValue(
      mockQueryResult<LeituraHistorico[]>({
        data: undefined,
        isLoading: true,
        error: null,
      }),
    );

    const { container } = render(
      <GraficoHistorico estacaoId="est-1" periodo={24} />,
    );
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('exibe mensagem de erro quando a consulta falha', () => {
    vi.spyOn(hooks, 'useLeituras').mockReturnValue(
      mockQueryResult<LeituraHistorico[]>({
        data: undefined,
        isLoading: false,
        error: new Error('Falha de rede'),
      }),
    );

    render(<GraficoHistorico estacaoId="est-1" periodo={24} />);
    expect(screen.getByRole('alert')).toHaveTextContent(
      'Não foi possível carregar o histórico de leituras.',
    );
  });

  it('exibe mensagem amigável quando não há leituras', () => {
    vi.spyOn(hooks, 'useLeituras').mockReturnValue(
      mockQueryResult<LeituraHistorico[]>({
        data: [],
        isLoading: false,
        error: null,
      }),
    );

    render(<GraficoHistorico estacaoId="est-1" periodo={24} />);
    expect(
      screen.getByText('Nenhuma leitura registrada no período selecionado.'),
    ).toBeInTheDocument();
  });

  it('renderiza os dados e a tabela de acessibilidade quando há leituras', () => {
    vi.spyOn(hooks, 'useLeituras').mockReturnValue(
      mockQueryResult<LeituraHistorico[]>({
        data: [
          {
            id: 'l-1',
            data_hora: '2026-09-21T10:00:00Z',
            nivel_metros: '1.85',
            classificacao: 'NORMAL',
          },
          {
            id: 'l-2',
            data_hora: '2026-09-21T10:15:00Z',
            nivel_metros: '2.05',
            classificacao: 'NORMAL',
          },
        ],
        isLoading: false,
        error: null,
      }),
    );

    render(
      <GraficoHistorico
        estacaoId="est-1"
        periodo={24}
        cotas={{ atencao: '2.50', alerta: '3.00', emergencia: '3.50' }}
      />,
    );

    expect(
      screen.getByText('Ver dados em tabela (acessibilidade)'),
    ).toBeInTheDocument();
    expect(screen.getByText('1.85')).toBeInTheDocument();
    expect(screen.getByText('2.05')).toBeInTheDocument();
  });
});
