import type { ReactNode } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DashboardDefesaCivil } from '../DashboardDefesaCivil';
import * as authHook from '@/hooks/useAuth';
import * as estacoesHook from '@/hooks/useEstacoes';
import type { EstacoesStatusResponse } from '@/services/api';

vi.mock('@/hooks/useAuth');
vi.mock('@/hooks/useEstacoes');
vi.mock('@/hooks/useSesmaria', () => ({
  useSesmariaDashboard: () => ({ data: undefined, isLoading: false }),
}));


function mockQueryResult<T>(
  partial: Partial<UseQueryResult<T, Error>>,
): UseQueryResult<T, Error> {
  return partial as UseQueryResult<T, Error>;
}

describe('DashboardDefesaCivil', () => {
  let queryClient: QueryClient;
  const mockLogout = vi.fn();

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

  it('renderiza o painel do operador com lista de estações e formulário de ocorrência', () => {
    vi.spyOn(authHook, 'useAuth').mockReturnValue({
      user: { nome: 'Operador Roberto', perfil: 'OPERADOR_DEFESA_CIVIL' },
      isAuthenticated: true,
      login: vi.fn(),
      logout: mockLogout,
    });

    vi.spyOn(estacoesHook, 'useEstacoes').mockReturnValue(
      mockQueryResult<EstacoesStatusResponse[]>({
        data: [
          {
            estacao_id: 'est-1',
            codigo_externo: 'EST01',
            nome: 'Ponte Velha',
            rio: 'Rio Sesmaria',
            nivel_atual_metros: '2.50',
            classificacao_risco: 'ALERTA',
            data_hora_leitura: '2026-09-21T14:00:00Z',
            dados_desatualizados: false,
            cotas: { atencao: '2.00', alerta: '2.50', emergencia: '3.00' },
          },
        ],
        isLoading: false,
        error: null,
      }),
    );

    render(<DashboardDefesaCivil />, { wrapper });

    expect(screen.getByText('Operador Roberto')).toBeInTheDocument();
    expect(screen.getByText('Ponte Velha')).toBeInTheDocument();
    expect(
      screen.queryByTitle('Configurações Administrativas'),
    ).not.toBeInTheDocument();

    // Clica no botão de registrar ocorrência
    fireEvent.click(
      screen.getByRole('button', { name: /\+ registrar ocorrência/i }),
    );

    // O formulário de ocorrência deve ser renderizado
    expect(
      screen.getByRole('form', {
        name: 'Formulário de registro de ocorrência',
      }),
    ).toBeInTheDocument();

    // Clica em sair
    fireEvent.click(screen.getByRole('button', { name: /sair/i }));
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it('exibe link de administração quando o usuário for ADMINISTRADOR', () => {
    vi.spyOn(authHook, 'useAuth').mockReturnValue({
      user: { nome: 'Admin Chefe', perfil: 'ADMINISTRADOR' },
      isAuthenticated: true,
      login: vi.fn(),
      logout: mockLogout,
    });

    vi.spyOn(estacoesHook, 'useEstacoes').mockReturnValue(
      mockQueryResult<EstacoesStatusResponse[]>({
        data: [],
        isLoading: false,
        error: null,
      }),
    );

    render(<DashboardDefesaCivil />, { wrapper });

    expect(
      screen.getByTitle('Configurações Administrativas'),
    ).toBeInTheDocument();
  });
});
