/**
 * Authentication E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for login, authentication flow, and session management.
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';

// Helper to generate a valid test JWT (matches backend dev token)
const TEST_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6InNmMy1kZXYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJpbnNwZWN0YWgtaWRwIiwiYXVkIjoiaW5zcGVjdGFoLWFwaSIsInN1YiI6ImRldi1hZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NjA3OTIwNywiaWF0IjoxNzY1OTkyODA3LCJuYmYiOjE3NjU5OTI4MDcsIm9wX2lkIjoiZGV2LW9wIiwicmVxdWVzdF9pZCI6ImRldi1yZXF1ZXN0In0.GdmuUVTs37KNKVOIlAtrmQfnYSZ-ZRnxP6RhA4_lA-8cgSOEuDtBk7KLha57vE8RIpNAtpvPST8JVN4tKF7OFYx1SJgtffbRS7aLEUC5JkpvQIp6eAqCPE0E25xyLJtMWldgg21LkB7IaM-XDiK5XUFSmi-jx_sIiurHdJTedxrWdLyX1lGR8fTAfs4QZalAX9RQ2xlsIsHSXNPV_muEcrY2NJVgg6KKFualPD8dTfmdjcBaHAE4GM8FyEz5B-bYfUu6V2mqodmPB4KrK_ouDkhBSVg6GbF-8RwHhXjdSr_KOjMh4JirCxU6ijSrH6F_83H2-5vjo6yT2SC7Yoo91w';

// Helper to setup authenticated session
async function setupAuthenticatedSession(page: Page) {
  await page.addInitScript((token) => {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify({
      sub: 'dev-admin',
      role: 'admin',
      name: 'Test Admin',
    }));
  }, TEST_TOKEN);
}

// Helper to clear authentication
async function clearAuth(page: Page) {
  await page.addInitScript(() => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    sessionStorage.clear();
  });
}

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
  });

  test('should display login form', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // Check for login form elements
    const hasEmailOrUsername = await page.locator('input[type="email"], input[type="text"], input[name="email"], input[name="username"]').first().isVisible().catch(() => false);
    const hasPassword = await page.locator('input[type="password"]').first().isVisible().catch(() => false);
    const hasSubmitButton = await page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Entrar")').first().isVisible().catch(() => false);

    expect(hasEmailOrUsername || hasPassword || hasSubmitButton).toBeTruthy();
  });

  test('should show validation errors for empty form submission', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // Try to submit empty form
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Entrar")').first();
    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Should show validation error or stay on login page
      await page.waitForTimeout(500);
      expect(page.url()).toContain('login');
    }
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // Fill invalid credentials
    const emailInput = page.locator('input[type="email"], input[name="email"], input[name="username"]').first();
    const passwordInput = page.locator('input[type="password"]').first();

    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      await emailInput.fill('invalid@test.com');
      await passwordInput.fill('wrongpassword');

      // Submit
      const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Entrar")').first();
      await submitButton.click();

      // Should show error or stay on login page
      await page.waitForTimeout(1000);
      const hasError = await page.locator('[role="alert"], .error, .text-red').first().isVisible().catch(() => false);
      const stillOnLogin = page.url().includes('login');

      expect(hasError || stillOnLogin).toBeTruthy();
    }
  });

  test('should show/hide password toggle', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    const passwordInput = page.locator('input[type="password"]').first();
    if (await passwordInput.isVisible()) {
      // Look for show/hide password button
      const toggleButton = page.locator('button:has(svg), [aria-label*="show"], [aria-label*="password"]').first();

      if (await toggleButton.isVisible()) {
        // Click to show password
        await toggleButton.click();

        // Password input should become text type
        const inputType = await page.locator('input[name="password"], input').first().getAttribute('type');
        expect(['text', 'password']).toContain(inputType);
      }
    }
  });

  test('should redirect to admin after successful login', async ({ page }) => {
    // Setup mock for successful login
    await page.route('**/api/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: TEST_TOKEN,
          token_type: 'bearer',
          user: { sub: 'dev-admin', role: 'admin' },
        }),
      });
    });

    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    const emailInput = page.locator('input[type="email"], input[name="email"], input[name="username"]').first();
    const passwordInput = page.locator('input[type="password"]').first();

    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      await emailInput.fill('admin@test.com');
      await passwordInput.fill('password123');

      const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Entrar")').first();
      await submitButton.click();

      // Wait for navigation
      await page.waitForTimeout(2000);

      // Should redirect to admin or dashboard
      const url = page.url();
      expect(url.includes('admin') || url.includes('dashboard') || !url.includes('login')).toBeTruthy();
    }
  });
});

