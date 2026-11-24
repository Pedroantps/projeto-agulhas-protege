import { expect, test } from '@playwright/test';

test.describe('Fluxo de Login', () => {
  test('login com credenciais válidas redireciona para dashboard', async ({
    page,
  }) => {
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          nome: 'Operador Defesa Civil',
          perfil: 'OPERADOR_DEFESA_CIVIL',
        }),
      });
    });

    await page.goto('/login');
    await page.fill('#email', 'testecomum@teste.com');
    await page.fill('#senha', 'Teste@2029');
    await page.click('#btn-login');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('login com senha errada exibe toast de erro', async ({ page }) => {
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Email ou senha inválidos',
        }),
      });
    });

    await page.goto('/login');
    await page.fill('#email', 'testecomum@teste.com');
    await page.fill('#senha', 'senha_errada');
    await page.click('#btn-login');
    await expect(page.getByRole('status')).toContainText(
      /inválidos|credenciais/i,
    );
  });

  test('rota protegida sem login redireciona para /login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*login/);
  });
});
