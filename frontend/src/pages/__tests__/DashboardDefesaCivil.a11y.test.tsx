import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider, type UseQueryResult } from '@tanstack/react-query';
import { describe, expect, it, vi } from 'vitest';
import { checkA11y } from '@/test-setup';
import { DashboardDefesaCivil } from '../DashboardDefesaCivil';
import * as authHook from '@/hooks/useAuth';
import * as hooksEstacoes from '@/hooks/useEstacoes';
import type { EstacoesStatusResponse } from '@/services/api';

vi.mock('@/hooks/useAuth');
vi.mock('@/hooks/useEstacoes');
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

describe('DashboardDefesaCivil — Acessibilidade', () => {
  it('não tem violações WCAG AA', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.spyOn(authHook, 'useAuth').mockReturnValue({
      user: {
        nome: 'Carlos Operador',
        perfil: 'OPERADOR_DEFESA_CIVIL',
      },
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    });

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
      }),
    );

    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <DashboardDefesaCivil />
        </MemoryRouter>
      </QueryClientProvider>,
    );


    const results = await checkA11y(container);
    expect(results.violations).toEqual([]);
  });
});