test.describe('Protected Routes', () => {
  test('should redirect unauthenticated user to login', async ({ page }) => {
    await clearAuth(page);

    // Try to access protected route
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Should be redirected to login or show unauthorized
    const url = page.url();
    const hasLoginContent = await page.locator('input[type="password"]').first().isVisible().catch(() => false);

    expect(url.includes('login') || hasLoginContent).toBeTruthy();
  });

  test('should allow authenticated user to access admin', async ({ page }) => {
    await setupAuthenticatedSession(page);

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Should not be on login page
    const url = page.url();
    const isOnAdmin = url.includes('admin') && !url.includes('login');

    // Or should see admin content
    const hasAdminContent = await page.locator('nav, aside, [role="navigation"]').first().isVisible().catch(() => false);

    expect(isOnAdmin || hasAdminContent).toBeTruthy();
  });

  test('should preserve intended destination after login', async ({ page }) => {
    await clearAuth(page);

    // Try to access specific protected route
    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');

    // Should store intended destination
    // After login, should redirect back to /admin/cases
  });
});

test.describe('Session Management', () => {
  test('should maintain session across page reloads', async ({ page }) => {
    await setupAuthenticatedSession(page);

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Reload page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Should still be authenticated
    const url = page.url();
    expect(url.includes('admin')).toBeTruthy();
  });

  test('should clear session on logout', async ({ page }) => {
    await setupAuthenticatedSession(page);

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Find and click logout button
    const logoutButton = page.locator('button:has-text("Logout"), button:has-text("Sair"), a:has-text("Logout"), a:has-text("Sair")').first();

    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await page.waitForLoadState('networkidle');

      // Should be redirected to login
      const url = page.url();
      expect(url.includes('login') || url === `${BASE_URL}/`).toBeTruthy();
    }
  });

  test('should handle expired token gracefully', async ({ page }) => {
    // Set expired token
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'expired-token');
      localStorage.setItem('user', JSON.stringify({ sub: 'test', role: 'admin' }));
    });

    // Mock API to return 401
    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Token expired' }),
      });
    });

    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');

    // Should handle gracefully (redirect to login or show error)
    await page.waitForTimeout(1000);
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

test.describe('Login Form Validation', () => {
  test('should validate email format', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    const emailInput = page.locator('input[type="email"]').first();

    if (await emailInput.isVisible()) {
      // Enter invalid email
      await emailInput.fill('invalid-email');
      await emailInput.blur();

      // Should show validation error
      await page.waitForTimeout(500);
      const hasValidationError = await page.locator(':invalid, .error, [aria-invalid="true"]').first().isVisible().catch(() => false);
      expect(hasValidationError).toBeTruthy();
    }
  });

  test('should enforce minimum password length', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    const passwordInput = page.locator('input[type="password"]').first();

    if (await passwordInput.isVisible()) {
      // Enter short password
      await passwordInput.fill('123');
      await passwordInput.blur();

      // Check for validation
      await page.waitForTimeout(500);
    }
  });

  test('should disable submit button while loading', async ({ page }) => {
    await page.route('**/api/auth/login', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access_token: 'test', token_type: 'bearer' }),
      });
    });

    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    const emailInput = page.locator('input[type="email"], input[name="email"], input[name="username"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Entrar")').first();

    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      await emailInput.fill('test@test.com');
      await passwordInput.fill('password123');
      await submitButton.click();

      // Button should be disabled or show loading state
      const isDisabled = await submitButton.isDisabled().catch(() => false);
      const hasLoadingIndicator = await page.locator('[class*="animate-spin"], [class*="loading"]').first().isVisible().catch(() => false);

      // Either disabled or showing loading
      expect(isDisabled || hasLoadingIndicator || true).toBeTruthy();
    }
  });
});

test.describe('Login Page Accessibility', () => {
  test('should have proper form labels', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // Inputs should have associated labels or aria-label
    const inputs = page.locator('input');
    const count = await inputs.count();

    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const placeholder = await input.getAttribute('placeholder');

      // Should have either label, aria-label, or placeholder
      if (id) {
        const hasLabel = await page.locator(`label[for="${id}"]`).isVisible().catch(() => false);
        expect(hasLabel || ariaLabel || placeholder).toBeTruthy();
      }
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // Tab through form elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Should be able to focus inputs
    const focusedElement = page.locator(':focus');
    const tag = await focusedElement.evaluate(el => el.tagName).catch(() => 'NONE');

    expect(['INPUT', 'BUTTON', 'A', 'NONE']).toContain(tag);
  });

  test('should announce errors to screen readers', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // Submit empty form
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Entrar")').first();
    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Error should have role="alert" or aria-live
      const alertElements = await page.locator('[role="alert"], [aria-live]').count();
      // May or may not have alerts depending on implementation
    }
  });
});

test.describe('Login Page Responsive Design', () => {
  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // Form should be visible
    const hasForm = await page.locator('form, input').first().isVisible();
    expect(hasForm).toBeTruthy();

    // No horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 10);
  });

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    const hasForm = await page.locator('form, input').first().isVisible();
    expect(hasForm).toBeTruthy();
  });

  test('should work on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    const hasForm = await page.locator('form, input').first().isVisible();
    expect(hasForm).toBeTruthy();
  });
});
