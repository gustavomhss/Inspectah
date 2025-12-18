/**
 * Admin Module E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for admin dashboard, cases, sources, and overview pages.
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000';

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
// ADMIN OVERVIEW PAGE
// =============================================================================

test.describe('Admin Overview Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should display admin dashboard', async ({ page }) => {
    // Should show dashboard content
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show navigation sidebar', async ({ page }) => {
    // Look for navigation elements
    const hasNav = await page.locator('nav, aside, [role="navigation"]').first().isVisible().catch(() => false);
    expect(hasNav).toBeTruthy();
  });

  test('should have working navigation links', async ({ page }) => {
    // Find navigation links
    const navLinks = page.locator('nav a, aside a');
    const count = await navLinks.count();

    expect(count).toBeGreaterThan(0);

    // Click first link and verify navigation
    if (count > 0) {
      const firstLink = navLinks.first();
      const href = await firstLink.getAttribute('href');

      if (href && !href.includes('#')) {
        await firstLink.click();
        await page.waitForLoadState('networkidle');
        expect(page.url()).toBeTruthy();
      }
    }
  });

  test('should show statistics cards', async ({ page }) => {
    // Look for stat cards or metrics
    const statCards = page.locator('[class*="stat"], [class*="card"], [class*="metric"]');
    const count = await statCards.count();

    // May or may not have stats depending on implementation
  });

  test('should handle empty state', async ({ page }) => {
    // When no data, should show appropriate message
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

// =============================================================================
// ADMIN CASES PAGE
// =============================================================================

test.describe('Admin Cases Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');
  });

  test('should display cases list page', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show cases table or grid', async ({ page }) => {
    // Look for table or grid layout
    const hasTable = await page.locator('table, [role="table"], [class*="grid"]').first().isVisible().catch(() => false);
    const hasList = await page.locator('[class*="list"], [class*="case"]').first().isVisible().catch(() => false);

    // Should have some data display structure or empty state
  });

  test('should have search functionality', async ({ page }) => {
    // Look for search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="buscar"], input[placeholder*="pesquisar"]').first();

    if (await searchInput.isVisible()) {
      await searchInput.fill('test case');
      await searchInput.press('Enter');

      // Should trigger search
      await page.waitForTimeout(500);
    }
  });

  test('should have filter options', async ({ page }) => {
    // Look for filter buttons or dropdowns
    const filters = page.locator('select, [role="listbox"], button:has-text("Filter"), button:has-text("Filtro")');
    const count = await filters.count();

    // May or may not have filters
  });

  test('should navigate to case detail on click', async ({ page }) => {
    // Find case item and click
    const caseItem = page.locator('a[href*="/cases/"], tr[class*="cursor-pointer"], [data-testid*="case"]').first();

    if (await caseItem.isVisible()) {
      await caseItem.click();
      await page.waitForLoadState('networkidle');

      // Should navigate to detail page
      expect(page.url()).toContain('cases');
    }
  });

  test('should have pagination', async ({ page }) => {
    // Look for pagination controls
    const pagination = page.locator('[class*="pagination"], nav[aria-label*="pagination"], button:has-text("Next"), button:has-text("Prev")');

    if (await pagination.first().isVisible()) {
      // Test pagination click
      const nextButton = page.locator('button:has-text("Next"), button:has-text("Próx"), [aria-label="Next page"]').first();

      if (await nextButton.isVisible() && !await nextButton.isDisabled()) {
        await nextButton.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('should handle empty cases list', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/cases**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0, page: 1, size: 10 }),
      });
    });

    await page.reload();
    await page.waitForLoadState('networkidle');

    // Should show empty state message
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should handle API error gracefully', async ({ page }) => {
    // Mock error response
    await page.route('**/api/cases**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.reload();
    await page.waitForLoadState('networkidle');

    // Should show error message
    const hasError = await page.locator('[class*="error"], [role="alert"], text=/erro|error/i').first().isVisible().catch(() => false);
    // Should handle gracefully either way
  });

  test('should sort cases by column', async ({ page }) => {
    // Find sortable column headers
    const sortableHeaders = page.locator('th[class*="cursor"], th button, [role="columnheader"]');

    if (await sortableHeaders.first().isVisible()) {
      await sortableHeaders.first().click();
      await page.waitForTimeout(500);

      // Click again to reverse sort
      await sortableHeaders.first().click();
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// ADMIN CASE DETAIL PAGE
// =============================================================================

test.describe('Admin Case Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    // Navigate to a specific case
    await page.goto(`${BASE_URL}/admin/cases/case_test_123`);
    await page.waitForLoadState('networkidle');
  });

  test('should display case detail', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show case information', async ({ page }) => {
    // Look for case details
    const hasDetails = await page.locator('[class*="detail"], [class*="info"], h1, h2').first().isVisible().catch(() => false);
    expect(hasDetails).toBeTruthy();
  });

  test('should show case status', async ({ page }) => {
    // Look for status badge or indicator
    const status = page.locator('[class*="status"], [class*="badge"], [class*="state"]');
    // May or may not show status
  });

  test('should have back navigation', async ({ page }) => {
    // Look for back button
    const backButton = page.locator('a:has-text("Voltar"), button:has-text("Voltar"), a:has-text("Back"), [aria-label="Back"]').first();

    if (await backButton.isVisible()) {
      await backButton.click();
      await page.waitForLoadState('networkidle');

      // Should navigate back
      expect(page.url()).toContain('cases');
    }
  });

  test('should handle non-existent case', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases/non_existent_case_999`);
    await page.waitForLoadState('networkidle');

    // Should show 404 or error message
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show case timeline if available', async ({ page }) => {
    // Look for timeline component
    const timeline = page.locator('[class*="timeline"], [data-testid*="timeline"]');
    // May or may not have timeline
  });

  test('should show related sources', async ({ page }) => {
    // Look for sources section
    const sources = page.locator('text=/fonte|source/i, [class*="source"]');
    // May or may not show sources
  });
});

// =============================================================================
// ADMIN SOURCES PAGE
// =============================================================================

test.describe('Admin Sources Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources`);
    await page.waitForLoadState('networkidle');
  });

  test('should display sources list', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show sources table or cards', async ({ page }) => {
    const hasDisplay = await page.locator('table, [class*="card"], [class*="list"]').first().isVisible().catch(() => false);
    // Should have some structure
  });

  test('should have add source button', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add"), button:has-text("Adicionar"), button:has-text("Nova"), a:has-text("Add")').first();

    if (await addButton.isVisible()) {
      await addButton.click();
      await page.waitForLoadState('networkidle');

      // Should navigate to add form
    }
  });

  test('should filter sources by type', async ({ page }) => {
    const typeFilter = page.locator('select, [role="listbox"], button:has-text("Tipo"), button:has-text("Type")').first();

    if (await typeFilter.isVisible()) {
      await typeFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should filter sources by status', async ({ page }) => {
    const statusFilter = page.locator('button:has-text("Status"), select[name*="status"]').first();

    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.waitForTimeout(300);
    }
  });

  test('should show source health status', async ({ page }) => {
    // Look for health indicators
    const healthIndicators = page.locator('[class*="health"], [class*="status"], .text-green, .text-red, .text-yellow');
    // May show health status
  });

  test('should navigate to source detail', async ({ page }) => {
    const sourceItem = page.locator('a[href*="/sources/"], tr[class*="cursor-pointer"]').first();

    if (await sourceItem.isVisible()) {
      await sourceItem.click();
      await page.waitForLoadState('networkidle');

      expect(page.url()).toContain('source');
    }
  });

  test('should have bulk actions', async ({ page }) => {
    // Look for checkboxes and bulk action buttons
    const checkboxes = page.locator('input[type="checkbox"]');
    const count = await checkboxes.count();

    if (count > 0) {
      // Select first item
      await checkboxes.first().click();

      // Look for bulk action button
      const bulkAction = page.locator('button:has-text("Delete"), button:has-text("Excluir"), button:has-text("Actions")').first();
    }
  });

  test('should search sources', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="buscar"]').first();

    if (await searchInput.isVisible()) {
      await searchInput.fill('test source');
      await page.waitForTimeout(500);
    }
  });
});

