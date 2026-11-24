import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Filter,
  MapPin,
  Radio,
  Trash2,
  ShieldAlert,
  User,
} from 'lucide-react';
import { Panel } from '@/components/common';
import { useOcorrencias } from '@/hooks/useOcorrencias';
import {
  atualizarStatusOcorrencia,
  excluirOcorrencia,
  type OcorrenciaItem,
} from '@/services/api';

interface ListaOcorrenciasProps {
  estacaoId?: string;
  modoOperador?: boolean;
}

export const ListaOcorrencias: React.FC<ListaOcorrenciasProps> = ({
  estacaoId,
  modoOperador = false,
}) => {
  const { data: ocorrencias = [], isLoading, error } = useOcorrencias(estacaoId);
  const [filtroStatus, setFiltroStatus] = useState<string>('TODAS');
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: ({
      id,
      status,
    }: {
      id: string;
      status: 'ABERTA' | 'EM_ANDAMENTO' | 'ENCERRADA';
    }) => atualizarStatusOcorrencia(id, status),
    onSuccess: (_, variables) => {
      const labels: Record<string, string> = {
        ABERTA: 'Aberta',
        EM_ANDAMENTO: 'Em Andamento',
        ENCERRADA: 'Encerrada',
      };
      toast.success(
        `Status da ocorrência atualizado para: ${labels[variables.status] ?? variables.status}`,
      );
      void queryClient.invalidateQueries({ queryKey: ['ocorrencias'] });
    },
    onError: () => {
      toast.error('Erro ao atualizar status da ocorrência.');
    },
  });

  const exclusao = useMutation({
    mutationFn: (id: string) => excluirOcorrencia(id),
    onSuccess: () => {
      toast.success('Ocorrência excluída. A exclusão ficou registrada na auditoria.');
      void queryClient.invalidateQueries({ queryKey: ['ocorrencias'] });
    },
    onError: () => {
      toast.error('Erro ao excluir a ocorrência.');
    },
  });

  const confirmarExclusao = (oco: OcorrenciaItem) => {
    if (
      window.confirm(
        `Excluir a ocorrência em "${oco.localizacao}"? Esta ação não pode ser desfeita.`,
      )
    ) {
      exclusao.mutate(oco.id);
    }
  };

  const ocorrenciasFiltradas = ocorrencias.filter((item) => {
    if (filtroStatus === 'TODAS') return true;
    return item.status === filtroStatus;
  });

  const abertasCount = ocorrencias.filter((o) => o.status === 'ABERTA').length;
  const emAndamentoCount = ocorrencias.filter(
    (o) => o.status === 'EM_ANDAMENTO',
  ).length;

  const formatarData = (iso: string) => {
    try {
      const d = new Date(iso);
      return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }).format(d);
    } catch {
      return iso;
    }
  };

  const getStatusBadge = (status: OcorrenciaItem['status']) => {
    switch (status) {
      case 'ABERTA':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
            <span className="size-1.5 animate-pulse rounded-full bg-amber-500" />
            Aberta
          </span>
        );
      case 'EM_ANDAMENTO':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-semibold text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
            <Clock className="size-3" />
            Em Atendimento
          </span>
        );
      case 'ENCERRADA':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
            <CheckCircle2 className="size-3" />
            Encerrada
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700 dark:bg-slate-700 dark:text-slate-300">
            {status}
          </span>
        );
    }
  };

  return (
    <Panel>
      <div className="space-y-4">
        {/* Header do Painel */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex size-9 items-center justify-center rounded-lg bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400">
              <ShieldAlert className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">
                  {modoOperador
                    ? 'Ocorrências Registradas em Campo'
                    : 'Informes de Campo da Defesa Civil'}
                </h2>
                {ocorrencias.length > 0 && (
                  <span className="rounded-full bg-brand/10 px-2 py-0.5 text-xs font-semibold text-brand dark:bg-brand/20 dark:text-brand-light">
                    {ocorrencias.length} {ocorrencias.length === 1 ? 'registro' : 'registros'}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {modoOperador
                  ? 'Histórico operacional de intervenções, alagamentos e vistorias em Resende.'
                  : 'Relatos oficiais de vistoria e acompanhamento das margens do Rio Sesmaria.'}
              </p>
            </div>
          </div>

          {/* Filtros rápidos */}
          {ocorrencias.length > 0 && (
            <div className="flex items-center gap-1.5 self-start sm:self-auto">
              <Filter className="size-3.5 text-slate-400" />
              {(
                [
                  { id: 'TODAS', label: 'Todas' },
                  { id: 'ABERTA', label: `Abertas (${abertasCount})` },
                  { id: 'EM_ANDAMENTO', label: `Em Andamento (${emAndamentoCount})` },
                  { id: 'ENCERRADA', label: 'Encerradas' },
                ] as const
              ).map((f) => (
                <button
                  key={f.id}
                  onClick={() => setFiltroStatus(f.id)}
                  className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-colors ${
                    filtroStatus === f.id
                      ? 'bg-slate-800 text-white dark:bg-slate-100 dark:text-slate-900'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="space-y-3 py-4">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="animate-pulse rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/50"
              >
                <div className="mb-2 h-4 w-1/3 rounded bg-slate-200 dark:bg-slate-700" />
                <div className="h-3 w-3/4 rounded bg-slate-200 dark:bg-slate-700" />
              </div>
            ))}
          </div>
        )}

        {/* Erro */}
        {error && (
          <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-600 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-400">
            <AlertCircle className="size-4 shrink-0" />
            <span>Não foi possível carregar as ocorrências no momento.</span>
          </div>
        )}

        {/* Estado Vazio */}
        {!isLoading && !error && ocorrenciasFiltradas.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-200 p-8 text-center dark:border-slate-700">
            <Radio className="mx-auto mb-2 size-8 text-slate-300 dark:text-slate-600" />
            <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
              {filtroStatus === 'TODAS'
                ? 'Nenhuma ocorrência registrada até o momento.'
                : 'Nenhuma ocorrência encontrada com o filtro selecionado.'}
            </p>
            <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
              {modoOperador
                ? 'Utilize o botão "+ Registrar Ocorrência" acima para cadastrar intervenções em campo.'
                : 'A Defesa Civil mantém o monitoramento contínuo da bacia.'}
            </p>
          </div>
        )}

        {/* Lista de Cards */}
        {!isLoading && !error && ocorrenciasFiltradas.length > 0 && (
          <div className="space-y-3">
            {ocorrenciasFiltradas.map((oco, idx) => (
              <div
                key={oco.id || `oco-${idx}`}
                className="relative flex flex-col justify-between gap-3 rounded-xl border border-slate-200/80 bg-white p-4 shadow-sm transition-all hover:border-slate-300 dark:border-slate-700/80 dark:bg-slate-800/90 dark:hover:border-slate-600 sm:flex-row sm:items-start"
              >

                <div className="space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    {getStatusBadge(oco.status)}
                    <span className="flex items-center gap-1 text-xs font-semibold text-slate-800 dark:text-slate-200">
                      <MapPin className="size-3.5 text-brand" />
                      {oco.localizacao}
                    </span>
                    <span className="text-xs text-slate-400 dark:text-slate-500">
                      • {formatarData(oco.criado_em)}
                    </span>
                  </div>

                  <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
                    {oco.descricao}
                  </p>

                  <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] text-slate-500 dark:text-slate-400">
                    {oco.estacao_nome && (
                      <span className="rounded bg-slate-100 px-1.5 py-0.5 dark:bg-slate-700">
                        Estação: {oco.estacao_nome}
                      </span>
                    )}
                    {oco.usuario_nome && (
                      <span className="flex items-center gap-1">
                        <User className="size-3" />
                        Agente: {oco.usuario_nome}
                      </span>
                    )}
                  </div>
                </div>

                {/* Ações de status para Operadores */}
                {modoOperador && (
                  <div className="flex shrink-0 items-center gap-1.5 pt-2 sm:pt-0">
                    {oco.status === 'ABERTA' && (
                      <button
                        onClick={() =>
                          mutation.mutate({
                            id: oco.id,
                            status: 'EM_ANDAMENTO',
                          })
                        }
                        disabled={mutation.isPending}
                        className="rounded-lg border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 transition-colors hover:bg-blue-100 dark:border-blue-900/60 dark:bg-blue-900/30 dark:text-blue-300 dark:hover:bg-blue-900/50"
                        title="Marcar como Em Atendimento"
                      >
                        Iniciar Atendimento
                      </button>
                    )}
                    {oco.status !== 'ENCERRADA' && (
                      <button
                        onClick={() =>
                          mutation.mutate({
                            id: oco.id,
                            status: 'ENCERRADA',
                          })
                        }
                        disabled={mutation.isPending}
                        className="rounded-lg border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 transition-colors hover:bg-emerald-100 dark:border-emerald-900/60 dark:bg-emerald-900/30 dark:text-emerald-300 dark:hover:bg-emerald-900/50"
                        title="Encerrar Ocorrência"
                      >
                        Encerrar
                      </button>
                    )}
                    {oco.status === 'ENCERRADA' && (
                      <button
                        onClick={() =>
                          mutation.mutate({
                            id: oco.id,
                            status: 'ABERTA',
                          })
                        }
                        disabled={mutation.isPending}
                        className="rounded-lg border border-slate-200 px-2 py-1 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-700"
                        title="Reabrir Ocorrência"
                      >
                        Reabrir
                      </button>
                    )}
                    <button
                      onClick={() => confirmarExclusao(oco)}
                      disabled={exclusao.isPending}
                      className="rounded-lg border border-red-200 p-1.5 text-red-600 transition-colors hover:bg-red-50 dark:border-red-900/60 dark:text-red-400 dark:hover:bg-red-900/30"
                      title="Excluir ocorrência"
                      aria-label={`Excluir ocorrência em ${oco.localizacao}`}
                    >
                      <Trash2 className="size-3.5" />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Panel>
  );
};
