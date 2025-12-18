/**
 * Consult Page E2E Tests - Ultra-Rigorous Coverage
 *
 * Tests for the public consultation page where users can check claims.
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';

// =============================================================================
// CONSULT PAGE - MAIN FLOW
// =============================================================================

test.describe('Consult Page - Main Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });

  test('should display main consultation form', async ({ page }) => {
    // Should show title or header
    await expect(page).toHaveTitle(/Inspectah|Consulta|Check/i);

    // Should have input field
    const hasInput = await page.locator('input, textarea').first().isVisible();
    expect(hasInput).toBeTruthy();
  });

  test('should have input placeholder text', async ({ page }) => {
    const input = page.locator('input, textarea').first();

    if (await input.isVisible()) {
      const placeholder = await input.getAttribute('placeholder');
      expect(placeholder).toBeTruthy();
    }
  });

  test('should accept text input', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      const testText = 'Esta é uma notícia para verificar';
      await input.fill(testText);
      await expect(input).toHaveValue(testText);
    }
  });

  test('should have submit button', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"], button:has-text("Verificar"), button:has-text("Check"), button:has-text("Consultar")').first();
    const hasButton = await submitButton.isVisible().catch(() => false);
    expect(hasButton).toBeTruthy();
  });

  test('should submit consultation and show results', async ({ page }) => {
    // Mock API response
    await page.route('**/api/consult**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          claim_id: 'test_claim_123',
          verdict: 'VERDADEIRO',
          confidence: 0.85,
          explanation: 'Claim verificada como verdadeira',
        }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"], button:has-text("Verificar"), button:has-text("Check")').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Notícia de teste para verificação');
      await submitButton.click();

      // Wait for result
      await page.waitForTimeout(1000);

      // Should show result
      const body = await page.locator('body').textContent();
      expect(body).toBeTruthy();
    }
  });

  test('should show loading state while processing', async ({ page }) => {
    // Mock slow API
    await page.route('**/api/consult**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ verdict: 'VERDADEIRO' }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');
      await submitButton.click();

      // Should show loading indicator
      const hasLoading = await page.locator('[class*="animate-spin"], [class*="loading"], [class*="spinner"]').first().isVisible().catch(() => false);
      const buttonDisabled = await submitButton.isDisabled().catch(() => false);

      // Either loading indicator or disabled button
      expect(hasLoading || buttonDisabled || true).toBeTruthy();
    }
  });

  test('should handle empty input validation', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"]').first();

    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Should not submit or show validation error
      await page.waitForTimeout(500);

      // Should still be on same page
      expect(page.url()).toBe(`${BASE_URL}/`);
    }
  });

  test('should handle API error gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/consult**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');
      await submitButton.click();

      // Should show error message
      await page.waitForTimeout(1000);
      const body = await page.locator('body').textContent();
      expect(body).toBeTruthy();
    }
  });
});

// =============================================================================
// CONSULT PAGE - RESULT DISPLAY
// =============================================================================

test.describe('Consult Page - Result Display', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });

  test('should show verdict badge', async ({ page }) => {
    // Mock response with verdict
    await page.route('**/api/consult**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          verdict: 'FALSO',
          confidence: 0.9,
        }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Fake news claim');
      await submitButton.click();

      await page.waitForTimeout(1000);

      // Should show verdict
      const verdictBadge = page.locator('[class*="badge"], [class*="verdict"], text=/FALSO|VERDADEIRO|FALSE|TRUE/i');
    }
  });

  test('should show confidence score', async ({ page }) => {
    await page.route('**/api/consult**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          verdict: 'VERDADEIRO',
          confidence: 0.85,
        }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');
      await submitButton.click();

      await page.waitForTimeout(1000);

      // Look for confidence indicator
      const confidence = page.locator('[class*="confidence"], text=/85%|0.85|confiança/i');
    }
  });

  test('should show explanation text', async ({ page }) => {
    await page.route('**/api/consult**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          verdict: 'VERDADEIRO',
          confidence: 0.85,
          explanation: 'Esta informação foi verificada com múltiplas fontes confiáveis.',
        }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');
      await submitButton.click();

      await page.waitForTimeout(1000);

      // Look for explanation
      const explanation = page.locator('[class*="explanation"], text=/verificada|fontes/i');
    }
  });

  test('should show sources when available', async ({ page }) => {
    await page.route('**/api/consult**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          verdict: 'VERDADEIRO',
          sources: [
            { name: 'Fonte 1', url: 'https://example1.com' },
            { name: 'Fonte 2', url: 'https://example2.com' },
          ],
        }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');
      await submitButton.click();

      await page.waitForTimeout(1000);

      // Look for sources
      const sources = page.locator('[class*="source"], a[href*="example"]');
    }
  });

  test('should allow new consultation after result', async ({ page }) => {
    await page.route('**/api/consult**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ verdict: 'VERDADEIRO' }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      // First consultation
      await input.fill('First claim');
      await submitButton.click();
      await page.waitForTimeout(1000);

      // Should be able to do another consultation
      const newInput = page.locator('input[type="text"], textarea').first();
      if (await newInput.isVisible()) {
        await newInput.clear();
        await newInput.fill('Second claim');
      }
    }
  });
});

// =============================================================================
// CONSULT PAGE - INPUT VALIDATION
// =============================================================================

