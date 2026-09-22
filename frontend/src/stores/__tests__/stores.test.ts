import { useAuthStore } from '../authStore';

describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, isAuthenticated: false });
  });

  it('autentica ao definir usuário e limpa a sessão no logout', () => {
    const user = {
      nome: 'Ana Souza',
      perfil: 'OPERADOR_DEFESA_CIVIL' as const,
    };

    useAuthStore.getState().setUser(user);
    expect(useAuthStore.getState()).toMatchObject({
      user,
      isAuthenticated: true,
    });

    useAuthStore.getState().logout();
    expect(useAuthStore.getState()).toMatchObject({
      user: null,
      isAuthenticated: false,
    });
  });

  it('considera null como sessão não autenticada', () => {
    useAuthStore.getState().setUser(null);
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});
