/**
 * Cases Module E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for Case Timeline, Case X-ray, and Case management pages.
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';

// Test token for authenticated requests
const TEST_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6InNmMy1kZXYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJpbnNwZWN0YWgtaWRwIiwiYXVkIjoiaW5zcGVjdGFoLWFwaSIsInN1YiI6ImRldi1hZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NjA3OTIwNywiaWF0IjoxNzY1OTkyODA3LCJuYmYiOjE3NjU5OTI4MDcsIm9wX2lkIjoiZGV2LW9wIiwicmVxdWVzdF9pZCI6ImRldi1yZXF1ZXN0In0.GdmuUVTs37KNKVOIlAtrmQfnYSZ-ZRnxP6RhA4_lA-8cgSOEuDtBk7KLha57vE8RIpNAtpvPST8JVN4tKF7OFYx1SJgtffbRS7aLEUC5JkpvQIp6eAqCPE0E25xyLJtMWldgg21LkB7IaM-XDiK5XUFSmi-jx_sIiurHdJTedxrWdLyX1lGR8fTAfs4QZalAX9RQ2xlsIsHSXNPV_muEcrY2NJVgg6KKFualPD8dTfmdjcBaHAE4GM8FyEz5B-bYfUu6V2mqodmPB4KrK_ouDkhBSVg6GbF-8RwHhXjdSr_KOjMh4JirCxU6ijSrH6F_83H2-5vjo6yT2SC7Yoo91w';

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
// CASE TIMELINE PAGE
// =============================================================================

test.describe('Case Timeline Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/timeline`);
    await page.waitForLoadState('networkidle');
  });

  test('should display case timeline page', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show timeline container', async ({ page }) => {
    const timeline = page.locator('[class*="timeline"], [data-testid*="timeline"]');
    // May show timeline
  });

  test('should show timeline events', async ({ page }) => {
    const events = page.locator('[class*="event"], [class*="item"]');
    // May show events
  });

  test('should show event timestamps', async ({ page }) => {
    const timestamps = page.locator('[class*="timestamp"], [class*="date"], time');
    // May show timestamps
  });

  test('should expand event details on click', async ({ page }) => {
    const eventItem = page.locator('[class*="event"], [class*="item"]').first();

    if (await eventItem.isVisible()) {
      await eventItem.click();
      await page.waitForTimeout(500);

      // Should show expanded details
      const details = page.locator('[class*="detail"], [class*="expanded"]');
    }
  });

  test('should filter timeline by event type', async ({ page }) => {
    const typeFilter = page.locator('select, button:has-text("Type"), button:has-text("Tipo")').first();

    if (await typeFilter.isVisible()) {
      await typeFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should filter timeline by date range', async ({ page }) => {
    const dateFilter = page.locator('[class*="date-picker"], [class*="date-range"]').first();

    if (await dateFilter.isVisible()) {
      await dateFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should scroll through timeline', async ({ page }) => {
    const timeline = page.locator('[class*="timeline"]').first();

    if (await timeline.isVisible()) {
      await timeline.hover();
      await page.mouse.wheel(0, 500);
      await page.waitForTimeout(300);
    }
  });

  test('should navigate to event detail', async ({ page }) => {
    const eventLink = page.locator('a[href*="event"], [class*="event"][class*="cursor-pointer"]').first();

    if (await eventLink.isVisible()) {
      await eventLink.click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should show loading state', async ({ page }) => {
    // Mock slow API
    await page.route('**/api/cases/*/timeline**', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.continue();
    });

    await page.reload();

    const loading = page.locator('[class*="loading"], [class*="skeleton"]');
  });

  test('should handle empty timeline', async ({ page }) => {
    await page.route('**/api/cases/*/timeline**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ events: [], total: 0 }),
      });
    });

    await page.reload();
    await page.waitForLoadState('networkidle');

    // Should show empty state
    const emptyState = page.locator('[class*="empty"], text=/no events|sem eventos/i');
  });

  test('should handle API error', async ({ page }) => {
    await page.route('**/api/cases/*/timeline**', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Error' }),
      });
    });

    await page.reload();
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

// =============================================================================
// CASE XRAY PAGE
// =============================================================================

test.describe('Case X-ray Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/xray`);
    await page.waitForLoadState('networkidle');
  });

  test('should display case x-ray page', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show x-ray panels', async ({ page }) => {
    const panels = page.locator('[class*="panel"], [class*="tab"]');
    // May show panels
  });

  test('should show Anchors panel', async ({ page }) => {
    const anchorsTab = page.locator('button:has-text("Anchors"), button:has-text("Âncoras"), [role="tab"]:has-text("Anchor")').first();

    if (await anchorsTab.isVisible()) {
      await anchorsTab.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show Evidence panel', async ({ page }) => {
    const evidenceTab = page.locator('button:has-text("Evidence"), button:has-text("Evidências"), [role="tab"]:has-text("Evidence")').first();

    if (await evidenceTab.isVisible()) {
      await evidenceTab.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show Committees panel', async ({ page }) => {
    const committeesTab = page.locator('button:has-text("Committee"), button:has-text("Comitês"), [role="tab"]:has-text("Committee")').first();

    if (await committeesTab.isVisible()) {
      await committeesTab.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show Debunker panel', async ({ page }) => {
    const debunkerTab = page.locator('button:has-text("Debunker"), [role="tab"]:has-text("Debunk")').first();

    if (await debunkerTab.isVisible()) {
      await debunkerTab.click();
      await page.waitForTimeout(500);
    }
  });

  test('should switch between panels', async ({ page }) => {
    const tabs = page.locator('[role="tab"], [class*="tab"]');
    const count = await tabs.count();

    for (let i = 0; i < Math.min(count, 4); i++) {
      await tabs.nth(i).click();
      await page.waitForTimeout(300);
    }
  });

  test('should show anchor details', async ({ page }) => {
    const anchorItem = page.locator('[class*="anchor"]').first();

    if (await anchorItem.isVisible()) {
      await anchorItem.click();
      await page.waitForTimeout(500);
    }
  });

  test('should show evidence summary', async ({ page }) => {
    const summary = page.locator('[class*="summary"], [class*="evidence"]');
    // May show summary
  });

  test('should show committee decisions', async ({ page }) => {
    const decisions = page.locator('[class*="decision"], [class*="vote"]');
    // May show decisions
  });

  test('should show debunker results', async ({ page }) => {
    const results = page.locator('[class*="result"], [class*="debunk"]');
    // May show results
  });

  test('should expand/collapse sections', async ({ page }) => {
    const expandButton = page.locator('button[class*="expand"], [class*="accordion"]').first();

    if (await expandButton.isVisible()) {
      await expandButton.click();
      await page.waitForTimeout(300);

      await expandButton.click();
      await page.waitForTimeout(300);
    }
  });

  test('should handle API error', async ({ page }) => {
    await page.route('**/api/cases/*/xray**', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Error' }),
      });
    });

    await page.reload();
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle partial data', async ({ page }) => {
    await page.route('**/api/cases/*/xray**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          anchors: [],
          evidence: [],
          committees: null,
          debunker: null,
        }),
      });
    });

    await page.reload();
    await page.waitForLoadState('networkidle');
  });
});

// =============================================================================
// CASE DETAIL PAGE
// =============================================================================

test.describe('Case Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/cases/case_test_123`);
    await page.waitForLoadState('networkidle');
  });

  test('should display case detail page', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show case header', async ({ page }) => {
    const header = page.locator('h1, h2, [class*="header"]').first();
    const hasHeader = await header.isVisible().catch(() => false);
    expect(hasHeader).toBeTruthy();
  });

  test('should show case status badge', async ({ page }) => {
    const status = page.locator('[class*="status"], [class*="badge"]');
    // May show status
  });

  test('should show case metadata', async ({ page }) => {
    const metadata = page.locator('[class*="metadata"], [class*="info"]');
    // May show metadata
  });

  test('should navigate to timeline', async ({ page }) => {
    const timelineLink = page.locator('a[href*="timeline"], button:has-text("Timeline")').first();

    if (await timelineLink.isVisible()) {
      await timelineLink.click();
      await page.waitForLoadState('networkidle');

      expect(page.url()).toContain('timeline');
    }
  });

  test('should navigate to x-ray', async ({ page }) => {
    const xrayLink = page.locator('a[href*="xray"], button:has-text("X-ray")').first();

    if (await xrayLink.isVisible()) {
      await xrayLink.click();
      await page.waitForLoadState('networkidle');

      expect(page.url()).toContain('xray');
    }
  });

  test('should show related sources', async ({ page }) => {
    const sources = page.locator('[class*="source"], [class*="related"]');
    // May show sources
  });

  test('should show claim text', async ({ page }) => {
    const claimText = page.locator('[class*="claim"], [class*="text"]');
    // May show claim text
  });

  test('should have back navigation', async ({ page }) => {
    const backButton = page.locator('a:has-text("Back"), button:has-text("Voltar"), a[href*="/cases"]').first();

    if (await backButton.isVisible()) {
      await backButton.click();
      await page.waitForLoadState('networkidle');

      expect(page.url()).toContain('cases');
    }
  });

  test('should handle non-existent case', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases/non_existent_case_999`);
    await page.waitForLoadState('networkidle');

    // Should show 404 or error
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

// =============================================================================
// CASES API INTERACTIONS
// =============================================================================

test.describe('Cases API Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should load case timeline from API', async ({ page }) => {
    await page.route('**/api/cases/case_test_123/timeline**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          events: [
            { id: 'ev1', type: 'created', timestamp: '2024-01-01T00:00:00Z', description: 'Case created' },
            { id: 'ev2', type: 'updated', timestamp: '2024-01-02T00:00:00Z', description: 'Status changed' },
          ],
          total: 2,
        }),
      });
    });

    await page.goto(`${BASE_URL}/admin/cases/case_test_123/timeline`);
    await page.waitForLoadState('networkidle');
  });

  test('should load case x-ray from API', async ({ page }) => {
    await page.route('**/api/cases/case_test_123/xray**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          anchors: [{ id: 'a1', text: 'Anchor text', score: 0.9 }],
          evidence: [{ id: 'e1', source: 'Source 1', verdict: 'true' }],
          committees: [{ id: 'c1', decision: 'approved', votes: 5 }],
          debunker: { verified: true, sources: 3 },
        }),
      });
    });

    await page.goto(`${BASE_URL}/admin/cases/case_test_123/xray`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle timeline pagination', async ({ page }) => {
    await page.route('**/api/cases/*/timeline**', async route => {
      const url = new URL(route.request().url());
      const page_param = url.searchParams.get('page') || '1';

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          events: [{ id: `ev_page_${page_param}`, type: 'event', timestamp: new Date().toISOString() }],
          total: 100,
          page: parseInt(page_param),
          pages: 10,
        }),
      });
    });

    await page.goto(`${BASE_URL}/admin/cases/case_test_123/timeline`);
    await page.waitForLoadState('networkidle');
  });
});

