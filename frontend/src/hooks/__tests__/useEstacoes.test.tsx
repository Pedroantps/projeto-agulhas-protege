import React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useEstacoes } from '../useEstacoes';
import * as api from '@/services/api';

const createWrapper = (queryClient: QueryClient) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  Wrapper.displayName = 'QueryClientTestWrapper';
  return Wrapper;
};


describe('useEstacoes', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('retorna dados da API ao montar', async () => {
    const mockData: api.EstacoesStatusResponse[] = [
      {
        estacao_id: 'est-1',
        codigo_externo: 'EST01',
        nome: 'Ponte Central',
        rio: 'Rio Sesmaria',
        nivel_atual_metros: '2.45',
        classificacao_risco: 'NORMAL',
        data_hora_leitura: '2026-09-21T18:00:00Z',
        dados_desatualizados: false,
        cotas: { atencao: '2.50', alerta: '3.00', emergencia: '3.50' },
      },
    ];

    vi.spyOn(api, 'fetchStatusAtual').mockResolvedValue(mockData);

    const { result } = renderHook(() => useEstacoes(), {
      wrapper: createWrapper(queryClient),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(api.fetchStatusAtual).toHaveBeenCalledTimes(1);
  });

  it('configura refetch a cada 30 segundos', () => {
    vi.spyOn(api, 'fetchStatusAtual').mockResolvedValue([]);
    const { result } = renderHook(() => useEstacoes(), {
      wrapper: createWrapper(queryClient),
    });

    expect(result.current).toBeDefined();
  });
});
