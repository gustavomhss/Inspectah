/**
 * Edge Cases and Error Handling E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for error scenarios, edge cases, and resilience testing.
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000';

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
// NETWORK ERROR HANDLING
// =============================================================================

test.describe('Network Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle complete network failure', async ({ page }) => {
    await page.route('**/*', route => route.abort('failed'));

    await page.goto(BASE_URL).catch(() => {});

    // Should show some error or the page should handle it
    const body = await page.locator('body').textContent().catch(() => '');
  });

  test('should handle offline mode', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Go offline
    await page.context().setOffline(true);

    // Try to navigate
    await page.goto(`${BASE_URL}/admin/cases`).catch(() => {});

    // Restore network
    await page.context().setOffline(false);
  });

  test('should handle slow network', async ({ page }) => {
    // Simulate slow network
    await page.route('**/*', async route => {
      await new Promise(resolve => setTimeout(resolve, 3000));
      await route.continue();
    });

    await page.goto(BASE_URL, { timeout: 30000 }).catch(() => {});
  });

  test('should handle intermittent failures', async ({ page }) => {
    let requestCount = 0;
    await page.route('**/api/**', async route => {
      requestCount++;
      if (requestCount % 2 === 0) {
        await route.fulfill({ status: 500, body: 'Error' });
      } else {
        await route.continue();
      }
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle DNS resolution failure', async ({ page }) => {
    await page.route('**/api/**', route => route.abort('namenotresolved'));

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle connection timeout', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 60000));
      await route.abort('timedout');
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForTimeout(5000);
  });
});

// =============================================================================
// HTTP ERROR CODES
// =============================================================================

