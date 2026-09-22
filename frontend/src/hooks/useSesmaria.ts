import { useQuery } from '@tanstack/react-query';
import {
  fetchAlertaWhatsApp,
  fetchSesmariaDashboard,
  type SesmariaDashboardResponse,
} from '@/services/api';

export const useSesmariaDashboard = () => {
  return useQuery<SesmariaDashboardResponse>({
    queryKey: ['sesmaria-dashboard'],
    queryFn: fetchSesmariaDashboard,
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
};

export const useAlertaWhatsApp = () => {
  return useQuery({
    queryKey: ['sesmaria-alerta-whatsapp'],
    queryFn: fetchAlertaWhatsApp,
    staleTime: 60_000,
  });
};
