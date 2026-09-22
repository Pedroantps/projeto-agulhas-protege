import React from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Skeleton } from '@/components/common';
import { useLeituras } from '@/hooks/useLeituras';

interface GraficoHistoricoProps {
  estacaoId: string;
  periodo: number;
  cotas?: { atencao: string; alerta: string; emergencia: string };
}

export const GraficoHistorico: React.FC<GraficoHistoricoProps> = ({
  estacaoId,
  periodo,
  cotas,
}) => {
  const { data: leituras, isLoading, error } = useLeituras(estacaoId, periodo);

  if (isLoading) return <Skeleton height="h-64" />;

  if (error) {
    return (
      <div
        role="alert"
        className="flex h-64 items-center justify-center text-sm text-red-600 dark:text-red-400"
      >
        Não foi possível carregar o histórico de leituras.
      </div>
    );
  }

  const dados =
    leituras?.map((l) => ({
      hora: new Date(l.data_hora).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
      }),
      dataHoraCompleta: new Date(l.data_hora).toLocaleString('pt-BR'),
      nivel: Number(l.nivel_metros),
    })) ?? [];

  if (dados.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-slate-400">
        Nenhuma leitura registrada no período selecionado.
      </div>
    );
  }

  return (
    <div>
      {/* Gráfico SVG */}
      <div aria-hidden="true" className="w-full">
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart
            data={dados}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="nivelGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0284c7" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#0284c7" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              className="stroke-slate-200 dark:stroke-slate-700"
            />
            <XAxis dataKey="hora" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} unit="m" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderColor: '#334155',
                color: '#f8fafc',
                borderRadius: '0.5rem',
                fontSize: 12,
              }}
              formatter={(value) => [
                `${Number(value).toFixed(2)} m`,
                'Nível',
              ]}
            />
            <Area
              type="monotone"
              dataKey="nivel"
              stroke="#0284c7"
              fill="url(#nivelGradient)"
              strokeWidth={2}
            />
            {cotas && (
              <>
                <ReferenceLine
                  y={Number(cotas.atencao)}
                  stroke="#d97706"
                  strokeDasharray="4 2"
                  label={{
                    value: 'Atenção',
                    fill: '#d97706',
                    fontSize: 10,
                    position: 'insideTopRight',
                  }}
                />
                <ReferenceLine
                  y={Number(cotas.alerta)}
                  stroke="#ea580c"
                  strokeDasharray="4 2"
                  label={{
                    value: 'Alerta',
                    fill: '#ea580c',
                    fontSize: 10,
                    position: 'insideTopRight',
                  }}
                />
                <ReferenceLine
                  y={Number(cotas.emergencia)}
                  stroke="#dc2626"
                  strokeDasharray="4 2"
                  label={{
                    value: 'Emergência',
                    fill: '#dc2626',
                    fontSize: 10,
                    position: 'insideTopRight',
                  }}
                />
              </>
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Tabela fallback — acessibilidade WCAG 1.1.1 */}
      <details className="mt-4">
        <summary className="cursor-pointer text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300">
          Ver dados em tabela (acessibilidade)
        </summary>
        <div className="mt-2 max-h-48 overflow-y-auto">
          <table className="w-full border-collapse text-xs">
            <caption className="sr-only">
              Histórico de leituras de nível do rio
            </caption>
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th
                  scope="col"
                  className="px-2 py-1 text-left font-medium text-slate-600 dark:text-slate-400"
                >
                  Horário
                </th>
                <th
                  scope="col"
                  className="px-2 py-1 text-right font-medium text-slate-600 dark:text-slate-400"
                >
                  Nível (m)
                </th>
              </tr>
            </thead>
            <tbody>
              {dados.map((row, i) => (
                <tr
                  key={i}
                  className="border-b border-slate-100 dark:border-slate-700/50"
                >
                  <td className="px-2 py-1 text-slate-600 dark:text-slate-400">
                    {row.dataHoraCompleta}
                  </td>
                  <td className="px-2 py-1 text-right font-mono text-slate-800 dark:text-slate-200">
                    {row.nivel.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
};
