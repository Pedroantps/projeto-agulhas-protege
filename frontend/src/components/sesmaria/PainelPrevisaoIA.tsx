import { Calendar, CloudLightning } from 'lucide-react';

import { Panel, RiskBadge } from '@/components/common';
import type { PrevisaoNivelDia } from '@/services/api';

interface PainelPrevisaoIAProps {
  previsoes: PrevisaoNivelDia[];
}

export const PainelPrevisaoIA: React.FC<PainelPrevisaoIAProps> = ({ previsoes }) => {
  return (
    <Panel
      id="painel-previsao-ia"
      title="Modelo Preditivo — Projeção do Rio Sesmaria"
      className="space-y-6"
    >
      <div className="flex flex-col gap-1 border-b border-slate-100 pb-3 dark:border-slate-800">
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Projeção calculada a partir do nível real medido pelo CEMADEN, da chuva observada e prevista (Open-Meteo) na cabeceira e em Resende e da vazão do Funil (ONS). Modelo hidrológico simplificado com cenários de chuva; não substitui os comunicados oficiais da Defesa Civil.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {previsoes.map((prev) => {
          const isCritico = prev.classificacao_risco === 'ALERTA' || prev.classificacao_risco === 'EMERGENCIA';

          return (
            <div
              key={prev.dia_offset}
              className={`relative flex flex-col justify-between rounded-xl border p-5 transition-all ${
                isCritico
                  ? 'border-amber-300 bg-amber-50/40 shadow-sm dark:border-amber-900/50 dark:bg-amber-950/20'
                  : 'border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800'
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="size-4 text-slate-400" aria-hidden="true" />
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-200">
                      {prev.rotulo}
                    </span>
                  </div>
                  <RiskBadge nivel={prev.classificacao_risco} size="sm" />
                </div>

                {/* Nível Estimado */}
                <div className="mt-4">
                  <span className="text-xs text-slate-500 dark:text-slate-400">Nível Estimado do Rio</span>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl font-extrabold tabular-nums text-slate-900 dark:text-white">
                      {prev.nivel_estimado_metros}
                    </span>
                    <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">m</span>
                  </div>
                </div>

                {/* Métricas de Suporte */}
                <div className="mt-4 space-y-2 border-t border-slate-100 pt-3 text-xs dark:border-slate-700/60">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1 text-slate-500 dark:text-slate-400">
                      <CloudLightning className="size-3.5" aria-hidden="true" />
                      Chuva Prevista:
                    </span>
                    <span className="font-semibold text-slate-800 dark:text-slate-100">
                      {prev.chuva_prevista_mm} mm
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 dark:text-slate-400">Vazão Funil Estimada:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-100">
                      {prev.vazao_funil_esperada_m3s} m³/s
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 dark:text-slate-400">Probabilidade Alerta (&gt;2.5m):</span>
                    <span
                      className={`font-bold ${
                        prev.probabilidade_alerta > 50
                          ? 'text-amber-600 dark:text-amber-400'
                          : 'text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      {prev.probabilidade_alerta.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Confiabilidade */}
              <div className="mt-4 border-t border-slate-100 pt-3 dark:border-slate-700/60">
                <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                  <span>Confiabilidade da Previsão:</span>
                  <span className="font-bold">{prev.confiabilidade_percentual.toFixed(0)}%</span>
                </div>
                <div className="mt-1 h-1.5 w-full rounded-full bg-slate-100 dark:bg-slate-700">
                  <div
                    className="h-1.5 rounded-full bg-brand transition-all"
                    style={{ width: `${prev.confiabilidade_percentual}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
};
