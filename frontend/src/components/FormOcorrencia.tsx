import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Panel } from '@/components/common';
import { ApiError, criarOcorrencia } from '@/services/api';

interface FormOcorrenciaProps {
  estacaoId: string;
  alertaId?: string;
  onConcluir: () => void;
}

export const FormOcorrencia: React.FC<FormOcorrenciaProps> = ({
  estacaoId,
  alertaId,
  onConcluir,
}) => {
  const [localizacao, setLocalizacao] = useState('');
  const [descricao, setDescricao] = useState('');
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () =>
      criarOcorrencia({
        estacao_id: estacaoId,
        alerta_id: alertaId,
        localizacao: localizacao.trim(),
        descricao: descricao.trim(),
      }),
    onSuccess: () => {
      toast.success('Ocorrência registrada com sucesso!');
      void queryClient.invalidateQueries({ queryKey: ['ocorrencias'] });
      onConcluir();
    },
    onError: (error: unknown) => {
      if (error instanceof ApiError) {
        toast.error(error.detail);
      } else if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error('Erro ao registrar ocorrência.');
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (localizacao.trim().length < 5) {
      toast.error('Localização deve ter no mínimo 5 caracteres.');
      return;
    }
    if (descricao.trim().length < 10) {
      toast.error('Descrição deve ter no mínimo 10 caracteres.');
      return;
    }
    mutation.mutate();
  };

  return (
    <Panel title="Registrar Ocorrência de Campo">
      <form
        onSubmit={handleSubmit}
        className="space-y-4"
        aria-label="Formulário de registro de ocorrência"
      >
        <div>
          <label
            htmlFor="localizacao"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Localização *
          </label>
          <input
            id="localizacao"
            type="text"
            required
            minLength={5}
            value={localizacao}
            onChange={(e) => setLocalizacao(e.target.value)}
            placeholder="Ex: Rua das Flores, 123 — próximo à ponte do Ipiranga"
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
          />
        </div>
        <div>
          <label
            htmlFor="descricao"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Descrição da Ocorrência *
          </label>
          <textarea
            id="descricao"
            required
            minLength={10}
            rows={4}
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            placeholder="Descreva a situação observada em campo..."
            className="w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
          />
        </div>
        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={onConcluir}
            className="flex-1 rounded-lg border border-slate-300 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="flex-1 rounded-lg bg-brand py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-dark disabled:bg-brand/50"
          >
            {mutation.isPending ? 'Salvando...' : 'Registrar Ocorrência'}
          </button>
        </div>
      </form>
    </Panel>
  );
};
