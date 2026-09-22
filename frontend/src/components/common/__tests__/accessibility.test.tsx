import axe from 'axe-core';
import { render } from '@testing-library/react';

import { useThemeStore } from '@/stores/themeStore';

import { ConfirmModal } from '../ConfirmModal';
import { Panel } from '../Panel';
import { RiskBadge } from '../RiskBadge';
import { Skeleton } from '../Skeleton';
import { ThemeToggle } from '../ThemeToggle';

type Rgb = [number, number, number];

function hexToRgb(hex: string): Rgb {
  return [1, 3, 5].map((index) =>
    Number.parseInt(hex.slice(index, index + 2), 16),
  ) as Rgb;
}

function luminance([red, green, blue]: Rgb) {
  const [r, g, b] = [red, green, blue].map((channel) => {
    const value = channel / 255;
    return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(foreground: Rgb, background: Rgb) {
  const lighter = Math.max(luminance(foreground), luminance(background));
  const darker = Math.min(luminance(foreground), luminance(background));
  return (lighter + 0.05) / (darker + 0.05);
}

function blend(foreground: Rgb, background: Rgb, alpha: number): Rgb {
  return foreground.map((channel, index) =>
    Math.round(channel * alpha + background[index] * (1 - alpha)),
  ) as Rgb;
}

const AXE_JSDOM_OPTIONS = {
  rules: {
    // JSDOM não calcula estilos e canvas; contraste é validado matematicamente abaixo.
    'color-contrast': { enabled: false },
  },
};

describe('acessibilidade dos componentes comuns', () => {
  beforeEach(() => {
    useThemeStore.setState({ theme: 'light' });
    document.documentElement.classList.remove('dark');
  });

  it('não possui violações detectáveis pelo axe no conjunto base', async () => {
    const { container } = render(
      <main>
        <Panel title="Situação das estações">
          <RiskBadge nivel="NORMAL" />
          <Skeleton />
          <ThemeToggle />
        </Panel>
      </main>,
    );

    const results = await axe.run(container, AXE_JSDOM_OPTIONS);
    expect(results.violations).toEqual([]);
  });

  it('não possui violações detectáveis pelo axe no modal', async () => {
    const { baseElement } = render(
      <ConfirmModal
        aberto
        titulo="Encerrar alerta"
        descricao="Esta ação não poderá ser desfeita."
        variante="danger"
        onConfirmar={() => undefined}
        onCancelar={() => undefined}
      />,
    );

    const results = await axe.run(baseElement, AXE_JSDOM_OPTIONS);
    expect(results.violations).toEqual([]);
  });

  it.each([
    ['normal claro', '#065f46', '#d1fae5'],
    ['atenção claro', '#92400e', '#fef3c7'],
    ['alerta claro', '#9a3412', '#ffedd5'],
    ['emergência claro', '#991b1b', '#fee2e2'],
    ['botão de marca', '#ffffff', '#0369a1'],
  ])('mantém contraste WCAG AA em %s', (_, foreground, background) => {
    expect(
      contrast(hexToRgb(foreground), hexToRgb(background)),
    ).toBeGreaterThanOrEqual(4.5);
  });

  it.each([
    ['normal escuro', '#34d399', '#065f46'],
    ['atenção escuro', '#fbbf24', '#92400e'],
    ['alerta escuro', '#fb923c', '#9a3412'],
    ['emergência escuro', '#f87171', '#991b1b'],
  ])('mantém contraste WCAG AA em %s', (_, foreground, overlay) => {
    const background = blend(hexToRgb(overlay), hexToRgb('#1e293b'), 0.3);
    expect(contrast(hexToRgb(foreground), background)).toBeGreaterThanOrEqual(
      4.5,
    );
  });
});
