import React from 'react';
import { act, renderHook } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useAuth } from '../useAuth';
import * as api from '@/services/api';
import { useAuthStore } from '@/stores/authStore';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom',
  );
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('useAuth', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, isAuthenticated: false });
    mockNavigate.mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <MemoryRouter>{children}</MemoryRouter>
  );

  it('realiza login de operador e redireciona para /dashboard', async () => {
    vi.spyOn(api, 'loginApi').mockResolvedValue({
      nome: 'Operador Teste',
      perfil: 'OPERADOR_DEFESA_CIVIL',
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('op@defesa.rj.gov.br', 'senha123');
    });

    expect(useAuthStore.getState().user).toEqual({
      nome: 'Operador Teste',
      perfil: 'OPERADOR_DEFESA_CIVIL',
    });
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
  });

  it('realiza login de admin e redireciona para /admin', async () => {
    vi.spyOn(api, 'loginApi').mockResolvedValue({
      nome: 'Admin Teste',
      perfil: 'ADMINISTRADOR',
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('admin@defesa.rj.gov.br', 'senha123');
    });

    expect(mockNavigate).toHaveBeenCalledWith('/admin', { replace: true });
  });

  it('realiza logout, limpa a store e redireciona para /login', () => {
    useAuthStore.setState({
      user: { nome: 'Operador Teste', perfil: 'OPERADOR_DEFESA_CIVIL' },
      isAuthenticated: true,
    });
    vi.spyOn(api, 'logoutApi').mockResolvedValue();

    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.logout();
    });

    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true });
  });
});
