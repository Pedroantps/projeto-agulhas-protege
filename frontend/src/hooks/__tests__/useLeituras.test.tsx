import React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useLeituras } from '../useLeituras';
import * as api from '@/services/api';

describe('useLeituras', () => {
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

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('retorna leituras históricas da estação', async () => {
    const mockLeituras: api.LeituraHistorico[] = [
      {
        id: 'l-1',
        data_hora: '2026-09-21T18:00:00Z',
        nivel_metros: '2.10',
        classificacao: 'NORMAL',
      },
      {
        id: 'l-2',
        data_hora: '2026-09-21T18:15:00Z',
        nivel_metros: '2.25',
        classificacao: 'NORMAL',
      },
    ];

    vi.spyOn(api, 'fetchHistorico').mockResolvedValue(mockLeituras);

    const { result } = renderHook(() => useLeituras('est-1', 24), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockLeituras);
    expect(api.fetchHistorico).toHaveBeenCalledWith('est-1', 24);
  });

  it('não executa a query se estacaoId estiver vazio', () => {
    const spy = vi.spyOn(api, 'fetchHistorico');
    const { result } = renderHook(() => useLeituras('', 24), { wrapper });

    expect(result.current.fetchStatus).toBe('idle');
    expect(spy).not.toHaveBeenCalled();
  });
});
