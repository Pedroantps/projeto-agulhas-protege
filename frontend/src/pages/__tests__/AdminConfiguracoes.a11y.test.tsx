import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import type { UseQueryResult } from '@tanstack/react-query';
import { describe, expect, it, vi } from 'vitest';
import { checkA11y } from '@/test-setup';
import { AdminConfiguracoes } from '../AdminConfiguracoes';
import * as authHook from '@/hooks/useAuth';
import * as hooksEstacoes from '@/hooks/useEstacoes';
import type { EstacoesStatusResponse } from '@/services/api';

vi.mock('@/hooks/useAuth');
vi.mock('@/hooks/useEstacoes');
vi.mock('@/components/PainelColeta', () => ({ PainelColeta: () => null }));

function mockQueryResult<T>(
  partial: Partial<UseQueryResult<T, Error>>,
): UseQueryResult<T, Error> {
  return partial as UseQueryResult<T, Error>;
}

describe('AdminConfiguracoes — Acessibilidade', () => {
  it('não tem violações WCAG AA', async () => {
    vi.spyOn(authHook, 'useAuth').mockReturnValue({
      user: {
        nome: 'Ana Administradora',
        perfil: 'ADMINISTRADOR',
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
      <MemoryRouter>
        <AdminConfiguracoes />
      </MemoryRouter>,
    );

    const results = await checkA11y(container);
    expect(results.violations).toEqual([]);
  });
});