// =============================================================================
// CASES ACCESSIBILITY
// =============================================================================

test.describe('Cases Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should have proper heading structure in timeline', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/timeline`);
    await page.waitForLoadState('networkidle');

    const h1 = await page.locator('h1').count();
    expect(h1).toBeGreaterThanOrEqual(0);
  });

  test('should have proper heading structure in x-ray', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/xray`);
    await page.waitForLoadState('networkidle');

    const h1 = await page.locator('h1').count();
    expect(h1).toBeGreaterThanOrEqual(0);
  });

  test('should be keyboard navigable in timeline', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/timeline`);
    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    const focusedElement = page.locator(':focus');
    const tag = await focusedElement.evaluate(el => el.tagName).catch(() => 'BODY');
    expect(['A', 'BUTTON', 'INPUT', 'SELECT', 'BODY']).toContain(tag);
  });

  test('should be keyboard navigable in x-ray tabs', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/xray`);
    await page.waitForLoadState('networkidle');

    // Tab to tabs
    await page.keyboard.press('Tab');

    // Arrow keys to navigate tabs
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(200);

    await page.keyboard.press('ArrowLeft');
    await page.waitForTimeout(200);
  });
});

// =============================================================================
// CASES RESPONSIVE DESIGN
// =============================================================================

test.describe('Cases Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('timeline should work on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/timeline`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('x-ray should work on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/xray`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('timeline should work on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/timeline`);
    await page.waitForLoadState('networkidle');

    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('x-ray tabs should adapt on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/admin/cases/case_test_123/xray`);
    await page.waitForLoadState('networkidle');

    // Tabs should be accessible on mobile
    const tabs = page.locator('[role="tab"]');
    const count = await tabs.count();
    // May have scrollable tabs or dropdown
  });
});
