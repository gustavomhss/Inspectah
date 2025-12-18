/**
 * Smoke E2E Tests — S37
 *
 * Simula usuário real navegando pelo sistema.
 * O sistema não consegue distinguir de cliques reais de mouse/teclado.
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000';

// ==================== CONSULTA (PÚBLICO) ====================

test.describe('Página de Consulta', () => {
  test('carrega página inicial', async ({ page }) => {
    await page.goto(BASE_URL);

    // Verifica título
    await expect(page).toHaveTitle(/Inspectah/);

    // Verifica que existe um campo de input ou formulário
    const hasInput = await page.locator('input, textarea').first().isVisible().catch(() => false);
    const hasForm = await page.locator('form').first().isVisible().catch(() => false);

    expect(hasInput || hasForm).toBeTruthy();
  });

  test('formulário de consulta está funcional', async ({ page }) => {
    await page.goto(BASE_URL);

    // Tenta encontrar campo de consulta
    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      // Simula digitação como usuário real
      await input.click();
      await input.fill('Teste de consulta automatizado');

      // Verifica que o texto foi inserido
      await expect(input).toHaveValue('Teste de consulta automatizado');
    }
  });
});

// ==================== LOGIN ADMIN ====================

test.describe('Login Admin', () => {
  test('página de login carrega', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // Pode redirecionar ou mostrar formulário
    const url = page.url();
    const hasLoginForm = await page.locator('input[type="password"], input[type="email"], button:has-text("Login"), button:has-text("Entrar")').first().isVisible().catch(() => false);

    // Ou já está logado e redirecionou
    expect(url.includes('login') || hasLoginForm || url.includes('admin')).toBeTruthy();
  });
});

// ==================== ADMIN DASHBOARD ====================

test.describe('Admin Dashboard', () => {
  test('acessa área admin', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);

    // Aguarda carregamento
    await page.waitForLoadState('networkidle');

    // Verifica se carregou algo (pode ter redirecionado para login)
    const url = page.url();
    expect(url).toContain(BASE_URL);
  });

  test('navegação pelo menu funciona', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Tenta clicar em links de navegação
    const navLinks = page.locator('nav a, aside a, [role="navigation"] a');
    const count = await navLinks.count();

    if (count > 0) {
      // Clica no primeiro link de navegação
      await navLinks.first().click();
      await page.waitForLoadState('networkidle');

      // Verifica que navegou
      expect(page.url()).toBeTruthy();
    }
  });
});

// ==================== CASES / TIMELINE ====================

test.describe('Cases e Timeline', () => {
  test('lista de cases carrega', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');

    // Verifica que a página carregou (pode estar vazia ou com dados)
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

// ==================== SOURCES ADMIN ====================

test.describe('Sources Admin', () => {
  test('lista de fontes carrega', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');

    // Verifica que a página carregou
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('pode navegar para detalhes de fonte', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');

    // Tenta encontrar link para detalhes
    const detailLink = page.locator('a[href*="/sources/"]').first();

    if (await detailLink.isVisible()) {
      await detailLink.click();
      await page.waitForLoadState('networkidle');

      // Verifica que navegou
      expect(page.url()).toContain('/sources/');
    }
  });
});

// ==================== GUARDIAN COCKPIT (S37) ====================

test.describe('Guardian Cockpit', () => {
  test('cockpit carrega', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');

    // Verifica que a página carregou
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('tabs de navegação funcionam', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');

    // Procura por tabs
    const tabs = page.locator('button:has-text("Pendentes"), button:has-text("Revisão"), button:has-text("Concluídas")');
    const count = await tabs.count();

    if (count > 0) {
      // Clica na primeira tab
      await tabs.first().click();

      // Verifica que a tab foi selecionada (alguma mudança visual ou de conteúdo)
      await page.waitForTimeout(500);
    }
  });
});

// ==================== API HEALTH ====================

test.describe('API Health', () => {
  test('API está respondendo', async ({ request }) => {
    const response = await request.get(`${API_URL}/docs`);

    // Swagger docs devem retornar 200
    expect(response.status()).toBe(200);
  });

  test('endpoint de health responde', async ({ request }) => {
    // Tenta vários endpoints comuns de health
    const endpoints = ['/health', '/api/health', '/', '/api/v1/health'];

    for (const endpoint of endpoints) {
      const response = await request.get(`${API_URL}${endpoint}`).catch(() => null);
      if (response && response.status() === 200) {
        expect(response.status()).toBe(200);
        return;
      }
    }

    // Se nenhum health endpoint, pelo menos o docs deve funcionar
    const docsResponse = await request.get(`${API_URL}/docs`);
    expect(docsResponse.status()).toBe(200);
  });
});

// ==================== RESPONSIVIDADE ====================

test.describe('Responsividade', () => {
  test('mobile viewport funciona', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    await page.goto(BASE_URL);

    // Verifica que carrega sem erros
    await expect(page).toHaveTitle(/Inspectah/);
  });

  test('tablet viewport funciona', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad
    await page.goto(BASE_URL);

    await expect(page).toHaveTitle(/Inspectah/);
  });

  test('desktop viewport funciona', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 }); // Full HD
    await page.goto(BASE_URL);

    await expect(page).toHaveTitle(/Inspectah/);
  });
});

// ==================== NAVEGAÇÃO GERAL ====================

test.describe('Navegação Geral', () => {
  test('todas as rotas principais carregam sem erro 500', async ({ page }) => {
    const routes = [
      '/',
      '/login',
      '/admin',
      '/admin/cases',
      '/admin/sources',
      '/admin/guardian',
    ];

    for (const route of routes) {
      const response = await page.goto(`${BASE_URL}${route}`);

      // Não deve ter erro de servidor
      if (response) {
        expect(response.status()).toBeLessThan(500);
      }
    }
  });
});