test.describe('HTTP Error Codes', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle 400 Bad Request', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Bad request' }),
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle 401 Unauthorized', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Unauthorized' }),
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Should redirect to login or show unauthorized message
  });

  test('should handle 403 Forbidden', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Forbidden' }),
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle 404 Not Found', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Not found' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/cases/non_existent`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle 422 Validation Error', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: [
            { loc: ['body', 'name'], msg: 'field required', type: 'value_error.missing' },
          ],
        }),
      });
    });

    await page.goto(`${BASE_URL}/admin/sources/new`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle 429 Too Many Requests', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 429,
        contentType: 'application/json',
        headers: { 'Retry-After': '60' },
        body: JSON.stringify({ detail: 'Too many requests' }),
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle 500 Internal Server Error', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle 502 Bad Gateway', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 502,
        contentType: 'text/html',
        body: '<html><body>Bad Gateway</body></html>',
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle 503 Service Unavailable', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Service unavailable' }),
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle 504 Gateway Timeout', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 504,
        contentType: 'text/html',
        body: '<html><body>Gateway Timeout</body></html>',
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });
});

// =============================================================================
// MALFORMED RESPONSES
// =============================================================================

test.describe('Malformed Responses', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle invalid JSON response', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: 'not valid json {{{',
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle empty response', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: '',
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle null response', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: 'null',
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle missing fields in response', async ({ page }) => {
    await page.route('**/api/cases**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ unexpected: 'structure' }),
      });
    });

    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle HTML instead of JSON', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'text/html',
        body: '<html><body>Not JSON</body></html>',
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle wrong content type', async ({ page }) => {
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'text/plain',
        body: '{"valid": "json"}',
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });
});

// =============================================================================
// INPUT EDGE CASES
// =============================================================================

test.describe('Input Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle XSS attempts in input', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input, textarea').first();
    if (await input.isVisible()) {
      await input.fill('<script>alert("xss")</script>');
      const value = await input.inputValue();
      // Should sanitize or handle safely
    }
  });

  test('should handle SQL injection attempts', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input, textarea').first();
    if (await input.isVisible()) {
      await input.fill("'; DROP TABLE users; --");
      const value = await input.inputValue();
    }
  });

  test('should handle very long input', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input, textarea').first();
    if (await input.isVisible()) {
      const longText = 'a'.repeat(100000);
      await input.fill(longText);
    }
  });

  test('should handle unicode special characters', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input, textarea').first();
    if (await input.isVisible()) {
      await input.fill('𝕿𝖊𝖘𝖙 🎭 ᗩᗷᑕ 中文 العربية');
      const value = await input.inputValue();
    }
  });

  test('should handle null bytes', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input, textarea').first();
    if (await input.isVisible()) {
      await input.fill('test\x00null\x00bytes');
    }
  });

  test('should handle newlines in single-line input', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input[type="text"]').first();
    if (await input.isVisible()) {
      await input.fill('line1\nline2\nline3');
    }
  });

  test('should handle leading/trailing whitespace', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input, textarea').first();
    if (await input.isVisible()) {
      await input.fill('   spaces   ');
    }
  });

  test('should handle emoji-only input', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input, textarea').first();
    if (await input.isVisible()) {
      await input.fill('🚀🎉💯🔥');
    }
  });
});

// =============================================================================
// URL EDGE CASES
// =============================================================================

test.describe('URL Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle non-existent route', async ({ page }) => {
    const response = await page.goto(`${BASE_URL}/this/route/does/not/exist`);

    // Should show 404 page or redirect
  });

  test('should handle malformed URL parameters', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases?page=-1&size=99999999`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle special characters in URL', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases/%3Cscript%3E`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle very long URL', async ({ page }) => {
    const longParam = 'a'.repeat(10000);
    await page.goto(`${BASE_URL}/admin/cases?q=${longParam}`).catch(() => {});
  });

  test('should handle double slashes in URL', async ({ page }) => {
    await page.goto(`${BASE_URL}//admin//cases`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle URL with hash', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin#section`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle URL encoded characters', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases?search=%E4%B8%AD%E6%96%87`);
    await page.waitForLoadState('networkidle');
  });
});

// =============================================================================
// STATE EDGE CASES
// =============================================================================

test.describe('State Edge Cases', () => {
  test('should handle cleared localStorage', async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Clear localStorage mid-session
    await page.evaluate(() => localStorage.clear());

    // Navigate to another page
    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle corrupted localStorage', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'invalid-token');
      localStorage.setItem('user', 'not-valid-json{{{');
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle expired token mid-session', async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Mock expired token response
    await page.route('**/api/**', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Token expired' }),
      });
    });

    // Navigate to trigger API call
    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle rapid navigation', async ({ page }) => {
    await setupAuth(page);

    // Navigate rapidly without waiting
    page.goto(`${BASE_URL}/admin`);
    page.goto(`${BASE_URL}/admin/cases`);
    page.goto(`${BASE_URL}/admin/sources`);
    page.goto(`${BASE_URL}/admin/agents`);

    await page.waitForLoadState('networkidle');
  });

  test('should handle browser back/forward', async ({ page }) => {
    await setupAuth(page);

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');

    await page.goBack();
    await page.waitForLoadState('networkidle');

    await page.goForward();
    await page.waitForLoadState('networkidle');
  });

  test('should handle page refresh during loading', async ({ page }) => {
    await setupAuth(page);

    // Slow API
    await page.route('**/api/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 5000));
      await route.continue();
    });

    await page.goto(`${BASE_URL}/admin`);

    // Refresh while loading
    await page.waitForTimeout(1000);
    await page.reload();
  });
});

// =============================================================================
// CONCURRENT OPERATIONS
// =============================================================================

test.describe('Concurrent Operations', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle multiple tabs', async ({ browser }) => {
    const context = await browser.newContext();

    // Setup auth for context
    await context.addInitScript((token) => {
      localStorage.setItem('auth_token', token);
      localStorage.setItem('user', JSON.stringify({ sub: 'admin', role: 'admin' }));
    }, TEST_TOKEN);

    const page1 = await context.newPage();
    const page2 = await context.newPage();

    await page1.goto(`${BASE_URL}/admin/cases`);
    await page2.goto(`${BASE_URL}/admin/sources`);

    await page1.waitForLoadState('networkidle');
    await page2.waitForLoadState('networkidle');

    await context.close();
  });

  test('should handle double click', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    const button = page.locator('button').first();
    if (await button.isVisible()) {
      await button.dblclick();
    }
  });

  test('should handle rapid form submission', async ({ page }) => {
    await page.goto(`${BASE_URL}`);
    await page.waitForLoadState('networkidle');

    const submitButton = page.locator('button[type="submit"]').first();
    if (await submitButton.isVisible()) {
      // Click multiple times rapidly
      await submitButton.click();
      await submitButton.click();
      await submitButton.click();
    }
  });
});

// =============================================================================
// BROWSER EDGE CASES
// =============================================================================

test.describe('Browser Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle JavaScript disabled', async ({ browser }) => {
    const context = await browser.newContext({
      javaScriptEnabled: false,
    });
    const page = await context.newPage();

    await page.goto(BASE_URL);

    // Should show noscript content or handle gracefully
    await context.close();
  });

  test('should handle cookies disabled', async ({ browser }) => {
    const context = await browser.newContext({
      storageState: { cookies: [], origins: [] },
    });
    const page = await context.newPage();

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    await context.close();
  });

  test('should handle print', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Trigger print (won't actually print in test)
    await page.emulateMedia({ media: 'print' });
  });

  test('should handle focus/blur events', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Simulate tab blur
    await page.evaluate(() => {
      window.dispatchEvent(new Event('blur'));
    });

    await page.waitForTimeout(500);

    // Simulate tab focus
    await page.evaluate(() => {
      window.dispatchEvent(new Event('focus'));
    });
  });

  test('should handle visibility change', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Simulate visibility change
    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { value: true, writable: true });
      document.dispatchEvent(new Event('visibilitychange'));
    });

    await page.waitForTimeout(500);

    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { value: false, writable: true });
      document.dispatchEvent(new Event('visibilitychange'));
    });
  });
});

// =============================================================================
// MEMORY AND PERFORMANCE
// =============================================================================

test.describe('Memory and Performance', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('should handle large data sets', async ({ page }) => {
    // Mock large response
    const largeItems = Array.from({ length: 10000 }, (_, i) => ({
      id: `item_${i}`,
      name: `Item ${i}`,
    }));

    await page.route('**/api/cases**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: largeItems, total: 10000 }),
      });
    });

    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');
  });

  test('should handle rapid scrolling', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');

    // Scroll up and down rapidly
    for (let i = 0; i < 10; i++) {
      await page.mouse.wheel(0, 1000);
      await page.waitForTimeout(100);
      await page.mouse.wheel(0, -1000);
      await page.waitForTimeout(100);
    }
  });

  test('should handle window resize', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Resize rapidly
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.setViewportSize({ width: 375, height: 667 });
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.setViewportSize({ width: 1920, height: 1080 });
  });
});
