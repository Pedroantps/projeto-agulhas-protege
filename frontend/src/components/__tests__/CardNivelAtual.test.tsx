import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CardNivelAtual } from '../CardNivelAtual';
import type { EstacoesStatusResponse } from '@/services/api';

const estacaoMock: EstacoesStatusResponse = {
  estacao_id: '1',
  codigo_externo: 'SESMARIA-01',
  nome: 'Estação Parque Ipiranga',
  rio: 'Rio Sesmaria',
  nivel_atual_metros: '2.65',
  classificacao_risco: 'ALERTA',
  data_hora_leitura: new Date().toISOString(),
  dados_desatualizados: false,
  cotas: { atencao: '2.00', alerta: '2.50', emergencia: '3.20' },
};

describe('CardNivelAtual', () => {
  it('exibe nome e rio da estação', () => {
    render(<CardNivelAtual estacao={estacaoMock} />);
    expect(screen.getByText('Estação Parque Ipiranga')).toBeInTheDocument();
    expect(screen.getByText('Rio Sesmaria')).toBeInTheDocument();
  });

  it('exibe nível formatado com 2 casas decimais', () => {
    render(<CardNivelAtual estacao={estacaoMock} />);
    expect(screen.getByText('2.65')).toBeInTheDocument();
  });

  it('exibe RiskBadge com classificação correta', () => {
    render(<CardNivelAtual estacao={estacaoMock} />);
    expect(screen.getByRole('status')).toHaveTextContent(/alerta/i);
  });

  it('exibe indicador de dados defasados quando dados_desatualizados é true', () => {
    render(
      <CardNivelAtual
        estacao={{ ...estacaoMock, dados_desatualizados: true }}
      />,
    );
    expect(screen.getByRole('alert')).toHaveTextContent('Defasado');
  });

  it('chama onSelecionar ao clicar', () => {
    const onSelecionar = vi.fn();
    render(
      <CardNivelAtual estacao={estacaoMock} onSelecionar={onSelecionar} />,
    );
    fireEvent.click(screen.getByRole('button'));
    expect(onSelecionar).toHaveBeenCalledTimes(1);
  });

  it('tem aria-label acessível', () => {
    render(<CardNivelAtual estacao={estacaoMock} />);
    const card = screen.getByRole('button');
    expect(card).toHaveAttribute(
      'aria-label',
      expect.stringContaining('Estação Parque Ipiranga'),
    );
  });

  it('dispara onSelecionar ao pressionar a tecla Enter ou Espaço', () => {
    const onSelecionar = vi.fn();
    render(
      <CardNivelAtual estacao={estacaoMock} onSelecionar={onSelecionar} />,
    );

    const card = screen.getByRole('button');
    fireEvent.keyDown(card, { key: 'Enter' });
    expect(onSelecionar).toHaveBeenCalledTimes(1);

    fireEvent.keyDown(card, { key: ' ' });
    expect(onSelecionar).toHaveBeenCalledTimes(2);
  });

  it('aplica estado selecionado visual e acessível', () => {
    render(<CardNivelAtual estacao={estacaoMock} selecionada={true} />);

    const card = screen.getByRole('button');
    expect(card).toHaveAttribute('aria-pressed', 'true');
    expect(card.className).toContain('border-brand');
  });
});