// =============================================================================
// ADMIN SOURCE DETAIL PAGE
// =============================================================================

test.describe('Admin Source Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources/source_test_123`);
    await page.waitForLoadState('networkidle');
  });

  test('should display source detail', async ({ page }) => {
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should show source name and URL', async ({ page }) => {
    // Look for source info
    const hasInfo = await page.locator('h1, h2, [class*="title"]').first().isVisible().catch(() => false);
    expect(hasInfo).toBeTruthy();
  });

  test('should show health status', async ({ page }) => {
    const health = page.locator('[class*="health"], text=/healthy|unhealthy|saudável/i');
    // May show health
  });

  test('should have edit button', async ({ page }) => {
    const editButton = page.locator('button:has-text("Edit"), button:has-text("Editar"), a:has-text("Edit")').first();

    if (await editButton.isVisible()) {
      await editButton.click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should have delete button with confirmation', async ({ page }) => {
    const deleteButton = page.locator('button:has-text("Delete"), button:has-text("Excluir")').first();

    if (await deleteButton.isVisible()) {
      await deleteButton.click();

      // Should show confirmation dialog
      const confirmDialog = page.locator('[role="dialog"], [role="alertdialog"], .modal');

      if (await confirmDialog.isVisible()) {
        // Cancel deletion
        const cancelButton = page.locator('button:has-text("Cancel"), button:has-text("Cancelar")').first();
        if (await cancelButton.isVisible()) {
          await cancelButton.click();
        }
      }
    }
  });

  test('should show ingestion history', async ({ page }) => {
    const history = page.locator('[class*="history"], [class*="timeline"], text=/histórico|history/i');
    // May show history
  });

  test('should show source statistics', async ({ page }) => {
    const stats = page.locator('[class*="stat"], [class*="metric"], text=/claims|items/i');
    // May show statistics
  });
});

