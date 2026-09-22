import React from 'react';
import { AlertTriangle, Clock, Droplets } from 'lucide-react';
import { RiskBadge } from '@/components/common';
import type { EstacoesStatusResponse } from '@/services/api';

interface CardNivelAtualProps {
  estacao: EstacoesStatusResponse;
  selecionada?: boolean;
  onSelecionar?: () => void;
}

export const CardNivelAtual: React.FC<CardNivelAtualProps> = ({
  estacao,
  selecionada = false,
  onSelecionar,
}) => {
  const nivel = Number(estacao.nivel_atual_metros);
  const risco = estacao.classificacao_risco;

  return (
    <div
      className={`flex cursor-pointer flex-col justify-between rounded-xl border p-6 shadow-card transition-all duration-200 bg-white dark:bg-slate-800 ${
        selecionada
          ? 'border-brand ring-2 ring-brand/20 shadow-card-hover'
          : 'border-slate-200 hover:border-brand/30 hover:shadow-card-hover dark:border-slate-700'
      }`}
      onClick={onSelecionar}
      aria-label={`Estação ${estacao.nome} — nível ${nivel.toFixed(2)} metros — ${risco}`}
      aria-pressed={selecionada}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelecionar?.();
        }
      }}
    >
      <div>
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-base font-bold leading-snug text-slate-800 dark:text-slate-100">
              {estacao.nome}
            </h2>
            <p className="mt-0.5 text-xs font-medium text-slate-500 dark:text-slate-400">
              {estacao.rio}
            </p>
          </div>
          <RiskBadge nivel={risco} size="md" />
        </div>

        <div className="mt-5 flex items-baseline gap-2">
          <Droplets
            className="size-6 self-center text-brand"
            aria-hidden="true"
          />
          <span className="text-4xl font-extrabold tabular-nums text-slate-900 dark:text-white">
            {nivel.toFixed(2)}
          </span>
          <span className="text-base font-semibold text-slate-500 dark:text-slate-400">
            m
          </span>
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
        <span className="flex items-center gap-1">
          <Clock className="size-3.5" aria-hidden="true" />
          <time dateTime={estacao.data_hora_leitura}>
            {new Date(estacao.data_hora_leitura).toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </time>
        </span>
        {estacao.dados_desatualizados && (
          <span
            className="flex items-center gap-1 rounded bg-amber-50 px-2 py-0.5 font-semibold text-amber-600 dark:bg-amber-900/20 dark:text-amber-400"
            role="alert"
          >
            <AlertTriangle className="size-3.5" aria-hidden="true" />
            Defasado
          </span>
        )}
      </div>
    </div>

  );
};
