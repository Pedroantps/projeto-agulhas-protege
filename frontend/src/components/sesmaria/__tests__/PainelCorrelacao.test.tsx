import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { PainelCorrelacao } from '../PainelCorrelacao';
import type { CorrelacaoVariavel, TelemetriaBacia } from '@/services/api';

const mockTelemetria: TelemetriaBacia = {
  chuva_sjb_1h_lag4_mm: '12.4',
  chuva_sjb_1h_lag5_mm: '16.8',
  chuva_sjb_1h_lag6_mm: '11.2',
  chuva_sjb_acumulada_12h_mm: '28.5',
  chuva_sjb_acumulada_24h_mm: '45.0',
  chuva_sjb_acumulada_48h_mm: '78.2',
  chuva_sjb_acumulada_168h_mm: '142.0',
  saturacao_solo_sjb_percent: 78.5,
  chuva_resende_acumulada_12h_mm: '18.0',
  chuva_resende_acumulada_24h_mm: '32.4',
  chuva_resende_acumulada_48h_mm: '54.1',
  chuva_resende_acumulada_168h_mm: '112.5',
  vazao_funil_atual_m3s: '385.0',
  vazao_funil_lag1_m3s: '370.0',
  vazao_funil_lag2_m3s: '355.0',
  vazao_funil_media_transito_m3s: '362.5',
};

const mockCorrelacoes: CorrelacaoVariavel[] = [
  {
    id: 'corr-1',
    nome: 'Chuva Horária São José do Barreiro (-5h)',
    origem: 'CEMADEN',
    tipo: 'chuva_sjb_lag',
    lag_horas: '-5 horas',
    coeficiente_r: 0.88,
    relevancia: 'ALTA',
    descricao_fisica: 'Pico de onda de cheia',
  },
];

describe('PainelCorrelacao', () => {
  it('renderiza os eixos de São José do Barreiro, saturação e Represa do Funil', () => {
    render(
      <PainelCorrelacao
        telemetria={mockTelemetria}
        correlacoes={mockCorrelacoes}
        eventosCriticos={42}
      />,
    );

    expect(
      screen.getByText(/Análise de Correlação Hidrológica — Bacia do Rio Sesmaria/i),
    ).toBeInTheDocument();
    expect(screen.getByText('São José do Barreiro (SP)')).toBeInTheDocument();
    expect(screen.getByText('16.8 mm/h')).toBeInTheDocument();
    expect(screen.getByText(/Represa do Funil/i)).toBeInTheDocument();
    expect(screen.getByText('385.0 m³/s')).toBeInTheDocument();
    expect(screen.getByText('+0.88')).toBeInTheDocument();
  });
});
