import type { ReactNode } from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import toast from 'react-hot-toast';
import { FormOcorrencia } from '../FormOcorrencia';
import * as api from '@/services/api';

vi.mock('react-hot-toast');

describe('FormOcorrencia', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    });
    vi.restoreAllMocks();
  });

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('valida tamanho mínimo dos campos antes de enviar', () => {
    const onConcluir = vi.fn();
    render(<FormOcorrencia estacaoId="est-1" onConcluir={onConcluir} />, {
      wrapper,
    });

    const localizacaoInput = screen.getByLabelText(/localização/i);
    const descricaoInput = screen.getByLabelText(/descrição/i);
    const submitBtn = screen.getByRole('button', {
      name: /registrar ocorrência/i,
    });

    fireEvent.change(localizacaoInput, { target: { value: 'Rua' } });
    fireEvent.change(descricaoInput, { target: { value: 'Água subindo' } });
    fireEvent.click(submitBtn);

    expect(toast.error).toHaveBeenCalledWith(
      'Localização deve ter no mínimo 5 caracteres.',
    );
  });

  it('envia a ocorrência com sucesso e chama onConcluir', async () => {
    const onConcluir = vi.fn();
    vi.spyOn(api, 'criarOcorrencia').mockResolvedValue({} as api.OcorrenciaItem);

    render(<FormOcorrencia estacaoId="est-1" onConcluir={onConcluir} />, {
      wrapper,
    });

    fireEvent.change(screen.getByLabelText(/localização/i), {
      target: { value: 'Rua Principal, 120 — Centro' },
    });
    fireEvent.change(screen.getByLabelText(/descrição/i), {
      target: { value: 'Nível da água cobriu o meio-fio.' },
    });
    fireEvent.click(
      screen.getByRole('button', { name: /registrar ocorrência/i }),
    );

    await waitFor(() => {
      expect(api.criarOcorrencia).toHaveBeenCalledWith({
        estacao_id: 'est-1',
        alerta_id: undefined,
        localizacao: 'Rua Principal, 120 — Centro',
        descricao: 'Nível da água cobriu o meio-fio.',
      });
      expect(toast.success).toHaveBeenCalledWith(
        'Ocorrência registrada com sucesso!',
      );
      expect(onConcluir).toHaveBeenCalled();
    });
  });

  it('chama onConcluir ao clicar em Cancelar', () => {
    const onConcluir = vi.fn();
    render(<FormOcorrencia estacaoId="est-1" onConcluir={onConcluir} />, {
      wrapper,
    });

    fireEvent.click(screen.getByRole('button', { name: /cancelar/i }));
    expect(onConcluir).toHaveBeenCalledTimes(1);
  });
});
