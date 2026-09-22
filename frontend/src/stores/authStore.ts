import { create } from 'zustand';

export type AuthProfile = 'ADMINISTRADOR' | 'OPERADOR_DEFESA_CIVIL';

export interface AuthUser {
  nome: string;
  perfil: AuthProfile;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  setUser: (user: AuthUser | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: user !== null }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));
