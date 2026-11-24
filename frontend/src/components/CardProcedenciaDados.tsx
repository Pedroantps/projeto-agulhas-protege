import React from 'react';
import { Camera, CloudRain, Database } from 'lucide-react';

import { Panel } from '@/components/common';
import { useSesmariaDashboard } from '@/hooks/useSesmaria';

const formatar = (iso: string | null) =>
  iso
    ? new Intl.DateTimeFormat('pt-BR', {
        dateStyle: 'short',
        timeStyle: 'short',
      }).format(new Date(iso))
    : '—';

export const CardProcedenciaDados: React.FC = () => {
  const { data } = useSesmariaDashboard();
  if (!data) return null;

  return (
    <Panel title="Dados da Estação em Tempo Real">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-[minmax(0,320px)_1fr]">
        {data.foto_estacao_url ? (
          <figure className="space-y-1">
            <img
              src={data.foto_estacao_url}
              alt="Foto mais recente do Rio Sesmaria, registrada pela câmera da estação"
              loading="lazy"
              className="w-full rounded-lg border border-slate-200 object-cover dark:border-slate-700"
            />
            <figcaption className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
              <Camera className="size-3.5" aria-hidden="true" />
              Câmera da estação — {formatar(data.foto_estacao_data_hora)}
            </figcaption>
          </figure>
        ) : null}

        <div className="space-y-3 text-sm">
          {data.chuva_estacao_24h_mm !== null && (
            <p className="flex items-center gap-2 text-slate-700 dark:text-slate-200">
              <CloudRain className="size-4 text-brand" aria-hidden="true" />
              Chuva na estação: <strong>{data.chuva_estacao_1h_mm} mm</strong>{' '}
              na última hora e <strong>{data.chuva_estacao_24h_mm} mm</strong>{' '}
              em 24h.
            </p>
          )}
          <p className="flex items-start gap-2 text-xs text-slate-500 dark:text-slate-400">
            <Database className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
            <span>
              Fontes: {data.fonte_dados}. Última coleta do servidor:{' '}
              {formatar(data.coletado_em)}.
            </span>
          </p>
        </div>
      </div>
    </Panel>
  );
};

export default CardProcedenciaDados;
