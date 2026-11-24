import React from 'react';
import toast from 'react-hot-toast';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { DownloadCloud, RefreshCw } from 'lucide-react';

import { Panel } from '@/components/common';
import { useStatusColeta } from '@/hooks/useSesmaria';
import { executarColeta } from '@/services/api';

const formatar = (iso: string | null) =>
  iso
    ? new Intl.DateTimeFormat('pt-BR', {
        dateStyle: 'short',
        timeStyle: 'medium',
      }).format(new Date(iso))
    : '—';

export const PainelColeta: React.FC = () => {
  const { data: status, isLoading } = useStatusColeta();
  const queryClient = useQueryClient();

  const coletar = useMutation({
    mutationFn: executarColeta,
    onSuccess: (resultado) => {
      const falhas = Object.keys(resultado.erros).length;
      toast.success(
        `Coleta concluída: ${resultado.leituras_novas} leitura(s) nova(s)` +
          (falhas > 0 ? `; ${falhas} fonte(s) indisponível(is).` : '.'),
      );
      void queryClient.invalidateQueries();
    },
    onError: () => toast.error('Não foi possível executar a coleta agora.'),
  });

  return (
    <Panel title="Coleta de Dados Reais">
      <div className="space-y-4 text-sm">
        <p className="text-slate-600 dark:text-slate-300">
          O próprio servidor busca nível, chuva e vazão em fontes públicas a
          cada {status?.intervalo_minutos ?? 10} minutos e grava no banco. Use o
          botão para forçar uma atualização imediata.
        </p>

        {isLoading ? (
          <p className="text-slate-400">Carregando status…</p>
        ) : (
          <dl className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">
                Última coleta
              </dt>
              <dd className="font-semibold text-slate-800 dark:text-slate-100">
                {formatar(status?.ultima_coleta ?? null)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">
                Última leitura do rio
              </dt>
              <dd className="font-semibold text-slate-800 dark:text-slate-100">
                {formatar(status?.ultima_leitura ?? null)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">
                Leituras armazenadas
              </dt>
              <dd className="font-semibold text-slate-800 dark:text-slate-100">
                {status?.total_leituras ?? 0}
              </dd>
            </div>
          </dl>
        )}

        {status && (
          <ul className="list-disc space-y-0.5 pl-5 text-xs text-slate-500 dark:text-slate-400">
            {status.fontes.map((fonte) => (
              <li key={fonte}>{fonte}</li>
            ))}
          </ul>
        )}

        <button
          type="button"
          onClick={() => coletar.mutate()}
          disabled={coletar.isPending}
          className="inline-flex items-center gap-2 rounded-lg bg-brand px-4 py-2 text-xs font-semibold text-white transition-colors hover:bg-brand-dark disabled:opacity-60"
        >
          {coletar.isPending ? (
            <RefreshCw className="size-4 animate-spin" aria-hidden="true" />
          ) : (
            <DownloadCloud className="size-4" aria-hidden="true" />
          )}
          {coletar.isPending ? 'Coletando…' : 'Coletar dados agora'}
        </button>
      </div>
    </Panel>
  );
};

export default PainelColeta;
