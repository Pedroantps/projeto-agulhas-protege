import { expect, test } from '@playwright/test';

test.describe('Registro de Ocorrência', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          nome: 'Carlos Operador',
          perfil: 'OPERADOR_DEFESA_CIVIL',
        }),
      });
    });

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

    await page.route('**/api/v1/ocorrencias', async (route) => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'oco-123',
          estacao_id: 'est-1',
          localizacao: 'Rua das Flores, próximo à ponte do Ipiranga',
          descricao:
            'Moradores evacuando casas próximas ao rio. Água subindo.',
          status: 'ABERTA',
          criado_em: new Date().toISOString(),
        }),
      });
    });

    // Login como operador
    await page.goto('/login');
    await page.fill('#email', 'testecomum@teste.com');
    await page.fill('#senha', 'Teste@2029');
    await page.click('#btn-login');
    await page.waitForURL(/.*dashboard/);
  });

  test('registrar ocorrência exibe toast de sucesso', async ({ page }) => {
    await page.click('button:has-text("+ Registrar Ocorrência")', {
      timeout: 5000,
    });
    await page.fill(
      '#localizacao',
      'Rua das Flores, próximo à ponte do Ipiranga',
    );
    await page.fill(
      '#descricao',
      'Moradores evacuando casas próximas ao rio. Água subindo.',
    );
    await page.locator('button[type="submit"]:has-text("Registrar Ocorrência")').click();
    await expect(
      page.getByText(/Ocorrência registrada com sucesso/i),
    ).toBeVisible();
  });
});

