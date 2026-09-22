import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Droplets, LogIn, RefreshCw } from 'lucide-react';
import { CardNivelAtual, GraficoHistorico } from '@/components';

import { CardSkeleton, Panel, ThemeToggle } from '@/components/common';
import { useEstacoes } from '@/hooks/useEstacoes';

export const HomePublica: React.FC = () => {
  const { data: estacoes, isLoading, error, refetch, isFetching } =
    useEstacoes();
  const [estacaoSelecionada, setEstacaoSelecionada] = useState<string | null>(
    null,
  );
  const [periodo, setPeriodo] = useState(24);

  const rawList = Array.isArray(estacoes) ? estacoes : [];
  // Foco exclusivo no Rio Sesmaria (remove qualquer outro rio mockado)
  const sesmariaOnly = rawList.filter(
    (e) =>
      e.rio?.toLowerCase().includes('sesmaria') ||
      e.codigo_externo?.includes('SESMARIA'),
  );
  const estacoesList = sesmariaOnly.length > 0 ? sesmariaOnly : rawList;

  // Seleciona por padrão a estação do Rio Sesmaria para exibir medição e gráfico abertos
  const estacaoAtivaId = estacaoSelecionada ?? estacoesList[0]?.estacao_id ?? null;
  const estacaoAtual = estacoesList.find((e) => e.estacao_id === estacaoAtivaId);

  return (
    <div className="min-h-screen bg-slate-50 transition-colors dark:bg-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-4 py-4 dark:border-slate-700 dark:bg-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-brand/10 dark:bg-brand/20">
              <Droplets className="size-6 text-brand" aria-hidden="true" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold leading-tight text-slate-800 dark:text-slate-100">
                  Agulhas Protege
                </span>
                <span className="hidden rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold text-blue-800 dark:bg-blue-900/50 dark:text-blue-200 sm:inline-block">
                  Rio Sesmaria
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Consulta Pública de Nível Fluviométrico — Resende-RJ
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <button
              onClick={() => {
                void refetch();
              }}
              className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200"
              aria-label="Atualizar dados"
              title="Atualizar dados"
            >
              <RefreshCw
                className={`size-4 ${isFetching ? 'animate-spin' : ''}`}
              />
            </button>
            <ThemeToggle />
            <Link
              to="/login"
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:border-brand/40 hover:bg-brand/5 hover:text-brand dark:border-slate-700 dark:text-slate-200 dark:hover:bg-brand/10 dark:hover:text-brand-light"
            >
              <LogIn className="size-3.5" aria-hidden="true" />
              <span className="hidden sm:inline">Defesa Civil</span>
              <span className="sm:hidden">Entrar</span>
            </Link>
          </div>
        </div>
      </header>

      <main
        id="main-content"
        className="mx-auto max-w-6xl space-y-8 px-4 py-6"
      >
        {/* Seção 1: Medição Atual (Acesso Aberto) */}
        <section aria-labelledby="estacoes-heading">
          <div className="mb-4">
            <h1
              id="estacoes-heading"
              className="text-2xl font-bold text-slate-800 dark:text-slate-100"
            >
              Nível Atual dos Rios
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Telemetria em tempo real do Rio Sesmaria no município de Resende.
            </p>
          </div>

          {error && (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 p-6 text-center text-sm text-red-600 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-400"
            >
              Não foi possível carregar os dados. Tente atualizar a página.
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3">
            {isLoading
              ? Array.from({ length: 1 }).map((_, i) => (
                <CardSkeleton key={i} />
              ))
              : estacoesList.length === 0
                ? (
                  <p className="col-span-full py-8 text-center text-slate-400">
                    Nenhuma estação de monitoramento operando no momento.
                  </p>
                )
                : estacoesList.map((estacao) => (
                  <CardNivelAtual
                    key={estacao.estacao_id}
                    estacao={estacao}
                    selecionada={estacaoAtivaId === estacao.estacao_id}
                    onSelecionar={() =>
                      setEstacaoSelecionada(
                        estacaoAtivaId === estacao.estacao_id
                          ? null
                          : estacao.estacao_id,
                      )
                    }
                  />
                ))}
          </div>
        </section>

        {/* Seção 2: Gráficos Históricos (Acesso Aberto) */}
        {estacaoAtivaId && (
          <section aria-labelledby="grafico-heading">
            <Panel>
              <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2
                    id="grafico-heading"
                    className="text-lg font-semibold text-slate-800 dark:text-slate-100"
                  >
                    Histórico — {estacaoAtual?.nome ?? 'Rio Sesmaria'}
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Evolução das cotas e do nível d'água ao longo do tempo.
                  </p>
                </div>

                {/* Seletor de período */}
                <div
                  className="flex gap-2"
                  role="group"
                  aria-label="Período do gráfico"
                >
                  {[
                    { label: '24h', value: 24 },
                    { label: '7d', value: 168 },
                    { label: '30d', value: 720 },
                  ].map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setPeriodo(opt.value)}
                      className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${periodo === opt.value
                          ? 'bg-brand text-white shadow-sm'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-400 dark:hover:bg-slate-600'
                        }`}
                      aria-pressed={periodo === opt.value}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
              <GraficoHistorico
                estacaoId={estacaoAtivaId}
                periodo={periodo}
                cotas={estacaoAtual?.cotas}
              />
            </Panel>
          </section>
        )}
      </main>

    </div>
  );
};

export default HomePublica;
