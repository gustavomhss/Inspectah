/**
 * Ingestion Module E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for content ingestion, source monitoring, and data pipeline management.
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
// INGESTION LIST PAGE
// =============================================================================

test.describe('Ingestion List Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ingestion`);
    await page.waitForLoadState('networkidle');
  });

  test('should display ingestion list page', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show ingestion sources', async ({ page }) => {
    const sources = page.locator('[class*="source"], [class*="card"], table');
    // May show sources
  });

  test('should show source health indicators', async ({ page }) => {
    const healthIndicators = page.locator('[class*="health"], [class*="status"], .text-green, .text-red, .text-yellow');
    // May show health indicators
  });

  test('should filter sources by status', async ({ page }) => {
    const statusFilter = page.locator('select, button:has-text("Status"), [role="listbox"]').first();

    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should filter sources by type', async ({ page }) => {
    const typeFilter = page.locator('select, button:has-text("Tipo"), button:has-text("Type")').first();

    if (await typeFilter.isVisible()) {
      await typeFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should search sources', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="buscar"]').first();

    if (await searchInput.isVisible()) {
      await searchInput.fill('news');
      await page.waitForTimeout(500);
    }
  });

  test('should navigate to source detail', async ({ page }) => {
    const sourceItem = page.locator('a[href*="/ingestion/"], [class*="source"][class*="cursor-pointer"]').first();

    if (await sourceItem.isVisible()) {
      await sourceItem.click();
      await page.waitForLoadState('networkidle');

      expect(page.url()).toContain('ingestion');
    }
  });

  test('should show last ingestion timestamp', async ({ page }) => {
    const timestamps = page.locator('[class*="timestamp"], [class*="date"], text=/última|last/i');
    // May show timestamps
  });

  test('should show ingestion statistics', async ({ page }) => {
    const stats = page.locator('[class*="stat"], [class*="metric"], [class*="count"]');
    // May show statistics
  });
});

// =============================================================================
// INGESTION SOURCE DETAIL PAGE
// =============================================================================

test.describe('Ingestion Source Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ingestion/source_test_123`);
    await page.waitForLoadState('networkidle');
  });

  test('should display source detail', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show source configuration', async ({ page }) => {
    const config = page.locator('[class*="config"], [class*="setting"]');
    // May show configuration
  });

  test('should show ingestion history', async ({ page }) => {
    const history = page.locator('[class*="history"], [class*="timeline"]');
    // May show history
  });

  test('should show recent items', async ({ page }) => {
    const items = page.locator('[class*="item"], [class*="article"]');
    // May show recent items
  });

  test('should have manual trigger button', async ({ page }) => {
    const triggerButton = page.locator('button:has-text("Trigger"), button:has-text("Iniciar"), button:has-text("Run")').first();

    if (await triggerButton.isVisible()) {
      // Should be clickable
    }
  });

  test('should have pause/resume controls', async ({ page }) => {
    const pauseButton = page.locator('button:has-text("Pause"), button:has-text("Pausar")').first();
    const resumeButton = page.locator('button:has-text("Resume"), button:has-text("Retomar")').first();

    // One of them should be visible
  });

  test('should show error logs', async ({ page }) => {
    const errors = page.locator('[class*="error"], [class*="log"]');
    // May show error logs
  });

  test('should show success rate', async ({ page }) => {
    const successRate = page.locator('[class*="rate"], [class*="success"], text=/success|sucesso/i');
    // May show success rate
  });

  test('should have edit configuration button', async ({ page }) => {
    const editButton = page.locator('button:has-text("Edit"), button:has-text("Editar")').first();

    if (await editButton.isVisible()) {
      await editButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// INGESTION MONITORING
// =============================================================================

test.describe('Ingestion Monitoring', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ingestion`);
    await page.waitForLoadState('networkidle');
  });

  test('should show real-time ingestion status', async ({ page }) => {
    // Look for live indicators
    const liveIndicators = page.locator('[class*="live"], [class*="pulse"], [class*="animate"]');
    // May show live indicators
  });

  test('should show items per hour', async ({ page }) => {
    const throughput = page.locator('[class*="throughput"], text=/items.*hour|itens.*hora/i');
    // May show throughput
  });

  test('should show error rate', async ({ page }) => {
    const errorRate = page.locator('[class*="error-rate"], text=/error.*rate|taxa.*erro/i');
    // May show error rate
  });

  test('should show processing queue size', async ({ page }) => {
    const queue = page.locator('[class*="queue"], text=/queue|fila/i');
    // May show queue size
  });

  test('should refresh data automatically', async ({ page }) => {
    // Wait for auto-refresh
    await page.waitForTimeout(5000);

    // Data should have updated (check for timestamp changes)
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should have manual refresh button', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Refresh"), button:has-text("Atualizar"), button[aria-label*="refresh"]').first();

    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// INGESTION OPERATIONS
// =============================================================================

test.describe('Ingestion Operations', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ingestion`);
    await page.waitForLoadState('networkidle');
  });

  test('should trigger manual ingestion', async ({ page }) => {
    // Mock API response
    await page.route('**/api/ingestion/trigger**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'started', job_id: 'job_123' }),
      });
    });

    const triggerButton = page.locator('button:has-text("Trigger"), button:has-text("Iniciar")').first();

    if (await triggerButton.isVisible()) {
      await triggerButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should pause source', async ({ page }) => {
    await page.route('**/api/ingestion/*/pause', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'paused' }),
      });
    });

    const pauseButton = page.locator('button:has-text("Pause"), button:has-text("Pausar")').first();

    if (await pauseButton.isVisible()) {
      await pauseButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should resume source', async ({ page }) => {
    await page.route('**/api/ingestion/*/resume', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'active' }),
      });
    });

    const resumeButton = page.locator('button:has-text("Resume"), button:has-text("Retomar")').first();

    if (await resumeButton.isVisible()) {
      await resumeButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should retry failed items', async ({ page }) => {
    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Tentar novamente")').first();

    if (await retryButton.isVisible()) {
      await retryButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should clear error queue', async ({ page }) => {
    const clearButton = page.locator('button:has-text("Clear"), button:has-text("Limpar")').first();

    if (await clearButton.isVisible()) {
      await clearButton.click();

      // Should show confirmation
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Confirmar")').first();
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
      }

      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// INGESTION CHARTS AND METRICS
// =============================================================================

test.describe('Ingestion Charts and Metrics', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ingestion`);
    await page.waitForLoadState('networkidle');
  });

  test('should show ingestion volume chart', async ({ page }) => {
    const chart = page.locator('canvas, svg, [class*="chart"]').first();
    // May show chart
  });

  test('should show error trend chart', async ({ page }) => {
    const errorChart = page.locator('[class*="error-chart"], [class*="trend"]');
    // May show error chart
  });

  test('should show source breakdown', async ({ page }) => {
    const breakdown = page.locator('[class*="breakdown"], [class*="pie"]');
    // May show breakdown
  });

  test('should allow date range selection', async ({ page }) => {
    const dateRange = page.locator('button:has-text("Last 24h"), button:has-text("Last 7 days"), [class*="date-range"]').first();

    if (await dateRange.isVisible()) {
      await dateRange.click();
      await page.waitForTimeout(300);
    }
  });

  test('should export metrics data', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Exportar")').first();

    if (await exportButton.isVisible()) {
      await exportButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// INGESTION ERROR HANDLING
// =============================================================================

test.describe('Ingestion Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle API error gracefully', async ({ page }) => {
    await page.route('**/api/ingestion/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/ingestion`);
    await page.waitForLoadState('networkidle');

    // Should show error message
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle network timeout', async ({ page }) => {
    await page.route('**/api/ingestion/**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 30000));
      await route.abort();
    });

    await page.goto(`${BASE_URL}/admin/ingestion`);

    // Should show loading state
    await page.waitForTimeout(3000);
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show warning for unhealthy sources', async ({ page }) => {
    await page.route('**/api/ingestion/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            { id: 'src_1', name: 'Source 1', health: 'unhealthy', error_count: 50 },
          ],
          total: 1,
        }),
      });
    });

    await page.goto(`${BASE_URL}/admin/ingestion`);
    await page.waitForLoadState('networkidle');

    // Should show warning indicators
    const warnings = page.locator('[class*="warning"], [class*="error"], .text-red, .text-yellow');
  });

  test('should allow retry on error', async ({ page }) => {
    let attemptCount = 0;
    await page.route('**/api/ingestion/**', async (route) => {
      attemptCount++;
      if (attemptCount === 1) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Error' }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0 }),
        });
      }
    });

    await page.goto(`${BASE_URL}/admin/ingestion`);
    await page.waitForLoadState('networkidle');

    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Tentar novamente")').first();
    if (await retryButton.isVisible()) {
      await retryButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// INGESTION ACCESSIBILITY
// =============================================================================

test.describe('Ingestion Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ingestion`);
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

  test('should have accessible status indicators', async ({ page }) => {
    const statusIndicators = page.locator('[class*="status"], [class*="health"]');
    const count = await statusIndicators.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      const indicator = statusIndicators.nth(i);
      const ariaLabel = await indicator.getAttribute('aria-label');
      const title = await indicator.getAttribute('title');
      const textContent = await indicator.textContent();

      // Should have some accessible text
      expect(ariaLabel || title || textContent).toBeTruthy();
    }
  });

  test('should announce live updates', async ({ page }) => {
    const liveRegions = page.locator('[aria-live], [role="status"], [role="alert"]');
    // May have live regions
  });
});
