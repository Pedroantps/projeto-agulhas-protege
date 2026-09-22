import type { ReactNode } from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import toast from 'react-hot-toast';
import { ModalGerenciarCotas } from '../ModalGerenciarCotas';
import * as api from '@/services/api';

vi.mock('react-hot-toast');

describe('ModalGerenciarCotas', () => {
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

  const defaultProps = {
    estacaoId: 'est-1',
    estacaoNome: 'Ponte Velha',
    cotasAtuais: { atencao: 2.2, alerta: 2.7, emergencia: 3.4 },
    aberto: true,
    onFechar: vi.fn(),
  };

  it('não renderiza nada se aberto for false', () => {
    const { container } = render(
      <ModalGerenciarCotas {...defaultProps} aberto={false} />,
      { wrapper },
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('renderiza os campos preenchidos com as cotas atuais', () => {
    render(<ModalGerenciarCotas {...defaultProps} />, { wrapper });

    expect(screen.getByLabelText(/atenção/i)).toHaveValue(2.2);
    expect(screen.getByLabelText(/alerta/i)).toHaveValue(2.7);
    expect(screen.getByLabelText(/emergência/i)).toHaveValue(3.4);
  });

  it('bloqueia envio se a ordem matemática não for respeitada', () => {
    render(<ModalGerenciarCotas {...defaultProps} />, { wrapper });

    // Inverte: Atenção (3.0) maior que Alerta (2.5)
    fireEvent.change(screen.getByLabelText(/atenção/i), {
      target: { value: '3.0' },
    });
    fireEvent.change(screen.getByLabelText(/alerta/i), {
      target: { value: '2.5' },
    });

    fireEvent.click(screen.getByRole('button', { name: /salvar cotas/i }));

    expect(toast.error).toHaveBeenCalledWith(
      'As cotas devem seguir: Atenção < Alerta < Emergência (todas > 0).',
    );
  });

  it('abre o ConfirmModal e executa atualizarCotas após confirmação', async () => {
    const onFechar = vi.fn();
    vi.spyOn(api, 'atualizarCotas').mockResolvedValue(undefined);

    render(
      <ModalGerenciarCotas {...defaultProps} onFechar={onFechar} />,
      { wrapper },
    );

    fireEvent.change(screen.getByLabelText(/atenção/i), {
      target: { value: '2.3' },
    });
    fireEvent.change(screen.getByLabelText(/alerta/i), {
      target: { value: '2.8' },
    });
    fireEvent.change(screen.getByLabelText(/emergência/i), {
      target: { value: '3.5' },
    });

    fireEvent.click(screen.getByRole('button', { name: /salvar cotas/i }));

    // ConfirmModal deve abrir
    expect(
      await screen.findByText('Confirmar alteração de cotas?'),
    ).toBeInTheDocument();

    // Clica em confirmar no modal de confirmação
    fireEvent.click(
      screen.getByRole('button', { name: /confirmar alteração/i }),
    );

    await waitFor(() => {
      expect(api.atualizarCotas).toHaveBeenCalledWith('est-1', {
        cota_atencao: '2.3',
        cota_alerta: '2.8',
        cota_emergencia: '3.5',
      });
      expect(toast.success).toHaveBeenCalledWith(
        'Cotas de risco atualizadas com sucesso.',
      );
      expect(onFechar).toHaveBeenCalled();
    });
  });

  it('fecha o modal ao clicar no botão Cancelar', () => {
    const onFechar = vi.fn();
    render(
      <ModalGerenciarCotas {...defaultProps} onFechar={onFechar} />,
      { wrapper },
    );

    fireEvent.click(screen.getByRole('button', { name: /cancelar/i }));
    expect(onFechar).toHaveBeenCalledTimes(1);
  });
});
