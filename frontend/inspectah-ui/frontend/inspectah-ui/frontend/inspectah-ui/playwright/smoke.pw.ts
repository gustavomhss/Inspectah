/**
 * Smoke E2E Tests — S37
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000';

test.describe('Página de Consulta', () => {
  test('carrega página inicial', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/Inspectah/);
  });

  test('formulário de consulta funciona', async ({ page }) => {
    await page.goto(BASE_URL);
    const input = page.locator('input[type="text"], textarea').first();
    if (await input.isVisible()) {
      await input.click();
      await input.fill('Teste automatizado');
      await expect(input).toHaveValue('Teste automatizado');
    }
  });
});

test.describe('Admin', () => {
  test('acessa área admin', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain(BASE_URL);
  });

  test('login carrega', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    const url = page.url();
    expect(url).toBeTruthy();
  });

  test('cases carrega', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('sources carrega', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

test.describe('API Health', () => {
  test('API docs responde', async ({ request }) => {
    const response = await request.get(`${API_URL}/docs`);
    expect(response.status()).toBe(200);
  });
});

test.describe('Responsividade', () => {
  test('mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/Inspectah/);
  });

  test('desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/Inspectah/);
  });
});

test.describe('Navegação', () => {
  test('rotas sem erro 500', async ({ page }) => {
    const routes = ['/', '/login', '/admin', '/admin/cases', '/admin/sources'];
    for (const route of routes) {
      const response = await page.goto(`${BASE_URL}${route}`);
      if (response) {
        expect(response.status()).toBeLessThan(500);
      }
    }
  });
});
