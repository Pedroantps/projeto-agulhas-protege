import { CloudRain, Database, Layers, Sparkles } from 'lucide-react';

import { Panel } from '@/components/common';
import type { CorrelacaoVariavel, TelemetriaBacia } from '@/services/api';

interface PainelCorrelacaoProps {
  telemetria: TelemetriaBacia;
  correlacoes: CorrelacaoVariavel[];
  eventosCriticos: number;
}

export const PainelCorrelacao: React.FC<PainelCorrelacaoProps> = ({
  telemetria,
  correlacoes,
  eventosCriticos,
}) => {
  return (
    <Panel
      id="painel-correlacao"
      title="Análise de Correlação Hidrológica — Bacia do Rio Sesmaria"
      className="space-y-6"
    >
      <div className="flex flex-col gap-2 border-b border-slate-100 pb-4 dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Correlação linear (equivalente ao <code>CORREL</code>) entre as variáveis da bacia e o nível do Rio Sesmaria em Resende.
          </p>
          <span className="inline-flex items-center gap-1.5 mt-1 text-xs font-medium text-brand">
            <Sparkles className="size-3.5" aria-hidden="true" />
            Calibrado com foco em eventos de cheia ({eventosCriticos} medições com rio &gt; 2,50m)
          </span>
        </div>
      </div>

      {/* 3 Eixos Físicos da Bacia */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {/* Eixo 1: Montante / Cabeceira */}
        <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 transition-all hover:border-brand/30 dark:border-slate-700 dark:bg-slate-800/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Montante (Serra da Bocaina)
            </span>
            <CloudRain className="size-4 text-blue-500" aria-hidden="true" />
          </div>
          <h3 className="mt-1 text-sm font-semibold text-slate-800 dark:text-slate-100">
            São José do Barreiro (SP)
          </h3>
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
            Tempo de trânsito fluvial: 4 a 6 horas
          </p>

          <div className="mt-4 space-y-2 text-xs">
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 dark:border-slate-700/60">
              <span className="text-slate-600 dark:text-slate-300">Chuva há 4h (-4h):</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.chuva_sjb_1h_lag4_mm} mm/h</span>
            </div>
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 font-semibold text-brand dark:border-slate-700/60">
              <span className="flex items-center gap-1">
                <span>Chuva há 5h (-5h):</span>
                <span className="rounded bg-brand/10 px-1 py-0.2 text-[10px] text-brand">Pico r=0.88</span>
              </span>
              <span>{telemetria.chuva_sjb_1h_lag5_mm} mm/h</span>
            </div>
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 dark:border-slate-700/60">
              <span className="text-slate-600 dark:text-slate-300">Chuva há 6h (-6h):</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.chuva_sjb_1h_lag6_mm} mm/h</span>
            </div>
          </div>
        </div>

        {/* Eixo 2: Saturação do Solo */}
        <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 transition-all hover:border-brand/30 dark:border-slate-700 dark:bg-slate-800/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Capacidade de Infiltração
            </span>
            <Layers className="size-4 text-emerald-500" aria-hidden="true" />
          </div>
          <h3 className="mt-1 text-sm font-semibold text-slate-800 dark:text-slate-100">
            Saturação do Solo (Acumulado)
          </h3>
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
            SJB e Resende (12h a 7 dias)
          </p>

          <div className="mt-4 space-y-2 text-xs">
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 dark:border-slate-700/60">
              <span className="text-slate-600 dark:text-slate-300">Acumulado 24h (SJB):</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.chuva_sjb_acumulada_24h_mm} mm</span>
            </div>
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 dark:border-slate-700/60">
              <span className="text-slate-600 dark:text-slate-300">Acumulado 48h (SJB):</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.chuva_sjb_acumulada_48h_mm} mm</span>
            </div>
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 dark:border-slate-700/60">
              <span className="text-slate-600 dark:text-slate-300">Acumulado 7 Dias:</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.chuva_sjb_acumulada_168h_mm} mm</span>
            </div>
            <div className="flex items-center justify-between pt-0.5">
              <span className="text-slate-600 dark:text-slate-300">Índice Saturação:</span>
              <span className="font-bold text-amber-600 dark:text-amber-400">{telemetria.saturacao_solo_sjb_percent}% (Alto)</span>
            </div>
          </div>
        </div>

        {/* Eixo 3: Jusante / Efeito Remanso Funil */}
        <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 transition-all hover:border-brand/30 dark:border-slate-700 dark:bg-slate-800/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Jusante / Remanso
            </span>
            <Database className="size-4 text-purple-500" aria-hidden="true" />
          </div>
          <h3 className="mt-1 text-sm font-semibold text-slate-800 dark:text-slate-100">
            Represa do Funil (Paraíba do Sul)
          </h3>
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
            Tempo trânsito: 1h20 a 1h30
          </p>

          <div className="mt-4 space-y-2 text-xs">
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 dark:border-slate-700/60">
              <span className="text-slate-600 dark:text-slate-300">Vazão Atual Defluente:</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.vazao_funil_atual_m3s} m³/s</span>
            </div>
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 dark:border-slate-700/60">
              <span className="text-slate-600 dark:text-slate-300">Vazão há 1h (-1h):</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.vazao_funil_lag1_m3s} m³/s</span>
            </div>
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 dark:border-slate-700/60">
              <span className="text-slate-600 dark:text-slate-300">Vazão há 2h (-2h):</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.vazao_funil_lag2_m3s} m³/s</span>
            </div>
            <div className="flex items-center justify-between pt-0.5">
              <span className="text-slate-600 dark:text-slate-300">Média Trânsito (1h30):</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">{telemetria.vazao_funil_media_transito_m3s} m³/s</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabela de Fatores de Correlação */}
      <div>
        <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
          Matriz de Fatores de Correlação com a Altura do Rio Sesmaria
        </h4>
        <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-200 bg-slate-100 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
              <tr>
                <th className="px-4 py-3 font-semibold">Variável Preditiva</th>
                <th className="px-3 py-3 font-semibold">Origem do Dado</th>
                <th className="px-3 py-3 font-semibold">Defasagem (Lag)</th>
                <th className="px-3 py-3 font-semibold">Coeficiente (r)</th>
                <th className="px-3 py-3 font-semibold">Relevância</th>
                <th className="hidden px-4 py-3 font-semibold md:table-cell">Interpretação Física</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white dark:divide-slate-800 dark:bg-slate-900">
              {correlacoes.map((item) => (
                <tr key={item.id} className="transition-colors hover:bg-slate-50/80 dark:hover:bg-slate-800/40">
                  <td className="px-4 py-3 font-medium text-slate-800 dark:text-slate-100">
                    {item.nome}
                  </td>
                  <td className="px-3 py-3 text-slate-500 dark:text-slate-400">{item.origem}</td>
                  <td className="px-3 py-3 font-mono text-slate-600 dark:text-slate-300">{item.lag_horas}</td>
                  <td className="px-3 py-3 font-mono font-bold text-brand">
                    +{item.coeficiente_r.toFixed(2)}
                  </td>
                  <td className="px-3 py-3">
                    <span
                      className={`inline-block rounded px-2 py-0.5 text-[11px] font-semibold ${
                        item.relevancia === 'ALTA'
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                          : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
                      }`}
                    >
                      {item.relevancia}
                    </span>
                  </td>
                  <td className="hidden px-4 py-3 text-slate-500 dark:text-slate-400 md:table-cell">
                    {item.descricao_fisica}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Panel>
  );
};