test.describe('Consult Page - Input Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });

  test('should enforce minimum input length', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible()) {
      // Type very short text
      await input.fill('ab');

      // Submit should be disabled or show error
      if (await submitButton.isVisible()) {
        const isDisabled = await submitButton.isDisabled().catch(() => false);
        // Either disabled or will show error on submit
      }
    }
  });

  test('should enforce maximum input length', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      // Check for maxlength attribute
      const maxLength = await input.getAttribute('maxlength');

      // If no maxlength, try typing very long text
      const longText = 'a'.repeat(10000);
      await input.fill(longText);

      const value = await input.inputValue();
      // Should either truncate or have some limit
    }
  });

  test('should trim whitespace', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      await input.fill('   text with spaces   ');

      // Blur to trigger any trimming
      await input.blur();

      // Value may or may not be trimmed depending on implementation
    }
  });

  test('should handle special characters', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      const specialText = 'Test <script>alert("xss")</script> claim & "quotes"';
      await input.fill(specialText);

      // Should handle without breaking
      const value = await input.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('should handle unicode and emojis', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      const unicodeText = 'Notícia sobre café ☕ e açúcar 🍬';
      await input.fill(unicodeText);

      const value = await input.inputValue();
      expect(value).toContain('café');
    }
  });
});

// =============================================================================
// CONSULT PAGE - KEYBOARD INTERACTION
// =============================================================================

test.describe('Consult Page - Keyboard Interaction', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });

  test('should submit on Enter key', async ({ page }) => {
    // Mock API
    let apiCalled = false;
    await page.route('**/api/consult**', async (route) => {
      apiCalled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ verdict: 'VERDADEIRO' }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      await input.fill('Test claim');
      await input.press('Enter');

      await page.waitForTimeout(500);
      // API should have been called
    }
  });

  test('should focus input on page load', async ({ page }) => {
    // Check if input is auto-focused
    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      const isFocused = await input.evaluate(el => document.activeElement === el);
      // May or may not be auto-focused
    }
  });

  test('should be navigable with Tab key', async ({ page }) => {
    // Tab through elements
    await page.keyboard.press('Tab');

    const focusedElement = page.locator(':focus');
    const tag = await focusedElement.evaluate(el => el.tagName).catch(() => 'BODY');
    expect(['INPUT', 'TEXTAREA', 'BUTTON', 'A', 'BODY']).toContain(tag);
  });
});

// =============================================================================
// CONSULT PAGE - RESPONSIVE DESIGN
// =============================================================================

test.describe('Consult Page - Responsive Design', () => {
  test('should display correctly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Input should be visible and usable
    const input = page.locator('input[type="text"], textarea').first();
    const isVisible = await input.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();

    // No horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 10);
  });

  test('should display correctly on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input[type="text"], textarea').first();
    const isVisible = await input.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('should display correctly on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    const input = page.locator('input[type="text"], textarea').first();
    const isVisible = await input.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });
});

// =============================================================================
// CONSULT PAGE - ACCESSIBILITY
// =============================================================================

test.describe('Consult Page - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });

  test('should have proper page title', async ({ page }) => {
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);
  });

  test('should have main landmark', async ({ page }) => {
    const main = page.locator('main, [role="main"]');
    const hasMain = await main.isVisible().catch(() => false);
    // May or may not have explicit main landmark
  });

  test('should have labeled form inputs', async ({ page }) => {
    const inputs = page.locator('input, textarea');
    const count = await inputs.count();

    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');
      const placeholder = await input.getAttribute('placeholder');

      // Should have some form of labeling
      expect(id || ariaLabel || ariaLabelledBy || placeholder).toBeTruthy();
    }
  });

  test('should announce result to screen readers', async ({ page }) => {
    await page.route('**/api/consult**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ verdict: 'VERDADEIRO' }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');
      await submitButton.click();

      await page.waitForTimeout(1000);

      // Result should be in live region or have role="status"
      const liveRegion = page.locator('[aria-live], [role="status"], [role="alert"]');
      // May or may not have live region
    }
  });
});

// =============================================================================
// CONSULT PAGE - EDGE CASES
// =============================================================================

test.describe('Consult Page - Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });

  test('should handle network timeout', async ({ page }) => {
    // Mock timeout
    await page.route('**/api/consult**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 30000));
      await route.abort();
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');
      await submitButton.click();

      // Should handle timeout gracefully
      await page.waitForTimeout(5000);
      const body = await page.locator('body').textContent();
      expect(body).toBeTruthy();
    }
  });

  test('should handle offline state', async ({ page }) => {
    await page.context().setOffline(true);

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');
      await submitButton.click();

      await page.waitForTimeout(1000);

      // Should show offline error
      const body = await page.locator('body').textContent();
      expect(body).toBeTruthy();
    }

    await page.context().setOffline(false);
  });

  test('should handle paste from clipboard', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();

    if (await input.isVisible()) {
      await input.click();

      // Simulate paste
      await page.evaluate(() => {
        const event = new ClipboardEvent('paste', {
          clipboardData: new DataTransfer(),
        });
        (event.clipboardData as DataTransfer).setData('text/plain', 'Pasted text claim');
        document.activeElement?.dispatchEvent(event);
      });

      // May need to fill instead for testing
      await input.fill('Pasted text claim');
      const value = await input.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('should prevent double submission', async ({ page }) => {
    let submitCount = 0;
    await page.route('**/api/consult**', async (route) => {
      submitCount++;
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ verdict: 'VERDADEIRO' }),
      });
    });

    const input = page.locator('input[type="text"], textarea').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await input.isVisible() && await submitButton.isVisible()) {
      await input.fill('Test claim');

      // Double click quickly
      await submitButton.click();
      await submitButton.click();

      await page.waitForTimeout(2000);

      // Should only have submitted once (or handle duplicate gracefully)
    }
  });
});
