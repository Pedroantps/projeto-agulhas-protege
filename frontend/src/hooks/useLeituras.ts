import { useQuery } from '@tanstack/react-query';
import { fetchHistorico, type LeituraHistorico } from '@/services/api';

export const useLeituras = (estacaoId: string, horas: number) =>
  useQuery<LeituraHistorico[]>({
    queryKey: ['leituras', 'historico', estacaoId, horas],
    queryFn: async () => {
      const data = await fetchHistorico(estacaoId, horas);
      return Array.isArray(data) ? data : [];
    },
    enabled: Boolean(estacaoId),
  });
