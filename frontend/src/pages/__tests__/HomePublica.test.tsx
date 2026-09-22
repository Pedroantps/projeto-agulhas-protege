import type { ReactNode } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider, type UseQueryResult } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { HomePublica } from '../HomePublica';
import * as hooksEstacoes from '@/hooks/useEstacoes';
import * as hooksLeituras from '@/hooks/useLeituras';
import type {
  EstacoesStatusResponse,
  LeituraHistorico,
} from '@/services/api';

vi.mock('@/hooks/useEstacoes');
vi.mock('@/hooks/useLeituras');
vi.mock('@/hooks/useOcorrencias', () => ({
  useOcorrencias: () => ({ data: [], isLoading: false, error: null }),
}));
vi.mock('@/hooks/useSesmaria', () => ({
  useSesmariaDashboard: () => ({ data: undefined, isLoading: false }),
}));


function mockQueryResult<T>(
  partial: Partial<UseQueryResult<T, Error>>,
): UseQueryResult<T, Error> {
  return partial as UseQueryResult<T, Error>;
}

describe('HomePublica', () => {
  let queryClient: QueryClient;
  const mockRefetch = vi.fn();

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.restoreAllMocks();
    vi.spyOn(hooksLeituras, 'useLeituras').mockReturnValue(
      mockQueryResult<LeituraHistorico[]>({
        data: [
          {
            id: 'l1',
            data_hora: '2026-09-21T12:00:00Z',
            nivel_metros: '1.9',
            classificacao: 'NORMAL',
          },
        ],
        isLoading: false,
        error: null,
      }),
    );
  });

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );


  it('renderiza estações e permite seleção para visualizar gráfico histórico', () => {
    vi.spyOn(hooksEstacoes, 'useEstacoes').mockReturnValue(
      mockQueryResult<EstacoesStatusResponse[]>({
        data: [
          {
            estacao_id: 'est-1',
            codigo_externo: 'EST01',
            nome: 'Ponte Velha',
            rio: 'Rio Sesmaria',
            nivel_atual_metros: '2.10',
            classificacao_risco: 'NORMAL',
            data_hora_leitura: '2026-09-21T12:00:00Z',
            dados_desatualizados: false,
            cotas: { atencao: '2.50', alerta: '3.00', emergencia: '3.50' },
          },
        ],
        isLoading: false,
        error: null,
        refetch: mockRefetch as unknown as UseQueryResult<
          EstacoesStatusResponse[],
          Error
        >['refetch'],
        isFetching: false,
      }),
    );

    render(<HomePublica />, { wrapper });

    expect(screen.getByText('Agulhas Protege')).toBeInTheDocument();
    expect(screen.getByText('Ponte Velha')).toBeInTheDocument();

    // Seleciona o card da estação
    fireEvent.click(screen.getByRole('button', { name: /ponte velha/i }));

    // Seção de histórico deve aparecer
    expect(screen.getByText('Histórico — Ponte Velha')).toBeInTheDocument();

    // Testa os botões de período (7d e 30d)
    const btn7d = screen.getByRole('button', { name: '7d' });
    fireEvent.click(btn7d);
    expect(btn7d).toHaveAttribute('aria-pressed', 'true');
  });

  it('dispara refetch ao clicar no botão de atualizar', () => {
    vi.spyOn(hooksEstacoes, 'useEstacoes').mockReturnValue(
      mockQueryResult<EstacoesStatusResponse[]>({
        data: [],
        isLoading: false,
        error: null,
        refetch: mockRefetch as unknown as UseQueryResult<
          EstacoesStatusResponse[],
          Error
        >['refetch'],
        isFetching: false,
      }),
    );

    render(<HomePublica />, { wrapper });

    fireEvent.click(screen.getByRole('button', { name: /atualizar dados/i }));
    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });

  it('exibe alerta de erro quando houver falha na carga', () => {
    vi.spyOn(hooksEstacoes, 'useEstacoes').mockReturnValue(
      mockQueryResult<EstacoesStatusResponse[]>({
        data: undefined,
        isLoading: false,
        error: new Error('Erro'),
        refetch: mockRefetch as unknown as UseQueryResult<
          EstacoesStatusResponse[],
          Error
        >['refetch'],
        isFetching: false,
      }),
    );

    render(<HomePublica />, { wrapper });


    expect(screen.getByRole('alert')).toHaveTextContent(
      'Não foi possível carregar os dados. Tente atualizar a página.',
    );
  });
});