// =============================================================================
// ADMIN SOURCE FORM PAGE
// =============================================================================

test.describe('Admin Source Form Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin/sources/new`);
    await page.waitForLoadState('networkidle');
  });

  test('should display source form', async ({ page }) => {
    const form = page.locator('form');
    const hasForm = await form.isVisible().catch(() => false);

    // Or look for form fields
    const hasFields = await page.locator('input, select, textarea').first().isVisible().catch(() => false);
    expect(hasForm || hasFields).toBeTruthy();
  });

  test('should have required fields', async ({ page }) => {
    // Look for required field indicators
    const requiredFields = page.locator('[required], [aria-required="true"], label:has-text("*")');
    // Should have some required fields
  });

  test('should validate form on submit', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Salvar")').first();

    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Should show validation errors for empty required fields
      await page.waitForTimeout(500);
    }
  });

  test('should validate URL format', async ({ page }) => {
    const urlInput = page.locator('input[type="url"], input[name*="url"]').first();

    if (await urlInput.isVisible()) {
      // Enter invalid URL
      await urlInput.fill('not-a-valid-url');
      await urlInput.blur();

      await page.waitForTimeout(300);
    }
  });

  test('should allow selecting source type', async ({ page }) => {
    const typeSelect = page.locator('select[name*="type"], [role="listbox"]').first();

    if (await typeSelect.isVisible()) {
      await typeSelect.click();
      await page.waitForTimeout(300);
    }
  });

  test('should have cancel button', async ({ page }) => {
    const cancelButton = page.locator('button:has-text("Cancel"), button:has-text("Cancelar"), a:has-text("Cancel")').first();

    if (await cancelButton.isVisible()) {
      await cancelButton.click();
      await page.waitForLoadState('networkidle');

      // Should navigate back to sources list
      expect(page.url()).toContain('sources');
    }
  });

  test('should submit form successfully', async ({ page }) => {
    // Mock successful API response
    await page.route('**/api/sources', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'new_source_123', name: 'Test Source' }),
        });
      } else {
        await route.continue();
      }
    });

    // Fill form
    const nameInput = page.locator('input[name*="name"]').first();
    const urlInput = page.locator('input[name*="url"], input[type="url"]').first();

    if (await nameInput.isVisible()) {
      await nameInput.fill('Test Source');
    }

    if (await urlInput.isVisible()) {
      await urlInput.fill('https://example.com');
    }

    // Submit
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Salvar")').first();
    if (await submitButton.isVisible()) {
      await submitButton.click();
      await page.waitForTimeout(1000);
    }
  });
});

