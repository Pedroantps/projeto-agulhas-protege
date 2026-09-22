import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, ExternalLink, MessageSquare, Send } from 'lucide-react';


import { Panel } from '@/components/common';
import type { RecomendacaoFunil } from '@/services/api';

interface CardRecomendacaoFunilProps {
  recomendacao: RecomendacaoFunil;
  mensagemWhatsapp: string;
}

export const CardRecomendacaoFunil: React.FC<CardRecomendacaoFunilProps> = ({
  recomendacao,
  mensagemWhatsapp,
}) => {
  const [copiado, setCopiado] = useState(false);

  const handleCopiarMensagem = async () => {
    try {
      await navigator.clipboard.writeText(mensagemWhatsapp);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 3000);
    } catch {
      // Fallback
    }
  };

  const handleAbrirWhatsApp = () => {
    const encoded = encodeURIComponent(mensagemWhatsapp);
    window.open(`https://wa.me/?text=${encoded}`, '_blank', 'noopener,noreferrer');
  };

  return (
    <Panel
      id="card-recomendacao-funil"
      title="Prescrição Operacional — Controle de Vazão na Represa do Funil"
      className="space-y-4"
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-1">
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Ação preventiva recomendada pelo modelo para mitigar o <strong>efeito remanso</strong> na foz do Rio Sesmaria durante o trânsito da onda de cheia.
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Tempo de resposta da manobra: <strong>{recomendacao.tempo_transito_medio}</strong> até refletir no leito urbano de Resende.
          </p>
        </div>

        {/* Indicadores de Vazão Atual vs. Sugerida */}
        <div className="flex items-center gap-4 rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-800/80">
          <div>
            <span className="block text-[11px] font-medium text-slate-500 dark:text-slate-400">Vazão Atual Funil</span>
            <span className="text-lg font-extrabold text-slate-800 dark:text-slate-100">
              {recomendacao.vazao_atual_m3s} <span className="text-xs font-normal">m³/s</span>
            </span>
          </div>

          <div className="h-8 w-px bg-slate-200 dark:bg-slate-700" />

          <div>
            <span className="block text-[11px] font-medium text-amber-600 dark:text-amber-400">Teto Seguro Recomendado</span>
            <span className="text-lg font-extrabold text-brand">
              {recomendacao.vazao_maxima_sugerida_m3s} <span className="text-xs font-normal">m³/s</span>
            </span>
          </div>
        </div>
      </div>

      {/* Caixa de Ação Preventiva */}
      <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-4 dark:border-amber-900/40 dark:bg-amber-950/20">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 size-5 shrink-0 text-amber-600 dark:text-amber-400" aria-hidden="true" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300">
              Recomendação para a Defesa Civil & Furnas
            </h4>
            <p className="text-xs leading-relaxed text-amber-900 dark:text-amber-200">
              {recomendacao.acao_preventiva}
            </p>
          </div>
        </div>
      </div>

      {/* Botões de Ação para Defesa Civil */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <span className="text-xs text-slate-500 dark:text-slate-400">
          Redução de nível esperada no Sesmaria: <strong>~{recomendacao.impacto_estimado_leito_cm} cm</strong> no pico.
        </span>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopiarMensagem}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            {copiado ? (
              <>
                <CheckCircle className="size-3.5 text-emerald-600" aria-hidden="true" />
                <span>Copiado!</span>
              </>
            ) : (
              <>
                <MessageSquare className="size-3.5" aria-hidden="true" />
                <span>Copiar Boletim</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleAbrirWhatsApp}
            className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm transition-colors hover:bg-emerald-700 active:bg-emerald-800 dark:bg-emerald-700 dark:hover:bg-emerald-600"
            aria-label="Enviar Alerta Defesa Civil via WhatsApp"
          >
            <Send className="size-3.5" aria-hidden="true" />
            <span>Enviar Alerta Defesa Civil (WhatsApp)</span>
            <ExternalLink className="size-3 opacity-70" aria-hidden="true" />
          </button>
        </div>
      </div>
    </Panel>
  );
};
