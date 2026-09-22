import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import toast from 'react-hot-toast';
import { Login } from '../Login';
import * as authHook from '@/hooks/useAuth';
import { ApiError } from '@/services/api';

vi.mock('react-hot-toast');
vi.mock('@/hooks/useAuth');

describe('Login', () => {
  const mockLogin = vi.fn();

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(authHook, 'useAuth').mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: mockLogin,
      logout: vi.fn(),
    });
  });

  it('renderiza o formulário de login e permite alternar visibilidade da senha', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    const senhaInput = screen.getByLabelText(/^senha$/i);
    expect(senhaInput).toHaveAttribute('type', 'password');

    const toggleBtn = screen.getByRole('button', { name: /mostrar senha/i });
    fireEvent.click(toggleBtn);
    expect(senhaInput).toHaveAttribute('type', 'text');

    fireEvent.click(screen.getByRole('button', { name: /ocultar senha/i }));
    expect(senhaInput).toHaveAttribute('type', 'password');
  });

  it('submete as credenciais e exibe toast de sucesso', async () => {
    mockLogin.mockResolvedValueOnce(undefined);

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText(/e-mail/i), {
      target: { value: 'operador@defesa.rj.gov.br' },
    });
    fireEvent.change(screen.getByLabelText(/^senha$/i), {
      target: { value: 'segredo123' },
    });

    fireEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith(
        'operador@defesa.rj.gov.br',
        'segredo123',
      );
      expect(toast.success).toHaveBeenCalledWith('Login realizado com sucesso!');
    });
  });

  it('trata erro retornado pela API', async () => {
    mockLogin.mockRejectedValueOnce(
      new ApiError(401, 'Credenciais incorretas.'),
    );

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText(/e-mail/i), {
      target: { value: 'errado@defesa.rj.gov.br' },
    });
    fireEvent.change(screen.getByLabelText(/^senha$/i), {
      target: { value: 'errada' },
    });

    fireEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Credenciais incorretas.');
    });
  });
});
