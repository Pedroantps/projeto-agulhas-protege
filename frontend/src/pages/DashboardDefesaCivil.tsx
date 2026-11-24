import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { LogOut, Settings, Shield } from 'lucide-react';


import { CardNivelAtual, FormOcorrencia, ListaOcorrencias } from '@/components';

import { CardSkeleton, ThemeToggle } from '@/components/common';
import {
  CardRecomendacaoFunil,
  PainelCorrelacao,
  PainelPrevisaoIA,
} from '@/components/sesmaria';
import { useAuth } from '@/hooks/useAuth';
import { useEstacoes } from '@/hooks/useEstacoes';
import { useSesmariaDashboard } from '@/hooks/useSesmaria';

export const DashboardDefesaCivil: React.FC = () => {
  const { user, logout } = useAuth();
  const { data: estacoes, isLoading, error } = useEstacoes();
  const { data: sesmariaData } = useSesmariaDashboard();

  const [estacaoParaOcorrencia, setEstacaoParaOcorrencia] = useState<
    string | null
  >(null);

  const rawList = Array.isArray(estacoes) ? estacoes : [];
  // Foco exclusivo no Rio Sesmaria
  const sesmariaOnly = rawList.filter(
    (e) =>
      e.rio?.toLowerCase().includes('sesmaria') ||
      e.codigo_externo?.includes('SESMARIA'),
  );
  const estacoesList = sesmariaOnly.length > 0 ? sesmariaOnly : rawList;

  const estacaoAlvo = estacaoParaOcorrencia
    ? estacoesList.find((e) => e.estacao_id === estacaoParaOcorrencia)
    : undefined;

  return (
    <div className="min-h-screen bg-slate-50 transition-colors dark:bg-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex size-9 items-center justify-center rounded-lg bg-brand/10 text-brand dark:bg-brand/20">
              <Shield className="size-5" aria-hidden="true" />
            </div>
            <div>
              <span className="font-bold text-slate-800 dark:text-slate-100">
                Defesa Civil
              </span>
              <span className="ml-2 hidden rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-600 sm:inline-block dark:bg-slate-700 dark:text-slate-300">
                {user?.perfil === 'ADMINISTRADOR'
                  ? 'ADMINISTRADOR'
                  : 'OPERADOR'}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {user?.perfil === 'ADMINISTRADOR' && (
              <Link
                to="/admin"
                className="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-brand dark:text-slate-300 dark:hover:bg-slate-700"
                title="Configurações Administrativas"
              >
                <Settings className="size-4" />
                <span className="hidden sm:inline">Admin</span>
              </Link>
            )}
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

      <main className="mx-auto max-w-7xl space-y-8 px-4 py-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">
              Monitoramento em Tempo Real
            </h1>
            <span className="rounded-full bg-brand/10 px-2.5 py-0.5 text-xs font-semibold text-brand">
              Rio Sesmaria • Plantão 24h
            </span>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Acompanhamento operacional, registro de ocorrências, correlação hidrológica e previsão com dados reais.
          </p>

        </div>

        {error && (
          <div
            role="alert"
            className="rounded-xl border border-red-200 bg-red-50 p-6 text-center text-sm text-red-600 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-400"
          >
            Erro ao sincronizar dados das estações.
          </div>
        )}

        {/* Modal/Formulário de ocorrência */}
        {estacaoParaOcorrencia && (
          <div className="rounded-2xl border border-brand/30 bg-brand/5 p-4 dark:border-brand/40 dark:bg-brand/10">
            <div className="mb-2 text-xs font-semibold text-brand">
              Registrando ocorrência para: {estacaoAlvo?.nome}
            </div>
            <FormOcorrencia
              estacaoId={estacaoParaOcorrencia}
              onConcluir={() => setEstacaoParaOcorrencia(null)}
            />
          </div>
        )}

        {/* Seção 1: Grid de estações e acionamento operacional */}
        <section aria-labelledby="estacoes-operacionais">
          <h2
            id="estacoes-operacionais"
            className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
          >
            Estação de Monitoramento
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {isLoading
              ? Array.from({ length: 1 }).map((_, i) => <CardSkeleton key={i} />)
              : estacoesList.map((estacao) => (
                  <div
                    key={estacao.estacao_id}
                    className="space-y-2 rounded-xl bg-white p-2 shadow-card dark:bg-slate-800/80"
                  >
                    <CardNivelAtual estacao={estacao} />
                    <button
                      onClick={() => setEstacaoParaOcorrencia(estacao.estacao_id)}
                      className="w-full rounded-lg border border-brand/30 py-2 text-xs font-semibold text-brand transition-colors hover:bg-brand hover:text-white"
                    >
                      + Registrar Ocorrência
                    </button>
                  </div>
                ))}
          </div>
        </section>

        {/* Seção 2: Ocorrências de Campo da Defesa Civil */}
        <section aria-label="Ocorrências Registradas em Campo">
          <ListaOcorrencias modoOperador={true} />
        </section>

        {/* Módulos de Operação e Inteligência da Defesa Civil */}

        {sesmariaData && (
          <>
            {/* Seção 2: Modelo Preditivo (+24h, +48h, +72h) */}
            <section aria-label="Previsão do nível">
              <PainelPrevisaoIA previsoes={sesmariaData.previsoes} />
            </section>

            {/* Seção 3: Análise de Correlação da Bacia (SJB, Saturação, Funil) */}
            <section aria-label="Correlação Hidrológica">
              <PainelCorrelacao
                telemetria={sesmariaData.telemetria}
                correlacoes={sesmariaData.correlacoes}
                eventosCriticos={sesmariaData.eventos_criticos_base}
              />
            </section>

            {/* Seção 4: Prescrição Operacional da Represa do Funil e WhatsApp */}
            <section aria-label="Recomendação de Vazão Funil">
              <CardRecomendacaoFunil
                recomendacao={sesmariaData.recomendacao_funil}
                mensagemWhatsapp={sesmariaData.mensagem_alerta_whatsapp}
              />
            </section>
          </>
        )}
      </main>
    </div>
  );
};

export default DashboardDefesaCivil;
