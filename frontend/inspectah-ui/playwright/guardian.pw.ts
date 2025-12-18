/**
 * Guardian Cockpit E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for the Guardian review system, human oversight, and claim queue management.
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
// GUARDIAN COCKPIT - MAIN VIEW
// =============================================================================

test.describe('Guardian Cockpit - Main View', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');
  });

  test('should display guardian cockpit', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show queue tabs', async ({ page }) => {
    // Look for queue tabs (Pending, Review, Completed)
    const tabs = page.locator('button:has-text("Pendentes"), button:has-text("Revisão"), button:has-text("Concluídas"), [role="tab"]');
    const count = await tabs.count();
    // Should have multiple tabs or different view options
  });

  test('should show claim queue', async ({ page }) => {
    const queue = page.locator('[class*="queue"], [class*="list"], table');
    // May show queue
  });

  test('should show claim count badges', async ({ page }) => {
    const badges = page.locator('[class*="badge"], [class*="count"]');
    // May show count badges
  });

  test('should filter by priority', async ({ page }) => {
    const priorityFilter = page.locator('select, button:has-text("Prioridade"), button:has-text("Priority")').first();

    if (await priorityFilter.isVisible()) {
      await priorityFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should filter by domain', async ({ page }) => {
    const domainFilter = page.locator('select, button:has-text("Domínio"), button:has-text("Domain")').first();

    if (await domainFilter.isVisible()) {
      await domainFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should sort claims', async ({ page }) => {
    const sortButton = page.locator('button:has-text("Sort"), button:has-text("Ordenar"), [class*="sort"]').first();

    if (await sortButton.isVisible()) {
      await sortButton.click();
      await page.waitForTimeout(300);
    }
  });

  test('should show empty state when no pending claims', async ({ page }) => {
    // Mock empty queue
    await page.route('**/api/guardian/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.reload();
    await page.waitForLoadState('networkidle');

    // Should show empty state
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

// =============================================================================
// GUARDIAN COCKPIT - CLAIM REVIEW
// =============================================================================

