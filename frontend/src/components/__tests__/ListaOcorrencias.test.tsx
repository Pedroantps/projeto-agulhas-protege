import type { ReactNode } from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import toast from 'react-hot-toast';
import { ListaOcorrencias } from '../ListaOcorrencias';
import * as api from '@/services/api';

vi.mock('react-hot-toast');

const mockOcorrencias: api.OcorrenciaItem[] = [
  {
    id: 'oco-1',
    estacao_id: 'est-1',
    estacao_nome: 'Estação Parque Ipiranga',
    usuario_nome: 'Carlos Operador',
    localizacao: 'Rua das Flores, 123 — Bairro Ipiranga',
    descricao: 'Nível da água subindo rapidamente, equipe no local.',
    status: 'ABERTA',
    criado_em: '2026-09-21T21:00:00.000Z',
  },
  {
    id: 'oco-2',
    estacao_id: 'est-1',
    estacao_nome: 'Estação Parque Ipiranga',
    usuario_nome: 'Ana Administradora',
    localizacao: 'Avenida Beira Rio, Centro',
    descricao: 'Bueiro transbordando na esquina com ponte velha.',
    status: 'ENCERRADA',
    criado_em: '2026-09-21T20:30:00.000Z',
  },
];

describe('ListaOcorrencias', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    vi.restoreAllMocks();
  });

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('renderiza estado vazio quando não há ocorrências', async () => {
    vi.spyOn(api, 'fetchOcorrencias').mockResolvedValue([]);

    render(<ListaOcorrencias />, { wrapper });

    await waitFor(() => {
      expect(
        screen.getByText(/nenhuma ocorrência registrada até o momento/i),
      ).toBeInTheDocument();
    });
  });

  it('renderiza lista de ocorrências com detalhes corretos', async () => {
    vi.spyOn(api, 'fetchOcorrencias').mockResolvedValue(mockOcorrencias);

    render(<ListaOcorrencias />, { wrapper });

    await waitFor(() => {
      expect(
        screen.getByText('Rua das Flores, 123 — Bairro Ipiranga'),
      ).toBeInTheDocument();
      expect(
        screen.getByText('Nível da água subindo rapidamente, equipe no local.'),
      ).toBeInTheDocument();
      expect(screen.getByText(/Carlos Operador/i)).toBeInTheDocument();
      expect(
        screen.getByText('Avenida Beira Rio, Centro'),
      ).toBeInTheDocument();
    });
  });

  it('permite filtrar por status da ocorrência', async () => {
    vi.spyOn(api, 'fetchOcorrencias').mockResolvedValue(mockOcorrencias);

    render(<ListaOcorrencias />, { wrapper });

    await waitFor(() => {
      expect(
        screen.getByText('Rua das Flores, 123 — Bairro Ipiranga'),
      ).toBeInTheDocument();
    });

    const btnEncerradas = screen.getByRole('button', { name: /encerradas/i });
    fireEvent.click(btnEncerradas);

    expect(
      screen.queryByText('Rua das Flores, 123 — Bairro Ipiranga'),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText('Avenida Beira Rio, Centro'),
    ).toBeInTheDocument();
  });

  it('no modo operador permite atualizar status da ocorrência', async () => {
    vi.spyOn(api, 'fetchOcorrencias').mockResolvedValue(mockOcorrencias);
    vi.spyOn(api, 'atualizarStatusOcorrencia').mockResolvedValue({
      ...mockOcorrencias[0],
      status: 'EM_ANDAMENTO',
    });

    render(<ListaOcorrencias modoOperador={true} />, { wrapper });

    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: /iniciar atendimento/i }),
      ).toBeInTheDocument();
    });

    fireEvent.click(
      screen.getByRole('button', { name: /iniciar atendimento/i }),
    );

    await waitFor(() => {
      expect(api.atualizarStatusOcorrencia).toHaveBeenCalledWith(
        'oco-1',
        'EM_ANDAMENTO',
      );
      expect(toast.success).toHaveBeenCalledWith(
        'Status da ocorrência atualizado para: Em Andamento',
      );
    });
  });
});
