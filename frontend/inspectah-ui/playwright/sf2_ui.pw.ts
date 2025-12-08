import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

test('sf2 capture console state', async ({ page }) => {
  await page.goto('http://127.0.0.1:8000', { waitUntil: 'domcontentloaded' });
  const dirname = path.dirname(fileURLToPath(import.meta.url));
  const screenshotPath = path.resolve(dirname, '..', '..', '..', 'out', 'evidence', 'SF2_G4', 'provider_screens', 'console.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  expect(await page.title()).toBeDefined();
});
