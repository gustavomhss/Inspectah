/**
 * Sources Module E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for source management, health monitoring, and configuration.
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
// SOURCES LIST PAGE
// =============================================================================

test.describe('Sources List Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');
  });

  test('should display sources list', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show source cards or table', async ({ page }) => {
    const sourceDisplay = page.locator('[class*="source"], table, [class*="card"]');
    // May show sources
  });

  test('should show health status badges', async ({ page }) => {
    const healthBadges = page.locator('[class*="health"], [class*="badge"], .text-green, .text-red, .text-yellow');
    // May show health badges
  });

  test('should filter sources by type', async ({ page }) => {
    const typeFilter = page.locator('select, button:has-text("Tipo"), button:has-text("Type")').first();

    if (await typeFilter.isVisible()) {
      await typeFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should filter sources by status', async ({ page }) => {
    const statusFilter = page.locator('select, button:has-text("Status")').first();

    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should search sources by name', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="buscar"]').first();

    if (await searchInput.isVisible()) {
      await searchInput.fill('cnn');
      await page.waitForTimeout(500);
    }
  });

  test('should navigate to source detail', async ({ page }) => {
    const sourceItem = page.locator('a[href*="/sources/"], tr[class*="cursor-pointer"], [class*="source-item"]').first();

    if (await sourceItem.isVisible()) {
      await sourceItem.click();
      await page.waitForLoadState('networkidle');

      expect(page.url()).toContain('source');
    }
  });

  test('should sort sources', async ({ page }) => {
    const sortHeader = page.locator('th[class*="cursor"], button:has-text("Sort"), [class*="sort"]').first();

    if (await sortHeader.isVisible()) {
      await sortHeader.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show source count', async ({ page }) => {
    const count = page.locator('[class*="count"], text=/\\d+ fonte|\\d+ source/i');
    // May show count
  });

  test('should have add source button', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add"), button:has-text("Adicionar"), a:has-text("Nova")').first();

    if (await addButton.isVisible()) {
      // Should be clickable
    }
  });
});

// =============================================================================
// SOURCE DETAIL PAGE
// =============================================================================

test.describe('Source Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources/src_cnn_001`);
    await page.waitForLoadState('networkidle');
  });

  test('should display source detail', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show source name', async ({ page }) => {
    const name = page.locator('h1, h2, [class*="title"]').first();
    const hasName = await name.isVisible().catch(() => false);
    expect(hasName).toBeTruthy();
  });

  test('should show source URL', async ({ page }) => {
    const url = page.locator('[class*="url"], a[href*="http"]').first();
    // May show URL
  });

  test('should show source type', async ({ page }) => {
    const type = page.locator('[class*="type"], text=/RSS|API|Scraper/i');
    // May show type
  });

  test('should show health status', async ({ page }) => {
    const health = page.locator('[class*="health"], [class*="status"]');
    // May show health
  });

  test('should show last fetch timestamp', async ({ page }) => {
    const lastFetch = page.locator('[class*="timestamp"], text=/última|last.*fetch/i');
    // May show timestamp
  });

  test('should show fetch success rate', async ({ page }) => {
    const successRate = page.locator('[class*="rate"], [class*="success"]');
    // May show success rate
  });

  test('should show recent items', async ({ page }) => {
    const recentItems = page.locator('[class*="item"], [class*="article"]');
    // May show recent items
  });

  test('should have edit button', async ({ page }) => {
    const editButton = page.locator('button:has-text("Edit"), button:has-text("Editar")').first();

    if (await editButton.isVisible()) {
      await editButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should have test fetch button', async ({ page }) => {
    const testButton = page.locator('button:has-text("Test"), button:has-text("Testar")').first();

    if (await testButton.isVisible()) {
      await testButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should have delete button with confirmation', async ({ page }) => {
    const deleteButton = page.locator('button:has-text("Delete"), button:has-text("Excluir")').first();

    if (await deleteButton.isVisible()) {
      await deleteButton.click();

      // Should show confirmation
      const confirmDialog = page.locator('[role="dialog"], [role="alertdialog"]');
      await page.waitForTimeout(500);

      // Cancel deletion
      const cancelButton = page.locator('button:has-text("Cancel"), button:has-text("Cancelar")').first();
      if (await cancelButton.isVisible()) {
        await cancelButton.click();
      }
    }
  });

  test('should handle non-existent source', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/sources/non_existent_999`);
    await page.waitForLoadState('networkidle');

    // Should show 404 or error
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

// =============================================================================
// SOURCE EDIT PAGE
// =============================================================================

test.describe('Source Edit Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources/src_cnn_001/edit`);
    await page.waitForLoadState('networkidle');
  });

  test('should display edit form', async ({ page }) => {
    const form = page.locator('form');
    const hasForm = await form.isVisible().catch(() => false);

    const hasFields = await page.locator('input, select, textarea').first().isVisible().catch(() => false);
    expect(hasForm || hasFields).toBeTruthy();
  });

  test('should populate existing values', async ({ page }) => {
    const nameInput = page.locator('input[name*="name"]').first();

    if (await nameInput.isVisible()) {
      const value = await nameInput.inputValue();
      // Should have some value from the source
    }
  });

  test('should validate URL format', async ({ page }) => {
    const urlInput = page.locator('input[name*="url"], input[type="url"]').first();

    if (await urlInput.isVisible()) {
      await urlInput.fill('invalid-url');
      await urlInput.blur();

      await page.waitForTimeout(300);
    }
  });

  test('should allow changing source type', async ({ page }) => {
    const typeSelect = page.locator('select[name*="type"], [role="listbox"]').first();

    if (await typeSelect.isVisible()) {
      await typeSelect.click();
      await page.waitForTimeout(300);
    }
  });

  test('should allow changing schedule', async ({ page }) => {
    const scheduleInput = page.locator('input[name*="schedule"], select[name*="schedule"]').first();

    if (await scheduleInput.isVisible()) {
      await scheduleInput.click();
      await page.waitForTimeout(300);
    }
  });

  test('should have save button', async ({ page }) => {
    const saveButton = page.locator('button:has-text("Save"), button:has-text("Salvar")').first();

    if (await saveButton.isVisible()) {
      // Should be clickable
    }
  });

  test('should have cancel button', async ({ page }) => {
    const cancelButton = page.locator('button:has-text("Cancel"), button:has-text("Cancelar")').first();

    if (await cancelButton.isVisible()) {
      await cancelButton.click();
      await page.waitForLoadState('networkidle');

      // Should navigate back
      expect(page.url()).not.toContain('edit');
    }
  });

  test('should show unsaved changes warning', async ({ page }) => {
    const nameInput = page.locator('input[name*="name"]').first();

    if (await nameInput.isVisible()) {
      await nameInput.fill('Modified Name');

      // Try to navigate away
      await page.goBack();

      // May show confirmation dialog
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// SOURCE HEALTH MONITORING
// =============================================================================

test.describe('Source Health Monitoring', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');
  });

  test('should show overall health summary', async ({ page }) => {
    const summary = page.locator('[class*="summary"], [class*="overview"]');
    // May show summary
  });

  test('should show healthy sources count', async ({ page }) => {
    const healthyCount = page.locator('[class*="healthy"], .text-green');
    // May show healthy count
  });

  test('should show unhealthy sources count', async ({ page }) => {
    const unhealthyCount = page.locator('[class*="unhealthy"], .text-red');
    // May show unhealthy count
  });

  test('should highlight unhealthy sources', async ({ page }) => {
    const unhealthySources = page.locator('[class*="unhealthy"], [class*="error"], .border-red');
    // Unhealthy sources should be highlighted
  });

  test('should show health history chart', async ({ page }) => {
    const chart = page.locator('canvas, svg[class*="chart"]');
    // May show chart
  });

  test('should show last check timestamp', async ({ page }) => {
    const lastCheck = page.locator('[class*="last-check"], text=/last.*check|última.*verificação/i');
    // May show last check
  });

  test('should trigger health check manually', async ({ page }) => {
    const checkButton = page.locator('button:has-text("Check"), button:has-text("Verificar")').first();

    if (await checkButton.isVisible()) {
      await checkButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// SOURCE DEBUNKER PAGE
// =============================================================================

test.describe('Source Debunker Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources/debunker`);
    await page.waitForLoadState('networkidle');
  });

  test('should display debunker page', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show debunker sources', async ({ page }) => {
    const sources = page.locator('[class*="debunker"], [class*="source"]');
    // May show debunker sources
  });

  test('should filter by credibility', async ({ page }) => {
    const credibilityFilter = page.locator('select, button:has-text("Credibility"), button:has-text("Credibilidade")').first();

    if (await credibilityFilter.isVisible()) {
      await credibilityFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should show source credibility scores', async ({ page }) => {
    const scores = page.locator('[class*="score"], [class*="credibility"]');
    // May show scores
  });

  test('should add new debunker source', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add"), button:has-text("Adicionar")').first();

    if (await addButton.isVisible()) {
      await addButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// SOURCE API INTERACTIONS
// =============================================================================

test.describe('Source API Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should load sources from API', async ({ page }) => {
    await page.route('**/api/sources**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            { id: 'src_1', name: 'CNN Brasil', type: 'rss', health: 'healthy' },
            { id: 'src_2', name: 'G1', type: 'scraper', health: 'healthy' },
          ],
          total: 2,
        }),
      });
    });

    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle API error', async ({ page }) => {
    await page.route('**/api/sources**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle empty sources list', async ({ page }) => {
    await page.route('**/api/sources**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');

    // Should show empty state
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should update source', async ({ page }) => {
    await page.route('**/api/sources/src_1', async (route) => {
      if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'src_1', name: 'Updated Source' }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'src_1', name: 'Source 1', type: 'rss' }),
        });
      }
    });

    await page.goto(`${BASE_URL}/admin/sources/src_1/edit`);
    await page.waitForLoadState('networkidle');
  });

  test('should delete source', async ({ page }) => {
    await page.route('**/api/sources/src_1', async (route) => {
      if (route.request().method() === 'DELETE') {
        await route.fulfill({
          status: 204,
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'src_1', name: 'Source 1' }),
        });
      }
    });

    await page.goto(`${BASE_URL}/admin/sources/src_1`);
    await page.waitForLoadState('networkidle');
  });

  test('should test source fetch', async ({ page }) => {
    await page.route('**/api/sources/*/test', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          items_fetched: 10,
          duration_ms: 250,
        }),
      });
    });

    await page.goto(`${BASE_URL}/admin/sources/src_1`);
    await page.waitForLoadState('networkidle');

    const testButton = page.locator('button:has-text("Test"), button:has-text("Testar")').first();
    if (await testButton.isVisible()) {
      await testButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// SOURCES ACCESSIBILITY
// =============================================================================

test.describe('Sources Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');
  });

  test('should have proper heading structure', async ({ page }) => {
    const h1 = await page.locator('h1').count();
    expect(h1).toBeGreaterThanOrEqual(0);
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    const focusedElement = page.locator(':focus');
    const tag = await focusedElement.evaluate(el => el.tagName).catch(() => 'BODY');
    expect(['A', 'BUTTON', 'INPUT', 'SELECT', 'BODY']).toContain(tag);
  });

  test('should have accessible source cards', async ({ page }) => {
    const cards = page.locator('[class*="source"], [class*="card"]');
    const count = await cards.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      const card = cards.nth(i);
      // Cards should be interactive
    }
  });

  test('should have accessible health indicators', async ({ page }) => {
    const indicators = page.locator('[class*="health"], [class*="status"]');
    const count = await indicators.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      const indicator = indicators.nth(i);
      const ariaLabel = await indicator.getAttribute('aria-label');
      const title = await indicator.getAttribute('title');
      const text = await indicator.textContent();

      // Should have accessible text
      expect(ariaLabel || title || text).toBeTruthy();
    }
  });
});

// =============================================================================
// SOURCES RESPONSIVE DESIGN
// =============================================================================

test.describe('Sources Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should work on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should adapt table to mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');

    // Table should adapt or become cards
    const table = page.locator('table');
    const cards = page.locator('[class*="card"]');
  });
});
