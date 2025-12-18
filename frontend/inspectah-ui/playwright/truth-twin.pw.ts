/**
 * Truth Twin E2E Tests
 *
 * Tests for the S40 Truth Twin page functionality.
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';

test.describe('Truth Twin Page', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the Truth Twin page
    await page.goto(`${BASE_URL}/admin/truth-twin`);
    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display the Truth Twin page', async ({ page }) => {
    // Check page title/header (h1)
    await expect(page.locator('h1:has-text("Truth Twin")')).toBeVisible();

    // Check search input exists
    await expect(page.getByPlaceholder(/claim id|slug/i)).toBeVisible();

    // Check search button exists
    await expect(page.getByRole('button', { name: /buscar/i })).toBeVisible();
  });

  test('should show empty state initially', async ({ page }) => {
    // Should show empty state message
    await expect(page.getByText(/digite.*claim.*id/i)).toBeVisible();
  });

  test('should search for a claim and display results', async ({ page }) => {
    // Enable console logging
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));

    // Type claim ID
    const searchInput = page.getByPlaceholder(/claim id|slug/i);
    await searchInput.fill('cl_lava_jato_000');

    // Click search button
    const searchButton = page.getByRole('button', { name: /buscar/i });
    console.log('Clicking search button...');
    await searchButton.click();

    // Wait a bit for state update
    await page.waitForTimeout(2000);

    // Get page content for debug
    const pageContent = await page.content();
    console.log('Page contains "cl_lava_jato_000":', pageContent.includes('cl_lava_jato_000'));
    console.log('Page contains "ESTABLISHED_FACT":', pageContent.includes('ESTABLISHED_FACT'));
    console.log('Page contains "error":', pageContent.toLowerCase().includes('error'));

    // Take a screenshot
    await page.screenshot({ path: '/tmp/truth-twin-debug.png' });

    // Wait for API response or timeout
    try {
      await page.waitForResponse(
        response => response.url().includes('/api/truth/cl_lava_jato_000/twin'),
        { timeout: 10000 }
      );
      console.log('API response received');
    } catch (e) {
      console.log('API response not received within timeout');
    }

    // Wait more for rendering
    await page.waitForTimeout(3000);

    // Should show results container
    await expect(page.getByTestId('truth-twin-results')).toBeVisible({ timeout: 10000 });

    // Should show claim text prominently (the main claim content)
    await expect(page.getByTestId('claim-text')).toBeVisible();
    await expect(page.getByTestId('claim-text')).toContainText(/1a fase Lava Jato/);

    // Should also have "A Claim" label inside results
    await expect(page.getByTestId('truth-twin-results').getByText('A Claim')).toBeVisible();

    // Should show state badge (ESTABLISHED_FACT) - use first() for multiple matches
    await expect(page.getByText('ESTABLISHED_FACT').first()).toBeVisible();

    // Should show decision timeline section
    await expect(page.getByText('Timeline de Decisões')).toBeVisible();

    // Should show provenance section
    await expect(page.getByRole('heading', { name: 'Proveniência' }).first()).toBeVisible();
  });

  test('should handle search with Enter key', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/claim id|slug/i);
    await searchInput.fill('cl_covid19_brasil_050');

    // Press Enter
    await searchInput.press('Enter');

    // Wait for API response
    await page.waitForResponse(response =>
      response.url().includes('/api/truth/cl_covid19_brasil_050/twin') &&
      response.status() === 200
    );

    // Should show results
    await expect(page.getByText('cl_covid19_brasil_050')).toBeVisible();
  });

  test('should display decision details when clicking timeline item', async ({ page }) => {
    // Search for a claim
    const searchInput = page.getByPlaceholder(/claim id|slug/i);
    await searchInput.fill('cl_lava_jato_000');
    await page.getByRole('button', { name: /buscar/i }).click();

    // Wait for results
    await page.waitForResponse(response =>
      response.url().includes('/api/truth/cl_lava_jato_000/twin') &&
      response.status() === 200
    );

    // Wait for timeline to render
    await page.waitForTimeout(1000);

    // Check that gate badges are visible (G0, G1, etc)
    const gateBadge = page.locator('text=/G[0-4]/');
    await expect(gateBadge.first()).toBeVisible();

    // Click on the first timeline item (the decision)
    const timelineItem = page.locator('[class*="cursor-pointer"]').first();
    await timelineItem.click();

    // Wait for the inspect API call
    await page.waitForResponse(
      response => response.url().includes('/api/truth/decision/') && response.url().includes('/inspect'),
      { timeout: 10000 }
    );

    // Wait for modal to appear
    await page.waitForTimeout(500);

    // Verify modal content appears
    await expect(page.getByText('Inspeção de Decisão')).toBeVisible();

    // Verify decision details are shown (should show state transition)
    await expect(page.getByText('Transição de Estado')).toBeVisible();

    // Verify S40 decision content is shown
    await expect(page.getByText('Razão da Decisão')).toBeVisible();
    await expect(page.getByText(/Decision after G1 verification/)).toBeVisible();

    // Verify committee decision is shown
    await expect(page.getByText('Decisão:')).toBeVisible();
    await expect(page.getByText('Confiança:')).toBeVisible();
    await expect(page.getByText('Notas')).toBeVisible();
    await expect(page.getByText(/Verified:.*Lava Jato/)).toBeVisible();

    // Close modal by clicking backdrop or X button
    const closeButton = page.locator('button').filter({ has: page.locator('svg path[d*="M6 18L18 6"]') });
    await closeButton.click();

    // Modal should be closed
    await expect(page.getByText('Inspeção de Decisão')).not.toBeVisible();
  });

  test('should show error for non-existent claim', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/claim id|slug/i);
    await searchInput.fill('cl_does_not_exist_12345');
    await page.getByRole('button', { name: /buscar/i }).click();

    // Wait for error response or error state
    await page.waitForTimeout(2000);

    // Should show error message
    const errorVisible = await page.getByText(/erro|not found|não encontrad/i).first().isVisible();
    expect(errorVisible).toBe(true);
  });

  test('should display provenance with guias and pilares', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/claim id|slug/i);
    await searchInput.fill('cl_lava_jato_000');
    await page.getByRole('button', { name: /buscar/i }).click();

    // Wait for results
    await page.waitForResponse(response =>
      response.url().includes('/api/truth/cl_lava_jato_000/twin') &&
      response.status() === 200
    );

    // Wait for provenance to render
    await page.waitForTimeout(1000);

    // Check for references section (S40)
    const hasReferences = await page.getByText(/guias|pilares|e40\.5/i).first().isVisible().catch(() => false);
    expect(hasReferences).toBe(true);
  });
});
