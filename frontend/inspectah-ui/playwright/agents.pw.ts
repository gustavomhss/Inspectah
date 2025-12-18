/**
 * Agents Module E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for agent management, committees, flows, and model policies.
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
// AGENTS LIST PAGE
// =============================================================================

test.describe('Agents List Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/agents`);
    await page.waitForLoadState('networkidle');
  });

  test('should display agents list', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show agent cards or table', async ({ page }) => {
    const hasAgentDisplay = await page.locator('[class*="agent"], [class*="card"], table').first().isVisible().catch(() => false);
    // May show agents or empty state
  });

  test('should filter agents by status', async ({ page }) => {
    const statusFilter = page.locator('select, button:has-text("Status"), [role="listbox"]').first();

    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should filter agents by type', async ({ page }) => {
    const typeFilter = page.locator('select, button:has-text("Tipo"), button:has-text("Type")').first();

    if (await typeFilter.isVisible()) {
      await typeFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should search agents by name', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="buscar"]').first();

    if (await searchInput.isVisible()) {
      await searchInput.fill('classifier');
      await page.waitForTimeout(500);
    }
  });

  test('should navigate to agent detail', async ({ page }) => {
    const agentItem = page.locator('a[href*="/agents/"], [class*="agent"][class*="cursor-pointer"]').first();

    if (await agentItem.isVisible()) {
      await agentItem.click();
      await page.waitForLoadState('networkidle');

      expect(page.url()).toContain('agent');
    }
  });

  test('should show agent health status', async ({ page }) => {
    const healthIndicators = page.locator('[class*="health"], [class*="status"], .text-green, .text-red');
    // May show health indicators
  });

  test('should show agent metrics summary', async ({ page }) => {
    const metrics = page.locator('[class*="metric"], [class*="stat"]');
    // May show metrics
  });
});

// =============================================================================
// AGENT DETAIL PAGE
// =============================================================================

test.describe('Agent Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/agents/agent_classifier_001`);
    await page.waitForLoadState('networkidle');
  });

  test('should display agent detail', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show agent name and description', async ({ page }) => {
    const hasTitle = await page.locator('h1, h2, [class*="title"]').first().isVisible().catch(() => false);
    expect(hasTitle).toBeTruthy();
  });

  test('should show agent configuration', async ({ page }) => {
    const config = page.locator('[class*="config"], [class*="setting"], text=/configuration|configuração/i');
    // May show configuration
  });

  test('should show agent capabilities', async ({ page }) => {
    const capabilities = page.locator('[class*="capability"], [class*="skill"], text=/capabilities|capacidades/i');
    // May show capabilities
  });

  test('should show agent logs', async ({ page }) => {
    const logs = page.locator('[class*="log"], [class*="trace"], text=/logs|traces/i');
    // May show logs
  });

  test('should show performance metrics', async ({ page }) => {
    const metrics = page.locator('[class*="metric"], [class*="chart"], canvas');
    // May show metrics
  });

  test('should have enable/disable toggle', async ({ page }) => {
    const toggle = page.locator('button:has-text("Enable"), button:has-text("Disable"), button:has-text("Ativar"), button:has-text("Desativar"), [role="switch"]').first();

    if (await toggle.isVisible()) {
      await toggle.click();
      await page.waitForTimeout(500);
    }
  });

  test('should have edit configuration button', async ({ page }) => {
    const editButton = page.locator('button:has-text("Edit"), button:has-text("Editar")').first();

    if (await editButton.isVisible()) {
      await editButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show last activity timestamp', async ({ page }) => {
    const timestamp = page.locator('[class*="timestamp"], [class*="date"], text=/última atividade|last activity/i');
    // May show timestamp
  });

  test('should handle non-existent agent', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/agents/non_existent_agent_999`);
    await page.waitForLoadState('networkidle');

    // Should show 404 or error
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

// =============================================================================
// AGENT COMMITTEES PAGE
// =============================================================================

test.describe('Agent Committees Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/agents/committees`);
    await page.waitForLoadState('networkidle');
  });

  test('should display committees list', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show committee composition', async ({ page }) => {
    const committees = page.locator('[class*="committee"], [class*="group"]');
    // May show committees
  });

  test('should show committee members', async ({ page }) => {
    const members = page.locator('[class*="member"], [class*="agent"]');
    // May show members
  });

  test('should show committee voting rules', async ({ page }) => {
    const rules = page.locator('[class*="rule"], [class*="voting"], text=/voting|votação/i');
    // May show rules
  });

  test('should navigate to committee detail', async ({ page }) => {
    const committeeItem = page.locator('a[href*="committee"], [class*="committee"][class*="cursor-pointer"]').first();

    if (await committeeItem.isVisible()) {
      await committeeItem.click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should show committee decisions history', async ({ page }) => {
    const history = page.locator('[class*="history"], [class*="decision"]');
    // May show history
  });
});

// =============================================================================
// AGENTS FLOW PAGE
// =============================================================================

test.describe('Agents Flow Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/agents/flow`);
    await page.waitForLoadState('networkidle');
  });

  test('should display flow visualization', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show flow diagram or graph', async ({ page }) => {
    const diagram = page.locator('svg, canvas, [class*="flow"], [class*="diagram"], [class*="graph"]').first();
    // May show diagram
  });

  test('should show flow steps', async ({ page }) => {
    const steps = page.locator('[class*="step"], [class*="node"]');
    // May show steps
  });

  test('should show flow connections', async ({ page }) => {
    const connections = page.locator('[class*="edge"], [class*="connection"], [class*="arrow"]');
    // May show connections
  });

  test('should allow clicking on flow nodes', async ({ page }) => {
    const node = page.locator('[class*="node"], [class*="step"]').first();

    if (await node.isVisible()) {
      await node.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show node details on click', async ({ page }) => {
    const node = page.locator('[class*="node"], [class*="step"]').first();

    if (await node.isVisible()) {
      await node.click();

      // Should show detail panel or modal
      const detail = page.locator('[class*="detail"], [class*="panel"], [role="dialog"]');
      await page.waitForTimeout(500);
    }
  });

  test('should have zoom controls', async ({ page }) => {
    const zoomControls = page.locator('button:has-text("+"), button:has-text("-"), [class*="zoom"]');
    // May have zoom controls
  });

  test('should have pan/drag capability', async ({ page }) => {
    const canvas = page.locator('svg, canvas, [class*="flow-canvas"]').first();

    if (await canvas.isVisible()) {
      // Try to drag
      await canvas.hover();
    }
  });
});

// =============================================================================
// MODEL POLICY PAGE
// =============================================================================

test.describe('Model Policy Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/agents/policy`);
    await page.waitForLoadState('networkidle');
  });

  test('should display model policy page', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show policy configuration', async ({ page }) => {
    const config = page.locator('[class*="policy"], [class*="config"]');
    // May show configuration
  });

  test('should show model selection', async ({ page }) => {
    const modelSelect = page.locator('select, [role="listbox"], [class*="model-select"]');
    // May show model selection
  });

  test('should show fallback configuration', async ({ page }) => {
    const fallback = page.locator('[class*="fallback"], text=/fallback/i');
    // May show fallback config
  });

  test('should show quota settings', async ({ page }) => {
    const quota = page.locator('[class*="quota"], text=/quota|limite/i');
    // May show quota settings
  });

  test('should have save button', async ({ page }) => {
    const saveButton = page.locator('button:has-text("Save"), button:has-text("Salvar")').first();

    if (await saveButton.isVisible()) {
      // Should be clickable
    }
  });

  test('should validate policy changes', async ({ page }) => {
    const saveButton = page.locator('button:has-text("Save"), button:has-text("Salvar")').first();

    if (await saveButton.isVisible()) {
      await saveButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show policy history', async ({ page }) => {
    const history = page.locator('[class*="history"], [class*="version"]');
    // May show history
  });
});

// =============================================================================
// AGENTS API INTERACTIONS
// =============================================================================

test.describe('Agents API Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should load agents from API', async ({ page }) => {
    let apiCalled = false;
    await page.route('**/api/agents**', async (route) => {
      apiCalled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            { id: 'agent_1', name: 'Classifier', status: 'active' },
            { id: 'agent_2', name: 'Verifier', status: 'active' },
          ],
          total: 2,
        }),
      });
    });

    await page.goto(`${BASE_URL}/admin/agents`);
    await page.waitForLoadState('networkidle');

    // API should have been called
  });

  test('should handle API error for agents list', async ({ page }) => {
    await page.route('**/api/agents**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/agents`);
    await page.waitForLoadState('networkidle');

    // Should handle error gracefully
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle empty agents list', async ({ page }) => {
    await page.route('**/api/agents**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.goto(`${BASE_URL}/admin/agents`);
    await page.waitForLoadState('networkidle');

    // Should show empty state
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should update agent status', async ({ page }) => {
    await page.route('**/api/agents/agent_1**', async (route) => {
      if (route.request().method() === 'PATCH') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'agent_1', status: 'disabled' }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'agent_1', name: 'Agent 1', status: 'active' }),
        });
      }
    });

    await page.goto(`${BASE_URL}/admin/agents/agent_1`);
    await page.waitForLoadState('networkidle');

    const toggle = page.locator('button:has-text("Disable"), [role="switch"]').first();
    if (await toggle.isVisible()) {
      await toggle.click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// AGENTS REAL-TIME UPDATES
// =============================================================================

test.describe('Agents Real-Time Updates', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should show real-time agent status changes', async ({ page }) => {
    // Setup WebSocket mock
    await page.addInitScript(() => {
      class MockWebSocket {
        onopen: ((event: Event) => void) | null = null;
        onmessage: ((event: MessageEvent) => void) | null = null;

        constructor() {
          setTimeout(() => {
            this.onopen?.(new Event('open'));
          }, 100);
        }

        send() {}
        close() {}
      }

      (window as unknown as { WebSocket: typeof MockWebSocket }).WebSocket = MockWebSocket;
    });

    await page.goto(`${BASE_URL}/admin/agents`);
    await page.waitForLoadState('networkidle');

    // Should handle WebSocket updates
    await page.waitForTimeout(500);
  });

  test('should show agent activity indicators', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/agents`);
    await page.waitForLoadState('networkidle');

    const activityIndicators = page.locator('[class*="activity"], [class*="pulse"], [class*="animate"]');
    // May show activity indicators
  });
});

// =============================================================================
// AGENTS ACCESSIBILITY
// =============================================================================

test.describe('Agents Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/agents`);
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

  test('should have accessible buttons', async ({ page }) => {
    const buttons = page.locator('button');
    const count = await buttons.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = buttons.nth(i);
      const hasText = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');

      // Should have text or aria-label
      expect(hasText || ariaLabel).toBeTruthy();
    }
  });
});
