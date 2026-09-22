import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Droplets, Eye, EyeOff, LogIn } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '@/hooks/useAuth';
import { ApiError } from '@/services/api';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [senhaVisivel, setSenhaVisivel] = useState(false);
  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCarregando(true);
    try {
      await login(email, senha);
      toast.success('Login realizado com sucesso!');
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error(error.detail);
      } else {
        toast.error('Erro de conexão. Tente novamente.');
      }
    } finally {
      setCarregando(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 p-4 dark:bg-slate-900">
      <div className="w-full max-w-sm">
        {/* Logo + título */}
        <div className="mb-8 text-center">
          <div className="mb-4 inline-flex size-16 items-center justify-center rounded-2xl bg-brand shadow-md">
            <Droplets className="size-9 text-white" aria-hidden="true" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">
            Agulhas Protege
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Defesa Civil — Resende-RJ
          </p>
        </div>

        {/* Formulário */}
        <form
          onSubmit={(e) => {
            void handleSubmit(e);
          }}
          className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800"
          aria-label="Formulário de login"
        >
          <div>
            <label
              htmlFor="email"
              className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              E-mail
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 transition-colors focus:outline-none focus:ring-2 focus:ring-brand dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
              placeholder="operador@defesacivil.rj.gov.br"
            />
          </div>

          <div>
            <label
              htmlFor="senha"
              className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Senha
            </label>
            <div className="relative">
              <input
                id="senha"
                type={senhaVisivel ? 'text' : 'password'}
                autoComplete="current-password"
                required
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 pr-10 text-sm text-slate-900 transition-colors focus:outline-none focus:ring-2 focus:ring-brand dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
              />
              <button
                type="button"
                onClick={() => setSenhaVisivel(!senhaVisivel)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                aria-label={senhaVisivel ? 'Ocultar senha' : 'Mostrar senha'}
              >
                {senhaVisivel ? (
                  <EyeOff className="size-4" />
                ) : (
                  <Eye className="size-4" />
                )}
              </button>
            </div>
          </div>

          <button
            id="btn-login"
            type="submit"
            disabled={carregando}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand py-2.5 font-semibold text-white transition-colors hover:bg-brand-dark focus:outline-none focus:ring-2 focus:ring-brand disabled:bg-brand/50"
          >
            <LogIn className="size-4" aria-hidden="true" />
            {carregando ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 transition-colors hover:text-brand dark:text-slate-400 dark:hover:text-brand-light"
          >
            <ArrowLeft className="size-3.5" />
            Voltar ao início público
          </Link>
        </div>
      </div>
    </main>
  );
};

export default Login;