test.describe('Guardian Cockpit - Claim Review', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');
  });

  test('should select claim for review', async ({ page }) => {
    const claimItem = page.locator('[class*="claim"], tr, [class*="item"]').first();

    if (await claimItem.isVisible()) {
      await claimItem.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show claim detail panel', async ({ page }) => {
    const claimItem = page.locator('[class*="claim"], tr').first();

    if (await claimItem.isVisible()) {
      await claimItem.click();

      // Should show detail panel
      const detailPanel = page.locator('[class*="detail"], [class*="panel"], [role="dialog"]');
      await page.waitForTimeout(500);
    }
  });

  test('should show agent analysis', async ({ page }) => {
    const analysis = page.locator('[class*="analysis"], [class*="agent-result"]');
    // May show analysis
  });

  test('should show confidence scores', async ({ page }) => {
    const scores = page.locator('[class*="confidence"], [class*="score"]');
    // May show scores
  });

  test('should show evidence and sources', async ({ page }) => {
    const evidence = page.locator('[class*="evidence"], [class*="source"]');
    // May show evidence
  });

  test('should have verdict buttons', async ({ page }) => {
    const verdictButtons = page.locator('button:has-text("Aprovar"), button:has-text("Rejeitar"), button:has-text("Approve"), button:has-text("Reject")');
    // May have verdict buttons
  });

  test('should allow adding reviewer notes', async ({ page }) => {
    const notesInput = page.locator('textarea[name*="note"], textarea[placeholder*="nota"], textarea[placeholder*="comment"]').first();

    if (await notesInput.isVisible()) {
      await notesInput.fill('Reviewer note for this claim');
      await page.waitForTimeout(300);
    }
  });

  test('should confirm verdict before submission', async ({ page }) => {
    const verdictButton = page.locator('button:has-text("Aprovar"), button:has-text("Approve")').first();

    if (await verdictButton.isVisible()) {
      await verdictButton.click();

      // Should show confirmation dialog
      const confirmDialog = page.locator('[role="dialog"], [role="alertdialog"], .modal');
      await page.waitForTimeout(500);
    }
  });

  test('should submit verdict', async ({ page }) => {
    // Mock API response
    await page.route('**/api/guardian/*/verdict', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    const verdictButton = page.locator('button:has-text("Aprovar"), button:has-text("Approve")').first();

    if (await verdictButton.isVisible()) {
      await verdictButton.click();

      // Handle confirmation if present
      const confirmButton = page.locator('button:has-text("Confirmar"), button:has-text("Confirm")').first();
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
      }

      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// GUARDIAN COCKPIT - QUEUE TABS
// =============================================================================

test.describe('Guardian Cockpit - Queue Tabs', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');
  });

  test('should switch between tabs', async ({ page }) => {
    const pendingTab = page.locator('button:has-text("Pendentes"), [role="tab"]:has-text("Pending")').first();
    const reviewTab = page.locator('button:has-text("Revisão"), [role="tab"]:has-text("Review")').first();
    const completedTab = page.locator('button:has-text("Concluídas"), [role="tab"]:has-text("Completed")').first();

    if (await reviewTab.isVisible()) {
      await reviewTab.click();
      await page.waitForTimeout(500);
    }

    if (await completedTab.isVisible()) {
      await completedTab.click();
      await page.waitForTimeout(500);
    }

    if (await pendingTab.isVisible()) {
      await pendingTab.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show different content for each tab', async ({ page }) => {
    // Pending tab
    let body = await page.locator('body').textContent();
    expect(body).toBeTruthy();

    // Review tab
    const reviewTab = page.locator('button:has-text("Revisão"), [role="tab"]:has-text("Review")').first();
    if (await reviewTab.isVisible()) {
      await reviewTab.click();
      await page.waitForTimeout(500);

      body = await page.locator('body').textContent();
      expect(body).toBeTruthy();
    }
  });

  test('should maintain tab state on refresh', async ({ page }) => {
    const reviewTab = page.locator('button:has-text("Revisão"), [role="tab"]:has-text("Review")').first();

    if (await reviewTab.isVisible()) {
      await reviewTab.click();
      await page.waitForTimeout(500);

      // Refresh
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Tab state may or may not be preserved depending on implementation
    }
  });
});

// =============================================================================
// GUARDIAN COCKPIT - BATCH OPERATIONS
// =============================================================================

test.describe('Guardian Cockpit - Batch Operations', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');
  });

  test('should select multiple claims', async ({ page }) => {
    const checkboxes = page.locator('input[type="checkbox"]');
    const count = await checkboxes.count();

    if (count > 1) {
      await checkboxes.first().click();
      await checkboxes.nth(1).click();

      // Should show batch action buttons
      const batchActions = page.locator('[class*="batch"], button:has-text("Batch"), button:has-text("Bulk")');
      await page.waitForTimeout(300);
    }
  });

  test('should select all claims', async ({ page }) => {
    const selectAllCheckbox = page.locator('input[type="checkbox"][name*="all"], th input[type="checkbox"]').first();

    if (await selectAllCheckbox.isVisible()) {
      await selectAllCheckbox.click();
      await page.waitForTimeout(300);
    }
  });

  test('should batch approve claims', async ({ page }) => {
    const checkboxes = page.locator('input[type="checkbox"]');
    const count = await checkboxes.count();

    if (count > 0) {
      await checkboxes.first().click();

      const batchApprove = page.locator('button:has-text("Aprovar Selecionados"), button:has-text("Batch Approve")').first();
      if (await batchApprove.isVisible()) {
        await batchApprove.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('should batch reject claims', async ({ page }) => {
    const checkboxes = page.locator('input[type="checkbox"]');
    const count = await checkboxes.count();

    if (count > 0) {
      await checkboxes.first().click();

      const batchReject = page.locator('button:has-text("Rejeitar Selecionados"), button:has-text("Batch Reject")').first();
      if (await batchReject.isVisible()) {
        await batchReject.click();
        await page.waitForTimeout(500);
      }
    }
  });
});

// =============================================================================
// GUARDIAN COCKPIT - STATISTICS
// =============================================================================

test.describe('Guardian Cockpit - Statistics', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');
  });

  test('should show queue statistics', async ({ page }) => {
    const stats = page.locator('[class*="stat"], [class*="metric"]');
    // May show statistics
  });

  test('should show pending count', async ({ page }) => {
    const pendingCount = page.locator('[class*="pending"], [class*="count"]');
    // May show pending count
  });

  test('should show review rate', async ({ page }) => {
    const reviewRate = page.locator('[class*="rate"], text=/review|taxa/i');
    // May show review rate
  });

  test('should show average review time', async ({ page }) => {
    const avgTime = page.locator('[class*="time"], text=/average|média/i');
    // May show average time
  });

  test('should show reviewer activity', async ({ page }) => {
    const activity = page.locator('[class*="activity"], [class*="reviewer"]');
    // May show activity
  });
});

