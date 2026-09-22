import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

import { ConfirmModal } from '../ConfirmModal';

function createProps() {
  return {
    aberto: true,
    titulo: 'Confirmar ação',
    descricao: 'Tem certeza?',
    onConfirmar: vi.fn(),
    onCancelar: vi.fn(),
  };
}

describe('ConfirmModal', () => {
  it('não renderiza quando fechado', () => {
    render(<ConfirmModal {...createProps()} aberto={false} />);
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
  });

  it('renderiza, associa textos e move foco para Cancelar', () => {
    render(<ConfirmModal {...createProps()} />);

    const dialog = screen.getByRole('alertdialog', {
      name: 'Confirmar ação',
      description: 'Tem certeza?',
    });
    expect(dialog).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancelar' })).toHaveFocus();
    expect(document.body).toHaveStyle({ overflow: 'hidden' });
  });

  it('confirma, cancela com Escape e cancela pelo backdrop', async () => {
    const user = userEvent.setup();
    const props = createProps();
    render(<ConfirmModal {...props} textoBotaoConfirmar="Excluir" />);

    await user.click(screen.getByRole('button', { name: 'Excluir' }));
    expect(props.onConfirmar).toHaveBeenCalledOnce();

    fireEvent.keyDown(screen.getByRole('alertdialog'), { key: 'Escape' });
    fireEvent.click(screen.getByTestId('confirm-modal-backdrop'));
    expect(props.onCancelar).toHaveBeenCalledTimes(2);
  });

  it('retém o foco dentro do diálogo ao navegar com Tab', () => {
    render(<ConfirmModal {...createProps()} />);
    const dialog = screen.getByRole('alertdialog');
    const cancelar = screen.getByRole('button', { name: 'Cancelar' });
    const confirmar = screen.getByRole('button', { name: 'Confirmar' });

    confirmar.focus();
    fireEvent.keyDown(dialog, { key: 'Tab' });
    expect(cancelar).toHaveFocus();

    fireEvent.keyDown(dialog, { key: 'Tab', shiftKey: true });
    expect(confirmar).toHaveFocus();
  });

  it('bloqueia ações e informa carregamento', () => {
    const props = createProps();
    render(<ConfirmModal {...props} carregando variante="danger" />);

    const dialog = screen.getByRole('alertdialog');
    expect(dialog).toHaveAttribute('aria-busy', 'true');
    expect(dialog).toHaveFocus();
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Aguarde...' })).toBeDisabled();

    fireEvent.keyDown(dialog, { key: 'Escape' });
    fireEvent.click(screen.getByTestId('confirm-modal-backdrop'));
    expect(props.onCancelar).not.toHaveBeenCalled();
  });

  it('restaura o foco ao fechar', () => {
    const trigger = document.createElement('button');
    document.body.appendChild(trigger);
    trigger.focus();
    const props = createProps();
    const { rerender } = render(<ConfirmModal {...props} />);

    rerender(<ConfirmModal {...props} aberto={false} />);
    expect(trigger).toHaveFocus();
    trigger.remove();
  });
});
