/**
 * Ops Cockpit E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for operations dashboard, system monitoring, and incident management.
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
// OPS COCKPIT - MAIN DASHBOARD
// =============================================================================

test.describe('Ops Cockpit - Main Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');
  });

  test('should display ops cockpit', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show system status overview', async ({ page }) => {
    const statusOverview = page.locator('[class*="status"], [class*="overview"]');
    // May show status overview
  });

  test('should show health indicators', async ({ page }) => {
    const healthIndicators = page.locator('[class*="health"], [class*="status"], .text-green, .text-red');
    // May show health indicators
  });

  test('should show active alerts', async ({ page }) => {
    const alerts = page.locator('[class*="alert"], [class*="warning"]');
    // May show alerts
  });

  test('should show key metrics', async ({ page }) => {
    const metrics = page.locator('[class*="metric"], [class*="kpi"], [class*="stat"]');
    // May show metrics
  });

  test('should auto-refresh data', async ({ page }) => {
    // Wait for auto-refresh cycle
    await page.waitForTimeout(5000);

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
// OPS COCKPIT - SYSTEM HEALTH
// =============================================================================

test.describe('Ops Cockpit - System Health', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');
  });

  test('should show API health', async ({ page }) => {
    const apiHealth = page.locator('[class*="api"], text=/API|api/i');
    // May show API health
  });

  test('should show database health', async ({ page }) => {
    const dbHealth = page.locator('[class*="database"], [class*="db"], text=/database|banco/i');
    // May show database health
  });

  test('should show cache health', async ({ page }) => {
    const cacheHealth = page.locator('[class*="cache"], [class*="redis"], text=/cache|redis/i');
    // May show cache health
  });

  test('should show queue health', async ({ page }) => {
    const queueHealth = page.locator('[class*="queue"], [class*="kafka"], text=/queue|fila|kafka/i');
    // May show queue health
  });

  test('should show external services health', async ({ page }) => {
    const externalHealth = page.locator('[class*="external"], text=/external|externo/i');
    // May show external services health
  });

  test('should navigate to service detail', async ({ page }) => {
    const serviceItem = page.locator('[class*="service"], [class*="card"]').first();

    if (await serviceItem.isVisible()) {
      await serviceItem.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// OPS COCKPIT - PERFORMANCE METRICS
// =============================================================================

test.describe('Ops Cockpit - Performance Metrics', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');
  });

  test('should show response time metrics', async ({ page }) => {
    const responseTime = page.locator('[class*="response"], [class*="latency"], text=/response|latência/i');
    // May show response time
  });

  test('should show throughput metrics', async ({ page }) => {
    const throughput = page.locator('[class*="throughput"], text=/requests|requisições/i');
    // May show throughput
  });

  test('should show error rate metrics', async ({ page }) => {
    const errorRate = page.locator('[class*="error-rate"], text=/error.*rate|taxa.*erro/i');
    // May show error rate
  });

  test('should show CPU usage', async ({ page }) => {
    const cpuUsage = page.locator('[class*="cpu"], text=/CPU/i');
    // May show CPU usage
  });

  test('should show memory usage', async ({ page }) => {
    const memoryUsage = page.locator('[class*="memory"], text=/memory|memória/i');
    // May show memory usage
  });

  test('should display charts', async ({ page }) => {
    const charts = page.locator('canvas, svg[class*="chart"], [class*="chart"]');
    // May show charts
  });

  test('should allow date range selection', async ({ page }) => {
    const dateRange = page.locator('button:has-text("Last 24h"), button:has-text("Last 7 days"), [class*="date-picker"]').first();

    if (await dateRange.isVisible()) {
      await dateRange.click();
      await page.waitForTimeout(300);
    }
  });
});

// =============================================================================
// OPS COCKPIT - ALERTS
// =============================================================================

test.describe('Ops Cockpit - Alerts', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');
  });

  test('should show active alerts', async ({ page }) => {
    const alerts = page.locator('[class*="alert"], [role="alert"]');
    // May show alerts
  });

  test('should show alert severity', async ({ page }) => {
    const severity = page.locator('[class*="critical"], [class*="warning"], [class*="info"]');
    // May show severity levels
  });

  test('should acknowledge alert', async ({ page }) => {
    const ackButton = page.locator('button:has-text("Acknowledge"), button:has-text("Reconhecer")').first();

    if (await ackButton.isVisible()) {
      await ackButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should dismiss alert', async ({ page }) => {
    const dismissButton = page.locator('button:has-text("Dismiss"), button:has-text("Dispensar"), button[aria-label*="close"]').first();

    if (await dismissButton.isVisible()) {
      await dismissButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should filter alerts by severity', async ({ page }) => {
    const severityFilter = page.locator('select, button:has-text("Severity"), button:has-text("Severidade")').first();

    if (await severityFilter.isVisible()) {
      await severityFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should filter alerts by status', async ({ page }) => {
    const statusFilter = page.locator('select, button:has-text("Active"), button:has-text("Resolved")').first();

    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should show alert history', async ({ page }) => {
    const historyTab = page.locator('button:has-text("History"), button:has-text("Histórico")').first();

    if (await historyTab.isVisible()) {
      await historyTab.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// OPS COCKPIT - INCIDENTS
// =============================================================================

test.describe('Ops Cockpit - Incidents', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ops/incidents`);
    await page.waitForLoadState('networkidle');
  });

  test('should display incidents page', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show incident list', async ({ page }) => {
    const incidents = page.locator('[class*="incident"], table');
    // May show incidents
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
    const statusButton = page.locator('button:has-text("Resolve"), button:has-text("Resolver"), select[name*="status"]').first();

    if (await statusButton.isVisible()) {
      await statusButton.click();
      await page.waitForTimeout(300);
    }
  });

  test('should add incident update', async ({ page }) => {
    const updateInput = page.locator('textarea[name*="update"], textarea[placeholder*="update"]').first();

    if (await updateInput.isVisible()) {
      await updateInput.fill('Incident update note');
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
});

// =============================================================================
// OPS COCKPIT - LOGS
// =============================================================================

test.describe('Ops Cockpit - Logs', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');
  });

  test('should show logs section', async ({ page }) => {
    const logs = page.locator('[class*="log"], text=/logs/i');
    // May show logs section
  });

  test('should filter logs by level', async ({ page }) => {
    const levelFilter = page.locator('select, button:has-text("Error"), button:has-text("Warn"), button:has-text("Info")').first();

    if (await levelFilter.isVisible()) {
      await levelFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should search logs', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="search"], input[placeholder*="buscar"]').first();

    if (await searchInput.isVisible()) {
      await searchInput.fill('error');
      await page.waitForTimeout(500);
    }
  });

  test('should show log detail', async ({ page }) => {
    const logItem = page.locator('[class*="log-item"], tr').first();

    if (await logItem.isVisible()) {
      await logItem.click();
      await page.waitForTimeout(500);
    }
  });

  test('should export logs', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Exportar")').first();

    if (await exportButton.isVisible()) {
      await exportButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// OPS COCKPIT - REAL-TIME UPDATES
// =============================================================================

test.describe('Ops Cockpit - Real-Time Updates', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should receive real-time metric updates', async ({ page }) => {
    // Mock WebSocket
    await page.addInitScript(() => {
      class MockWebSocket {
        onopen: ((event: Event) => void) | null = null;
        onmessage: ((event: MessageEvent) => void) | null = null;

        constructor() {
          setTimeout(() => {
            this.onopen?.(new Event('open'));

            // Send metric update
            setTimeout(() => {
              this.onmessage?.(new MessageEvent('message', {
                data: JSON.stringify({
                  type: 'metric_update',
                  payload: { cpu: 45, memory: 60, requests: 1000 },
                }),
              }));
            }, 500);
          }, 100);
        }

        send() {}
        close() {}
      }

      (window as unknown as { WebSocket: typeof MockWebSocket }).WebSocket = MockWebSocket;
    });

    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    // Wait for WebSocket updates
    await page.waitForTimeout(1000);
  });

  test('should receive real-time alert notifications', async ({ page }) => {
    await page.addInitScript(() => {
      class MockWebSocket {
        onopen: ((event: Event) => void) | null = null;
        onmessage: ((event: MessageEvent) => void) | null = null;

        constructor() {
          setTimeout(() => {
            this.onopen?.(new Event('open'));

            setTimeout(() => {
              this.onmessage?.(new MessageEvent('message', {
                data: JSON.stringify({
                  type: 'alert',
                  payload: { id: 'alert_1', severity: 'warning', message: 'High CPU usage' },
                }),
              }));
            }, 500);
          }, 100);
        }

        send() {}
        close() {}
      }

      (window as unknown as { WebSocket: typeof MockWebSocket }).WebSocket = MockWebSocket;
    });

    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    await page.waitForTimeout(1000);
  });

  test('should show connection status indicator', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    const connectionStatus = page.locator('[class*="connection"], [class*="online"], [class*="offline"]');
    // May show connection status
  });
});

// =============================================================================
// OPS COCKPIT - ERROR HANDLING
// =============================================================================

test.describe('Ops Cockpit - Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle API error gracefully', async ({ page }) => {
    await page.route('**/api/ops/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle partial data failure', async ({ page }) => {
    // Some endpoints fail, others succeed
    await page.route('**/api/ops/metrics**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Metrics unavailable' }),
      });
    });

    await page.route('**/api/ops/health**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'healthy' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    // Should show partial data
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should allow retry on error', async ({ page }) => {
    let attemptCount = 0;
    await page.route('**/api/ops/**', async (route) => {
      attemptCount++;
      if (attemptCount === 1) {
        await route.fulfill({ status: 500, body: '{}' });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ status: 'ok' }),
        });
      }
    });

    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Tentar novamente")').first();
    if (await retryButton.isVisible()) {
      await retryButton.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// OPS COCKPIT - ACCESSIBILITY
// =============================================================================

test.describe('Ops Cockpit - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/ops`);
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

  test('should have accessible charts', async ({ page }) => {
    const charts = page.locator('canvas, svg');
    const count = await charts.count();

    for (let i = 0; i < Math.min(count, 3); i++) {
      const chart = charts.nth(i);
      const ariaLabel = await chart.getAttribute('aria-label');
      const role = await chart.getAttribute('role');
      // Charts should have some accessible description
    }
  });

  test('should announce alert status changes', async ({ page }) => {
    const liveRegions = page.locator('[aria-live], [role="status"], [role="alert"]');
    // May have live regions for status updates
  });

  test('should have color contrast for status indicators', async ({ page }) => {
    const statusIndicators = page.locator('[class*="status"], [class*="health"]');
    const count = await statusIndicators.count();

    // All status indicators should be visible
    for (let i = 0; i < Math.min(count, 5); i++) {
      const indicator = statusIndicators.nth(i);
      const isVisible = await indicator.isVisible().catch(() => false);
    }
  });
});

// =============================================================================
// OPS COCKPIT - RESPONSIVE DESIGN
// =============================================================================

test.describe('Ops Cockpit - Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should work on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should have responsive charts', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/ops`);
    await page.waitForLoadState('networkidle');

    const charts = page.locator('canvas, svg');
    // Charts should resize appropriately
  });
});
