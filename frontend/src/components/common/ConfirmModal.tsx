import { AlertTriangle } from 'lucide-react';
import {
  useEffect,
  useId,
  useRef,
  type KeyboardEvent as ReactKeyboardEvent,
} from 'react';

interface ConfirmModalProps {
  aberto: boolean;
  titulo: string;
  descricao: string;
  textoBotaoConfirmar?: string;
  variante?: 'danger' | 'default';
  carregando?: boolean;
  onConfirmar: () => void;
  onCancelar: () => void;
}

const FOCUSABLE_ELEMENTS =
  'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function ConfirmModal({
  aberto,
  titulo,
  descricao,
  textoBotaoConfirmar = 'Confirmar',
  variante = 'default',
  carregando = false,
  onConfirmar,
  onCancelar,
}: ConfirmModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const cancelarRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const generatedId = useId();
  const titleId = `${generatedId}-title`;
  const descriptionId = `${generatedId}-description`;

  useEffect(() => {
    if (!aberto) return;

    previousFocusRef.current =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    (cancelarRef.current ?? dialogRef.current)?.focus();

    return () => {
      document.body.style.overflow = previousOverflow;
      previousFocusRef.current?.focus();
    };
  }, [aberto]);

  useEffect(() => {
    if (aberto && carregando) dialogRef.current?.focus();
  }, [aberto, carregando]);

  if (!aberto) return null;

  const handleKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      if (!carregando) onCancelar();
      return;
    }

    if (event.key !== 'Tab' || !dialogRef.current) return;

    const focusable = Array.from(
      dialogRef.current.querySelectorAll<HTMLElement>(FOCUSABLE_ELEMENTS),
    );

    if (focusable.length === 0) {
      event.preventDefault();
      dialogRef.current.focus();
      return;
    }

    const first = focusable[0];
    const last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  const confirmButtonClasses =
    variante === 'danger'
      ? 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-400'
      : 'bg-brand-dark text-white hover:bg-sky-800 disabled:bg-brand/50';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={carregando ? undefined : onCancelar}
        aria-hidden="true"
        data-testid="confirm-modal-backdrop"
      />
      <div
        ref={dialogRef}
        className="relative w-full max-w-sm animate-slide-up rounded-2xl border border-slate-200 bg-white p-6 shadow-modal motion-reduce:animate-none dark:border-slate-700 dark:bg-slate-800"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
        aria-busy={carregando}
        tabIndex={-1}
        onKeyDown={handleKeyDown}
      >
        {variante === 'danger' ? (
          <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
            <AlertTriangle
              className="size-6 text-red-600 dark:text-red-400"
              aria-hidden="true"
            />
          </div>
        ) : null}
        <h3
          id={titleId}
          className="text-center text-lg font-bold text-slate-800 dark:text-slate-100"
        >
          {titulo}
        </h3>
        <p
          id={descriptionId}
          className="mt-2 whitespace-pre-line text-center text-sm text-slate-600 dark:text-slate-300"
        >
          {descricao}
        </p>
        <div className="mt-6 flex gap-3">
          <button
            ref={cancelarRef}
            type="button"
            onClick={onCancelar}
            disabled={carregando}
            className="flex-1 rounded-lg border border-slate-300 py-2.5 font-medium text-slate-700 transition-colors hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 disabled:opacity-50 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-700 dark:focus:ring-offset-slate-800"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirmar}
            disabled={carregando}
            className={`flex-1 rounded-lg py-2.5 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 disabled:cursor-not-allowed dark:focus:ring-offset-slate-800 ${confirmButtonClasses}`}
          >
            {carregando ? 'Aguarde...' : textoBotaoConfirmar}
          </button>
        </div>
      </div>
    </div>
  );
}
