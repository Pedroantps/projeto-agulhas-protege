import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, ArrowLeft, LogOut, Settings, Sliders } from 'lucide-react';
import { ModalGerenciarCotas, PainelColeta } from '@/components';
import {
  CardSkeleton,
  Panel,
  RiskBadge,
  ThemeToggle,
} from '@/components/common';
import { useAuth } from '@/hooks/useAuth';
import { useEstacoes } from '@/hooks/useEstacoes';
import type { EstacoesStatusResponse } from '@/services/api';

export const AdminConfiguracoes: React.FC = () => {
  const { user, logout } = useAuth();
  const { data: estacoes, isLoading, error } = useEstacoes();
  const [estacaoParaEditar, setEstacaoParaEditar] =
    useState<EstacoesStatusResponse | null>(null);

  const estacoesList = Array.isArray(estacoes) ? estacoes : [];

  return (
    <div className="min-h-screen bg-slate-50 transition-colors dark:bg-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-9 items-center justify-center rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400">
              <Settings className="size-5" aria-hidden="true" />
            </div>
            <div>
              <span className="font-bold text-slate-800 dark:text-slate-100">
                Painel Administrativo
              </span>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Agulhas Protege — Defesa Civil
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-700"
            >
              <Activity className="size-3.5 text-brand" />
              <span>Ver Monitoramento</span>
            </Link>
            <span className="hidden text-xs text-slate-500 sm:inline dark:text-slate-400">
              {user?.nome}
            </span>
            <ThemeToggle />
            <button
              onClick={logout}
              className="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-500 transition-colors hover:bg-red-50 hover:text-red-600 dark:text-slate-400 dark:hover:bg-red-900/20 dark:hover:text-red-400"
              aria-label="Sair do sistema"
            >
              <LogOut className="size-4" />
              <span>Sair</span>
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">
              Gerenciar Estações e Cotas de Risco
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Parametrize os limiares hidrológicos de alerta e emergência para
              cada estação.
            </p>
          </div>
          <Link
            to="/dashboard"
            className="hidden items-center gap-1 text-xs text-brand hover:underline sm:inline-flex"
          >
            <ArrowLeft className="size-3.5" />
            Voltar ao dashboard
          </Link>
        </div>

        {error && (
          <div
            role="alert"
            className="rounded-xl border border-red-200 bg-red-50 p-6 text-center text-sm text-red-600 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-400"
          >
            Não foi possível carregar a lista de estações.
          </div>
        )}

        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : (
          <Panel title="Estações Cadastradas">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-200 text-xs uppercase text-slate-500 dark:border-slate-700 dark:text-slate-400">
                  <tr>
                    <th scope="col" className="px-4 py-3">
                      Estação / Rio
                    </th>
                    <th scope="col" className="px-4 py-3">
                      Código
                    </th>
                    <th scope="col" className="px-4 py-3 text-center">
                      Nível Atual
                    </th>
                    <th scope="col" className="px-4 py-3 text-center">
                      Cotas Atuais (m)
                    </th>
                    <th scope="col" className="px-4 py-3 text-right">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-700/60">
                  {estacoesList.map((estacao) => (
                    <tr
                      key={estacao.estacao_id}
                      className="hover:bg-slate-50/50 dark:hover:bg-slate-750"
                    >
                      <td className="px-4 py-3">
                        <div className="font-semibold text-slate-800 dark:text-slate-100">
                          {estacao.nome}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">
                          {estacao.rio}
                        </div>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-600 dark:text-slate-400">
                        {estacao.codigo_externo}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="inline-flex flex-col items-center gap-1">
                          <span className="font-mono font-bold text-slate-900 dark:text-white">
                            {Number(estacao.nivel_atual_metros).toFixed(2)} m
                          </span>
                          <RiskBadge
                            nivel={estacao.classificacao_risco}
                            size="sm"
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="inline-flex items-center gap-2 font-mono text-xs">
                          <span
                            className="rounded bg-amber-50 px-1.5 py-0.5 font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                            title="Cota de Atenção"
                          >
                            At: {Number(estacao.cotas?.atencao ?? 0).toFixed(2)}
                          </span>
                          <span
                            className="rounded bg-orange-50 px-1.5 py-0.5 font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-400"
                            title="Cota de Alerta"
                          >
                            Al: {Number(estacao.cotas?.alerta ?? 0).toFixed(2)}
                          </span>
                          <span
                            className="rounded bg-red-50 px-1.5 py-0.5 font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400"
                            title="Cota de Emergência"
                          >
                            Em:{' '}
                            {Number(estacao.cotas?.emergencia ?? 0).toFixed(2)}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => setEstacaoParaEditar(estacao)}
                          className="inline-flex items-center gap-1.5 rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 transition-colors hover:bg-blue-100 dark:border-blue-900/50 dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/40"
                          aria-label={`Ajustar cotas da estação ${estacao.nome}`}
                        >
                          <Sliders className="size-3.5" />
                          <span>Ajustar Cotas</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        )}

        <PainelColeta />

        {/* Modal de gerenciamento de cotas */}
        {estacaoParaEditar && (
          <ModalGerenciarCotas
            estacaoId={estacaoParaEditar.estacao_id}
            estacaoNome={estacaoParaEditar.nome}
            cotasAtuais={{
              atencao: estacaoParaEditar.cotas?.atencao ?? '0',
              alerta: estacaoParaEditar.cotas?.alerta ?? '0',
              emergencia: estacaoParaEditar.cotas?.emergencia ?? '0',
            }}
            aberto={Boolean(estacaoParaEditar)}
            onFechar={() => setEstacaoParaEditar(null)}
          />
        )}
      </main>
    </div>
  );
};

export default AdminConfiguracoes;
