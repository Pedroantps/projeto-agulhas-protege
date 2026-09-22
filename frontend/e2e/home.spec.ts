import { expect, test } from '@playwright/test';

test.describe('Home Pública', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/estacoes/status-atual', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            estacao_id: 'est-1',
            codigo_externo: 'SESMARIA-01',
            nome: 'Estação Parque Ipiranga',
            rio: 'Rio Sesmaria',
            nivel_atual_metros: '2.65',
            classificacao_risco: 'ALERTA',
            data_hora_leitura: new Date().toISOString(),
            dados_desatualizados: false,
            cotas: { atencao: '2.00', alerta: '2.50', emergencia: '3.20' },
          },
        ]),
      });
    });

    await page.route('**/api/v1/leituras/historico*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'l1',
            data_hora: new Date().toISOString(),
            nivel_metros: '2.65',
            classificacao: 'ALERTA',
          },
        ]),
      });
    });

    await page.goto('/');
  });

  test('exibe cards de estações com nível e risco', async ({ page }) => {
    await expect(
      page.getByRole('button', { name: /Estação/i }).first(),
    ).toBeVisible({ timeout: 10000 });
  });

  test('selecionar card exibe gráfico histórico', async ({ page }) => {
    const primeiroCard = page.getByRole('button', { name: /Estação/i }).first();
    await primeiroCard.click();
    await expect(
      page.getByRole('heading', { name: /Histórico/i }),
    ).toBeVisible();
  });

  test('seletor de período muda dados do gráfico', async ({ page }) => {
    await page.getByRole('button', { name: /Estação/i }).first().click();
    await page.click('button:has-text("7d")');
    await expect(page.locator('button[aria-pressed="true"]')).toContainText(
      '7d',
    );
  });

  test('dark mode toggle funciona', async ({ page }) => {
    await page.click('#theme-toggle');
    await expect(page.locator('html')).toHaveClass(/dark/);
    await page.click('#theme-toggle');
    await expect(page.locator('html')).not.toHaveClass(/dark/);
  });
});