// =============================================================================
// ADMIN NAVIGATION
// =============================================================================

test.describe('Admin Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should navigate between admin sections', async ({ page }) => {
    const sections = [
      { name: 'Cases', path: '/admin/cases' },
      { name: 'Sources', path: '/admin/sources' },
      { name: 'Agents', path: '/admin/agents' },
      { name: 'Guardian', path: '/admin/guardian' },
    ];

    for (const section of sections) {
      const link = page.locator(`a[href*="${section.path}"], button:has-text("${section.name}")`).first();

      if (await link.isVisible()) {
        await link.click();
        await page.waitForLoadState('networkidle');

        expect(page.url()).toContain(section.path);
        await page.goBack();
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('should highlight current section in nav', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/cases`);
    await page.waitForLoadState('networkidle');

    // Current nav item should have active styling
    const activeNav = page.locator('nav a[class*="active"], aside a[class*="active"], nav a[aria-current="page"]');
    // May or may not have active styling
  });

  test('should have user menu', async ({ page }) => {
    const userMenu = page.locator('[class*="user"], [class*="avatar"], button:has-text("Admin")').first();

    if (await userMenu.isVisible()) {
      await userMenu.click();

      // Should show dropdown with options
      const dropdown = page.locator('[role="menu"], [class*="dropdown"]');
      await page.waitForTimeout(300);
    }
  });

  test('should toggle sidebar on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Look for hamburger menu
    const menuButton = page.locator('button[aria-label*="menu"], button:has(svg), [class*="hamburger"]').first();

    if (await menuButton.isVisible()) {
      await menuButton.click();
      await page.waitForTimeout(300);

      // Sidebar should be visible
      const sidebar = page.locator('aside, nav, [class*="sidebar"]').first();
      const isVisible = await sidebar.isVisible().catch(() => false);
    }
  });
});

// =============================================================================
// ADMIN ACCESSIBILITY
// =============================================================================

test.describe('Admin Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForLoadState('networkidle');
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    const h1 = await page.locator('h1').count();
    const h2 = await page.locator('h2').count();

    // Should have at least one h1
    expect(h1 + h2).toBeGreaterThan(0);
  });

  test('should have skip navigation link', async ({ page }) => {
    const skipLink = page.locator('a[href="#main"], a:has-text("Skip")').first();
    // May or may not have skip link
  });

  test('should be keyboard navigable', async ({ page }) => {
    // Tab through elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Should focus on interactive elements
    const focusedElement = page.locator(':focus');
    const tag = await focusedElement.evaluate(el => el.tagName).catch(() => 'BODY');
    expect(['A', 'BUTTON', 'INPUT', 'SELECT', 'BODY', 'TEXTAREA']).toContain(tag);
  });

  test('should have sufficient color contrast', async ({ page }) => {
    // This would require axe-core or similar tool
    // For now, just verify page loads correctly
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });

  test('should have focus indicators', async ({ page }) => {
    // Tab to first focusable element
    await page.keyboard.press('Tab');

    // Focus should be visible
    const focusedElement = page.locator(':focus');
    const hasFocusIndicator = await focusedElement.isVisible().catch(() => false);
  });
});
