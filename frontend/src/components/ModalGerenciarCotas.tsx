import React, { useEffect, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, Save, Settings } from 'lucide-react';
import toast from 'react-hot-toast';
import { ConfirmModal } from '@/components/common';
import { ApiError, atualizarCotas } from '@/services/api';

interface ModalGerenciarCotasProps {
  estacaoId: string;
  estacaoNome: string;
  cotasAtuais: {
    atencao: string | number;
    alerta: string | number;
    emergencia: string | number;
  };
  aberto: boolean;
  onFechar: () => void;
}

export const ModalGerenciarCotas: React.FC<ModalGerenciarCotasProps> = ({
  estacaoId,
  estacaoNome,
  cotasAtuais,
  aberto,
  onFechar,
}) => {
  const [cotaAtencao, setCotaAtencao] = useState(
    cotasAtuais.atencao?.toString() ?? '',
  );
  const [cotaAlerta, setCotaAlerta] = useState(
    cotasAtuais.alerta?.toString() ?? '',
  );
  const [cotaEmergencia, setCotaEmergencia] = useState(
    cotasAtuais.emergencia?.toString() ?? '',
  );
  const [descricao, setDescricao] = useState('');
  const [mostrarConfirmacao, setMostrarConfirmacao] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (aberto) {
      setCotaAtencao(cotasAtuais.atencao?.toString() ?? '');
      setCotaAlerta(cotasAtuais.alerta?.toString() ?? '');
      setCotaEmergencia(cotasAtuais.emergencia?.toString() ?? '');
      setDescricao('');
      setMostrarConfirmacao(false);
    }
  }, [aberto, cotasAtuais]);

  const mutation = useMutation({
    mutationFn: () =>
      atualizarCotas(estacaoId, {
        cota_atencao: cotaAtencao,
        cota_alerta: cotaAlerta,
        cota_emergencia: cotaEmergencia,
      }),
    onSuccess: () => {
      toast.success('Cotas de risco atualizadas com sucesso.');
      void queryClient.invalidateQueries({ queryKey: ['estacoes'] });
      onFechar();
    },
    onError: (error: unknown) => {
      if (error instanceof ApiError) {
        if (error.status === 403) {
          toast.error('Acesso restrito ao perfil de Administrador.');
        } else if (error.status === 422) {
          toast.error(error.detail || 'Verifique os valores das cotas.');
        } else {
          toast.error(error.detail || 'Erro ao atualizar cotas.');
        }
      } else {
        toast.error('Não foi possível atualizar as cotas. Tente novamente.');
      }
    },
  });

  const atencao = parseFloat(cotaAtencao);
  const alerta = parseFloat(cotaAlerta);
  const emergencia = parseFloat(cotaEmergencia);
  const cotasValidas =
    !isNaN(atencao) &&
    !isNaN(alerta) &&
    !isNaN(emergencia) &&
    atencao > 0 &&
    alerta > atencao &&
    emergencia > alerta;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cotasValidas) {
      toast.error(
        'As cotas devem seguir: Atenção < Alerta < Emergência (todas > 0).',
      );
      return;
    }
    setMostrarConfirmacao(true);
  };

  const confirmarAlteracao = () => {
    setMostrarConfirmacao(false);
    mutation.mutate();
  };

  if (!aberto) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm transition-opacity"
        onClick={onFechar}
        aria-hidden="true"
        data-testid="modal-cotas-backdrop"
      />

      {/* Modal Dialog */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-cotas-titulo"
      >
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-md space-y-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-700 dark:bg-slate-800"
        >
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/30">
              <Settings
                className="size-5 text-blue-600 dark:text-blue-400"
                aria-hidden="true"
              />
            </div>
            <div>
              <h2
                id="modal-cotas-titulo"
                className="text-lg font-bold text-slate-800 dark:text-slate-100"
              >
                Gerenciar Cotas de Risco
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {estacaoNome}
              </p>
            </div>
          </div>

          {/* Indicador visual de ordenação */}
          <div className="flex items-center justify-center gap-2 font-mono text-xs text-slate-400">
            <span className={atencao > 0 ? 'text-amber-600' : ''}>Atenção</span>
            <span>&lt;</span>
            <span
              className={alerta > atencao ? 'text-orange-600' : 'text-red-500'}
            >
              Alerta
            </span>
            <span>&lt;</span>
            <span
              className={
                emergencia > alerta ? 'text-red-600' : 'text-red-500'
              }
            >
              Emergência
            </span>
          </div>

          {/* Campos de cota */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label
                htmlFor="cota-atencao"
                className="mb-1 block text-xs font-semibold text-amber-600 dark:text-amber-400"
              >
                Atenção (m)
              </label>
              <input
                id="cota-atencao"
                type="number"
                step="0.01"
                min="0.01"
                value={cotaAtencao}
                onChange={(e) => setCotaAtencao(e.target.value)}
                className="w-full rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-center font-mono text-sm outline-none focus:ring-2 focus:ring-amber-400 dark:border-amber-800 dark:bg-amber-900/20 dark:text-amber-300"
                required
              />
            </div>
            <div>
              <label
                htmlFor="cota-alerta"
                className="mb-1 block text-xs font-semibold text-orange-600 dark:text-orange-400"
              >
                Alerta (m)
              </label>
              <input
                id="cota-alerta"
                type="number"
                step="0.01"
                min="0.01"
                value={cotaAlerta}
                onChange={(e) => setCotaAlerta(e.target.value)}
                className="w-full rounded-lg border border-orange-200 bg-orange-50 px-3 py-2 text-center font-mono text-sm outline-none focus:ring-2 focus:ring-orange-400 dark:border-orange-800 dark:bg-orange-900/20 dark:text-orange-300"
                required
              />
            </div>
            <div>
              <label
                htmlFor="cota-emergencia"
                className="mb-1 block text-xs font-semibold text-red-600 dark:text-red-400"
              >
                Emergência (m)
              </label>
              <input
                id="cota-emergencia"
                type="number"
                step="0.01"
                min="0.01"
                value={cotaEmergencia}
                onChange={(e) => setCotaEmergencia(e.target.value)}
                className="w-full rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-center font-mono text-sm outline-none focus:ring-2 focus:ring-red-400 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300"
                required
              />
            </div>
          </div>

          {/* Justificativa / Observação */}
          <div>
            <label
              htmlFor="cota-descricao"
              className="mb-1 block text-xs font-semibold text-slate-600 dark:text-slate-400"
            >
              Justificativa da alteração (opcional)
            </label>
            <input
              id="cota-descricao"
              type="text"
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              placeholder="Ex: Revisão pós-dragagem do Rio Sesmaria"
              maxLength={255}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
            />
          </div>

          {/* Botões */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onFechar}
              className="flex-1 rounded-lg border border-slate-300 py-2.5 font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-blue-600 py-2.5 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-blue-500 dark:hover:bg-blue-600"
            >
              {mutation.isPending ? (
                <Loader2 className="size-4 animate-spin" aria-hidden="true" />
              ) : (
                <Save className="size-4" aria-hidden="true" />
              )}
              Salvar Cotas
            </button>
          </div>
        </form>
      </div>

      {/* Confirmação antes de salvar */}
      <ConfirmModal
        aberto={mostrarConfirmacao}
        titulo="Confirmar alteração de cotas?"
        descricao={`Atenção: ${cotaAtencao}m → Alerta: ${cotaAlerta}m → Emergência: ${cotaEmergencia}m\n\nEsta ação altera os limiares de classificação de risco para a estação ${estacaoNome}. Todas as leituras futuras serão classificadas com os novos valores.`}
        textoBotaoConfirmar="Confirmar Alteração"
        onConfirmar={confirmarAlteracao}
        onCancelar={() => setMostrarConfirmacao(false)}
      />
    </>
  );
};
