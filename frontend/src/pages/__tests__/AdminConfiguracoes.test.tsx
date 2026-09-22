import type { ReactNode } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminConfiguracoes } from '../AdminConfiguracoes';
import * as authHook from '@/hooks/useAuth';
import * as estacoesHook from '@/hooks/useEstacoes';
import type { EstacoesStatusResponse } from '@/services/api';

vi.mock('@/hooks/useAuth');
vi.mock('@/hooks/useEstacoes');

function mockQueryResult<T>(
  partial: Partial<UseQueryResult<T, Error>>,
): UseQueryResult<T, Error> {
  return partial as UseQueryResult<T, Error>;
}

describe('AdminConfiguracoes', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.restoreAllMocks();
  });

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );

  it('renderiza listagem de estações com cotas e abre o modal de edição', () => {
    vi.spyOn(authHook, 'useAuth').mockReturnValue({
      user: { nome: 'Dra. Mariana Admin', perfil: 'ADMINISTRADOR' },
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.spyOn(estacoesHook, 'useEstacoes').mockReturnValue(
      mockQueryResult<EstacoesStatusResponse[]>({
        data: [
          {
            estacao_id: 'est-1',
            codigo_externo: 'EST01',
            nome: 'Ponte Velha',
            rio: 'Rio Sesmaria',
            nivel_atual_metros: '2.10',
            classificacao_risco: 'NORMAL',
            data_hora_leitura: '2026-09-21T14:00:00Z',
            dados_desatualizados: false,
            cotas: { atencao: '2.20', alerta: '2.70', emergencia: '3.40' },
          },
        ],
        isLoading: false,
        error: null,
      }),
    );

    render(<AdminConfiguracoes />, { wrapper });

    expect(screen.getByText('Dra. Mariana Admin')).toBeInTheDocument();
    expect(screen.getByText('Ponte Velha')).toBeInTheDocument();
    expect(screen.getByText('EST01')).toBeInTheDocument();
    expect(screen.getByText('At: 2.20')).toBeInTheDocument();
    expect(screen.getByText('Al: 2.70')).toBeInTheDocument();
    expect(screen.getByText('Em: 3.40')).toBeInTheDocument();

    // Clica no botão Ajustar Cotas
    fireEvent.click(
      screen.getByRole('button', {
        name: 'Ajustar cotas da estação Ponte Velha',
      }),
    );

    // O modal deve ser aberto
    expect(
      screen.getByRole('dialog', { name: 'Gerenciar Cotas de Risco' }),
    ).toBeInTheDocument();
  });
});
