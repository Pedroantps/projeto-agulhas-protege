import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { useAuthStore } from '@/stores/authStore';
import { ProtectedRoute } from '../ProtectedRoute';

function renderWithRouter(initialEntry: string, allowedRoles: ('ADMINISTRADOR' | 'OPERADOR_DEFESA_CIVIL')[]) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<div>Página de Login</div>} />
        <Route path="/" element={<div>Página Pública</div>} />
        <Route element={<ProtectedRoute allowedRoles={allowedRoles} />}>
          <Route path="/admin" element={<div>Painel Administrativo</div>} />
          <Route path="/operador" element={<div>Painel Operador</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, isAuthenticated: false });
  });

  it('redireciona para /login quando o usuário não está autenticado', () => {
    renderWithRouter('/admin', ['ADMINISTRADOR']);

    expect(screen.getByText('Página de Login')).toBeInTheDocument();
    expect(screen.queryByText('Painel Administrativo')).not.toBeInTheDocument();
  });

  it('redireciona para / quando o usuário não possui o perfil exigido', () => {
    useAuthStore.setState({
      user: { nome: 'Operador Teste', perfil: 'OPERADOR_DEFESA_CIVIL' },
      isAuthenticated: true,
    });

    renderWithRouter('/admin', ['ADMINISTRADOR']);

    expect(screen.getByText('Página Pública')).toBeInTheDocument();
    expect(screen.queryByText('Painel Administrativo')).not.toBeInTheDocument();
  });

  it('renderiza a rota protegida quando o usuário tem o perfil autorizado', () => {
    useAuthStore.setState({
      user: { nome: 'Admin Teste', perfil: 'ADMINISTRADOR' },
      isAuthenticated: true,
    });

    renderWithRouter('/admin', ['ADMINISTRADOR']);

    expect(screen.getByText('Painel Administrativo')).toBeInTheDocument();
    expect(screen.queryByText('Página Pública')).not.toBeInTheDocument();
    expect(screen.queryByText('Página de Login')).not.toBeInTheDocument();
  });

  it('permite acesso a rotas permitidas para múltiplos perfis', () => {
    useAuthStore.setState({
      user: { nome: 'Operador Silva', perfil: 'OPERADOR_DEFESA_CIVIL' },
      isAuthenticated: true,
    });

    renderWithRouter('/operador', ['ADMINISTRADOR', 'OPERADOR_DEFESA_CIVIL']);

    expect(screen.getByText('Painel Operador')).toBeInTheDocument();
  });
});
