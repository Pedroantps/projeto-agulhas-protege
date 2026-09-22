import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient } from '@tanstack/react-query';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useAuthStore } from '@/stores/authStore';

import { App } from './App';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('App', () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    vi.stubGlobal('fetch', fetchMock);
    fetchMock.mockResolvedValue(
      jsonResponse([
        {
          estacao_id: 'est-1',
          codigo_externo: 'EST01',
          nome: 'Ponte Velha',
          rio: 'Rio Sesmaria',
          nivel_atual_metros: '2.10',
          classificacao_risco: 'NORMAL',
          data_hora_leitura: new Date().toISOString(),
          dados_desatualizados: false,
          cotas: { atencao: '2.50', alerta: '3.00', emergencia: '3.50' },
        },
      ]),
    );
  });

  afterEach(() => {
    fetchMock.mockReset();
    vi.unstubAllGlobals();
  });

  it('renderiza a página inicial pública na rota /', async () => {
    useAuthStore.setState({ user: null, isAuthenticated: false });
    const queryClient = createTestQueryClient();

    render(
      <MemoryRouter initialEntries={['/']}>
        <App queryClient={queryClient} />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('Agulhas Protege', {}, { timeout: 5000 }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole(
        'heading',
        { name: 'Nível Atual dos Rios' },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();
  });


  it('renderiza a tela de login na rota /login', async () => {
    useAuthStore.setState({ user: null, isAuthenticated: false });
    const queryClient = createTestQueryClient();

    render(
      <MemoryRouter initialEntries={['/login']}>
        <App queryClient={queryClient} />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole('button', { name: /entrar/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/e-mail/i)).toBeInTheDocument();
  });

  it('redireciona para /login ao tentar acessar rota protegida desautenticado', async () => {
    useAuthStore.setState({ user: null, isAuthenticated: false });
    const queryClient = createTestQueryClient();

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App queryClient={queryClient} />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole('button', { name: /entrar/i }),
    ).toBeInTheDocument();
  });

  it('permite acesso ao dashboard quando autenticado como operador', async () => {
    useAuthStore.setState({
      user: { nome: 'Carlos Operador', perfil: 'OPERADOR_DEFESA_CIVIL' },
      isAuthenticated: true,
    });
    const queryClient = createTestQueryClient();

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App queryClient={queryClient} />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole('heading', {
        name: 'Monitoramento em Tempo Real',
      }),
    ).toBeInTheDocument();
  });

  it('permite acesso ao admin quando autenticado como administrador', async () => {
    useAuthStore.setState({
      user: { nome: 'Ana Administradora', perfil: 'ADMINISTRADOR' },
      isAuthenticated: true,
    });
    const queryClient = createTestQueryClient();

    render(
      <MemoryRouter initialEntries={['/admin']}>
        <App queryClient={queryClient} />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole('heading', {
        name: 'Gerenciar Estações e Cotas de Risco',
      }),
    ).toBeInTheDocument();
  });
});
