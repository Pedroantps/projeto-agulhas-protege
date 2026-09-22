import { useNavigate } from 'react-router-dom';
import { loginApi, logoutApi } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';

export const useAuth = () => {
  const { user, isAuthenticated, setUser, logout: storeLogout } =
    useAuthStore();
  const navigate = useNavigate();

  const login = async (email: string, senha: string): Promise<void> => {
    const data = await loginApi({ email, senha });
    setUser({ nome: data.nome, perfil: data.perfil });
    const destination =
      data.perfil === 'ADMINISTRADOR' ? '/admin' : '/dashboard';
    void navigate(destination, { replace: true });
  };

  const logout = (): void => {
    void logoutApi().catch(() => {});
    storeLogout();
    void navigate('/login', { replace: true });
  };

  return { user, isAuthenticated, login, logout };
};
