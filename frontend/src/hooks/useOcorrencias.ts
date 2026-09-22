import { useQuery } from '@tanstack/react-query';
import { fetchOcorrencias, type OcorrenciaItem } from '@/services/api';

export const useOcorrencias = (estacaoId?: string) =>
  useQuery<OcorrenciaItem[]>({
    queryKey: ['ocorrencias', estacaoId ?? 'todas'],
    queryFn: async () => {
      const data = await fetchOcorrencias(estacaoId);
      return Array.isArray(data) ? data : [];
    },
    refetchInterval: 15_000,
    staleTime: 5_000,
  });