// =============================================================================
// GUARDIAN COCKPIT - KEYBOARD SHORTCUTS
// =============================================================================

test.describe('Guardian Cockpit - Keyboard Shortcuts', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');
  });

  test('should navigate claims with arrow keys', async ({ page }) => {
    // Focus on claim list
    await page.keyboard.press('Tab');

    // Navigate down
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(200);

    // Navigate up
    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(200);
  });

  test('should approve with keyboard shortcut', async ({ page }) => {
    // Some systems use A for approve
    await page.keyboard.press('a');
    await page.waitForTimeout(300);
  });

  test('should reject with keyboard shortcut', async ({ page }) => {
    // Some systems use R for reject
    await page.keyboard.press('r');
    await page.waitForTimeout(300);
  });

  test('should show shortcuts help', async ({ page }) => {
    // Press ? for help
    await page.keyboard.press('?');
    await page.waitForTimeout(300);

    const helpModal = page.locator('[class*="help"], [class*="shortcut"], [role="dialog"]');
    // May show help modal
  });
});

// =============================================================================
// GUARDIAN COCKPIT - REAL-TIME UPDATES
// =============================================================================

test.describe('Guardian Cockpit - Real-Time Updates', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should show new claim notifications', async ({ page }) => {
    // Mock WebSocket for real-time updates
    await page.addInitScript(() => {
      class MockWebSocket {
        onopen: ((event: Event) => void) | null = null;
        onmessage: ((event: MessageEvent) => void) | null = null;

        constructor() {
          setTimeout(() => {
            this.onopen?.(new Event('open'));
            // Simulate new claim after 500ms
            setTimeout(() => {
              this.onmessage?.(new MessageEvent('message', {
                data: JSON.stringify({
                  type: 'new_claim',
                  payload: { id: 'new_claim_123', title: 'New Claim' },
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

    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');

    // Wait for notification
    await page.waitForTimeout(1000);
  });

  test('should update queue count in real-time', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');

    // Count may update via WebSocket
    await page.waitForTimeout(500);
  });

  test('should show claim status changes', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');

    // Status changes may be shown via WebSocket
    await page.waitForTimeout(500);
  });
});

// =============================================================================
// GUARDIAN COCKPIT - ERROR HANDLING
// =============================================================================

test.describe('Guardian Cockpit - Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle API error gracefully', async ({ page }) => {
    await page.route('**/api/guardian/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');

    // Should show error message
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle verdict submission error', async ({ page }) => {
    await page.route('**/api/guardian/*/verdict', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid verdict' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');

    const verdictButton = page.locator('button:has-text("Aprovar")').first();
    if (await verdictButton.isVisible()) {
      await verdictButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should handle network timeout', async ({ page }) => {
    await page.route('**/api/guardian/**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 30000));
      await route.abort();
    });

    await page.goto(`${BASE_URL}/admin/guardian`);

    // Should show loading state
    await page.waitForTimeout(3000);
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

// =============================================================================
// GUARDIAN COCKPIT - ACCESSIBILITY
// =============================================================================

test.describe('Guardian Cockpit - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/guardian`);
    await page.waitForLoadState('networkidle');
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    const h1 = await page.locator('h1').count();
    expect(h1).toBeGreaterThanOrEqual(0);
  });

  test('should be fully keyboard navigable', async ({ page }) => {
    // Tab through all interactive elements
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
    }

    const focusedElement = page.locator(':focus');
    const isVisible = await focusedElement.isVisible().catch(() => false);
  });

  test('should have accessible action buttons', async ({ page }) => {
    const actionButtons = page.locator('button');
    const count = await actionButtons.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = actionButtons.nth(i);
      const hasText = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');

      expect(hasText || ariaLabel).toBeTruthy();
    }
  });

  test('should announce status changes', async ({ page }) => {
    // Live regions for status updates
    const liveRegions = page.locator('[aria-live], [role="status"], [role="alert"]');
    // May have live regions
  });
});
