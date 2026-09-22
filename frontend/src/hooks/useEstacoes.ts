import { useQuery } from '@tanstack/react-query';
import { fetchStatusAtual, type EstacoesStatusResponse } from '@/services/api';

export const useEstacoes = () =>
  useQuery<EstacoesStatusResponse[]>({
    queryKey: ['estacoes', 'status-atual'],
    queryFn: async () => {
      const data = await fetchStatusAtual();
      return Array.isArray(data) ? data : [];
    },
    refetchInterval: 30_000,
  });
