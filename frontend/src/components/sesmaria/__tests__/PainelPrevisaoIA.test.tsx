import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { PainelPrevisaoIA } from '../PainelPrevisaoIA';
import type { PrevisaoNivelDia } from '@/services/api';

const mockPrevisoes: PrevisaoNivelDia[] = [
  {
    dia_offset: 1,
    rotulo: '+24h (Amanhã)',
    data_alvo: '2026-09-22T00:00:00Z',
    chuva_prevista_mm: '38.0',
    vazao_funil_esperada_m3s: '410.0',
    nivel_estimado_metros: '2.62',
    probabilidade_alerta: 82.0,
    probabilidade_emergencia: 18.0,
    classificacao_risco: 'ALERTA',
    confiabilidade_percentual: 89.5,
  },
  {
    dia_offset: 2,
    rotulo: '+48h (2 dias)',
    data_alvo: '2026-09-23T00:00:00Z',
    chuva_prevista_mm: '22.0',
    vazao_funil_esperada_m3s: '360.0',
    nivel_estimado_metros: '2.30',
    probabilidade_alerta: 40.0,
    probabilidade_emergencia: 5.0,
    classificacao_risco: 'ATENCAO',
    confiabilidade_percentual: 80.0,
  },
];

describe('PainelPrevisaoIA', () => {
  it('renderiza os cards de previsão para os horizontes futuros', () => {
    render(<PainelPrevisaoIA previsoes={mockPrevisoes} />);

    expect(
      screen.getByText(/Modelo Preditivo de IA — Projeção do Rio Sesmaria/i),
    ).toBeInTheDocument();
    expect(screen.getByText('+24h (Amanhã)')).toBeInTheDocument();
    expect(screen.getByText('2.62')).toBeInTheDocument();
    expect(screen.getByText('38.0 mm')).toBeInTheDocument();
    expect(screen.getByText('82%')).toBeInTheDocument();
  });
});
