import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'playwright',
  testMatch: '**/*.pw.ts',
  reporter: 'line',
  use: {
    headless: true,
  },
});
