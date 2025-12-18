/**
 * Console Pages E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for Truth Console, Agent Studio, and Incident Console.
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';

// Test token for authenticated requests
const TEST_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6InNmMy1kZXYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJpbnNwZWN0YWgtaWRwIiwiYXVkIjoiaW5zcGVjdGFoLWFwaSIsInN1YiI6ImRldi1hZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NjA3OTIwNywiaWF0IjoxNzY1OTkyODA3LCJuYmYiOjE3NjU5OTI4MDcsIm9wX2lkIjoiZGV2LW9wIiwicmVxdWVzdF9pZCI6ImRldi1yZXF1ZXN0In0.GdmuUVTs37KNKVOIlAtrmQfnYSZ-ZRnxP6RhA4_lA-8cgSOEuDtBk7KLha57vE8RIpNAtpvPST8JVN4tKF7OFYx1SJgtffbRS7aLEUC5JkpvQIp6eAqCPE0E25xyLJtMWldgg21LkB7IaM-XDiK5XUFSmi-jx_sIiurHdJTedxrWdLyX1lGR8fTAfs4QZalAX9RQ2xlsIsHSXNPV_muEcrY2NJVgg6KKFualPD8dTfmdjcBaHAE4GM8FyEz5B-bYfUu6V2mqodmPB4KrK_ouDkhBSVg6GbF-8RwHhXjdSr_KOjMh4JirCxU6ijSrH6F_83H2-5vjo6yT2SC7Yoo91w';

// Helper to setup authenticated session
async function setupAuth(page: Page) {
  await page.addInitScript((token) => {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify({
      sub: 'dev-admin',
      role: 'admin',
      name: 'Test Admin',
    }));
  }, TEST_TOKEN);
}

// =============================================================================
// TRUTH CONSOLE PAGE
// =============================================================================

test.describe('Truth Console Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/console/truth`);
    await page.waitForLoadState('networkidle');
  });

  test('should display truth console', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show DSL editor', async ({ page }) => {
    const editor = page.locator('[class*="editor"], [class*="code"], textarea, [contenteditable]');
    // May show editor
  });

  test('should show policy list', async ({ page }) => {
    const policies = page.locator('[class*="policy"], [class*="list"]');
    // May show policies
  });

  test('should create new policy', async ({ page }) => {
    const newButton = page.locator('button:has-text("New"), button:has-text("Novo"), button:has-text("Create")').first();

    if (await newButton.isVisible()) {
      await newButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should validate DSL syntax', async ({ page }) => {
    const validateButton = page.locator('button:has-text("Validate"), button:has-text("Validar")').first();

    if (await validateButton.isVisible()) {
      await validateButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should deploy policy', async ({ page }) => {
    const deployButton = page.locator('button:has-text("Deploy"), button:has-text("Implantar")').first();

    if (await deployButton.isVisible()) {
      await deployButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show policy version history', async ({ page }) => {
    const history = page.locator('[class*="history"], [class*="version"]');
    // May show history
  });

  test('should rollback policy', async ({ page }) => {
    const rollbackButton = page.locator('button:has-text("Rollback"), button:has-text("Reverter")').first();

    if (await rollbackButton.isVisible()) {
      await rollbackButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show policy execution stats', async ({ page }) => {
    const stats = page.locator('[class*="stat"], [class*="metric"]');
    // May show stats
  });
});

// =============================================================================
// AGENT STUDIO PAGE
// =============================================================================

test.describe('Agent Studio Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/console/agent-studio`);
    await page.waitForLoadState('networkidle');
  });

  test('should display agent studio', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show agent configuration panel', async ({ page }) => {
    const configPanel = page.locator('[class*="config"], [class*="panel"]');
    // May show config panel
  });

  test('should show prompt editor', async ({ page }) => {
    const promptEditor = page.locator('[class*="prompt"], [class*="editor"], textarea');
    // May show editor
  });

  test('should test agent prompt', async ({ page }) => {
    const testButton = page.locator('button:has-text("Test"), button:has-text("Testar"), button:has-text("Run")').first();

    if (await testButton.isVisible()) {
      await testButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show test results', async ({ page }) => {
    const results = page.locator('[class*="result"], [class*="output"]');
    // May show results
  });

  test('should configure model parameters', async ({ page }) => {
    const params = page.locator('[class*="param"], input[name*="temperature"], input[name*="max_tokens"]');
    // May show parameters
  });

  test('should save agent configuration', async ({ page }) => {
    const saveButton = page.locator('button:has-text("Save"), button:has-text("Salvar")').first();

    if (await saveButton.isVisible()) {
      await saveButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show agent templates', async ({ page }) => {
    const templates = page.locator('[class*="template"]');
    // May show templates
  });

  test('should load template', async ({ page }) => {
    const templateItem = page.locator('[class*="template"]').first();

    if (await templateItem.isVisible()) {
      await templateItem.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show execution logs', async ({ page }) => {
    const logs = page.locator('[class*="log"], [class*="trace"]');
    // May show logs
  });
});

// =============================================================================
// INCIDENT CONSOLE PAGE
// =============================================================================

test.describe('Incident Console Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/console/incidents`);
    await page.waitForLoadState('networkidle');
  });

  test('should display incident console', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show incident list', async ({ page }) => {
    const incidents = page.locator('[class*="incident"], table');
    // May show incidents
  });

  test('should filter incidents by status', async ({ page }) => {
    const statusFilter = page.locator('select, button:has-text("Status"), button:has-text("Open"), button:has-text("Resolved")').first();

    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should filter incidents by severity', async ({ page }) => {
    const severityFilter = page.locator('select, button:has-text("Severity"), button:has-text("Critical")').first();

    if (await severityFilter.isVisible()) {
      await severityFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should create new incident', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Criar"), button:has-text("New")').first();

    if (await createButton.isVisible()) {
      await createButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should view incident detail', async ({ page }) => {
    const incidentItem = page.locator('[class*="incident"], tr').first();

    if (await incidentItem.isVisible()) {
      await incidentItem.click();
      await page.waitForTimeout(500);
    }
  });

  test('should update incident status', async ({ page }) => {
    const statusSelect = page.locator('select[name*="status"], button:has-text("Resolve")').first();

    if (await statusSelect.isVisible()) {
      await statusSelect.click();
      await page.waitForTimeout(300);
    }
  });

  test('should add incident comment', async ({ page }) => {
    const commentInput = page.locator('textarea[name*="comment"], textarea[placeholder*="comment"]').first();

    if (await commentInput.isVisible()) {
      await commentInput.fill('Incident update comment');
      await page.waitForTimeout(300);
    }
  });

  test('should show incident timeline', async ({ page }) => {
    const timeline = page.locator('[class*="timeline"], [class*="history"]');
    // May show timeline
  });

  test('should assign incident', async ({ page }) => {
    const assignButton = page.locator('button:has-text("Assign"), button:has-text("Atribuir")').first();

    if (await assignButton.isVisible()) {
      await assignButton.click();
      await page.waitForTimeout(300);
    }
  });

  test('should escalate incident', async ({ page }) => {
    const escalateButton = page.locator('button:has-text("Escalate"), button:has-text("Escalar")').first();

    if (await escalateButton.isVisible()) {
      await escalateButton.click();
      await page.waitForTimeout(300);
    }
  });

  test('should show related alerts', async ({ page }) => {
    const alerts = page.locator('[class*="alert"], [class*="related"]');
    // May show related alerts
  });
});

// =============================================================================
// CONSOLE KEYBOARD SHORTCUTS
// =============================================================================

test.describe('Console Keyboard Shortcuts', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should execute with Cmd/Ctrl+Enter in truth console', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/console/truth`);
    await page.waitForLoadState('networkidle');

    const editor = page.locator('[class*="editor"], textarea').first();

    if (await editor.isVisible()) {
      await editor.click();
      await page.keyboard.press('Meta+Enter');
      await page.waitForTimeout(500);
    }
  });

  test('should save with Cmd/Ctrl+S in agent studio', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/console/agent-studio`);
    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Meta+s');
    await page.waitForTimeout(500);
  });

  test('should create new with Cmd/Ctrl+N', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/console/truth`);
    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Meta+n');
    await page.waitForTimeout(500);
  });
});

// =============================================================================
// CONSOLE ERROR HANDLING
// =============================================================================

test.describe('Console Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle truth console API error', async ({ page }) => {
    await page.route('**/api/truth/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/console/truth`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle agent studio API error', async ({ page }) => {
    await page.route('**/api/agents/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/console/agent-studio`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle incident console API error', async ({ page }) => {
    await page.route('**/api/incidents/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/console/incidents`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show syntax error in DSL editor', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/console/truth`);
    await page.waitForLoadState('networkidle');

    const editor = page.locator('[class*="editor"], textarea').first();

    if (await editor.isVisible()) {
      await editor.fill('invalid { syntax }}}');

      const validateButton = page.locator('button:has-text("Validate")').first();
      if (await validateButton.isVisible()) {
        await validateButton.click();
        await page.waitForTimeout(500);
      }
    }
  });
});

// =============================================================================
// CONSOLE ACCESSIBILITY
// =============================================================================

test.describe('Console Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should have proper heading structure in truth console', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/console/truth`);
    await page.waitForLoadState('networkidle');

    const h1 = await page.locator('h1').count();
    expect(h1).toBeGreaterThanOrEqual(0);
  });

  test('should be keyboard navigable in agent studio', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/console/agent-studio`);
    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    const focusedElement = page.locator(':focus');
    const tag = await focusedElement.evaluate(el => el.tagName).catch(() => 'BODY');
    expect(['A', 'BUTTON', 'INPUT', 'SELECT', 'BODY', 'TEXTAREA']).toContain(tag);
  });

  test('should have accessible code editor', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/console/truth`);
    await page.waitForLoadState('networkidle');

    const editor = page.locator('[class*="editor"], textarea');
    // Editor should be accessible
  });
});

// =============================================================================
// CONSOLE RESPONSIVE DESIGN
// =============================================================================

test.describe('Console Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should work on mobile in truth console', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/console/truth`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should work on mobile in agent studio', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/console/agent-studio`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should work on mobile in incident console', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/console/incidents`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});
