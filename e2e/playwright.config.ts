// Playwright config for v1-02.
//
// Targets the staging API by default and the vite dev server for the
// parent SPA. The two URL are configured by env so CI can swap in its
// own values.
import { defineConfig } from '@playwright/test';

const API_BASE_URL = process.env.E2E_API_URL ?? 'http://127.0.0.1:13000';
const SPA_BASE_URL = process.env.E2E_SPA_URL ?? 'http://127.0.0.1:5173';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? [['list'], ['json', { outputFile: 'playwright-report.json' }]] : 'list',
  use: {
    baseURL: SPA_BASE_URL,
    trace: 'retain-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 20_000,
  },
  expect: {
    timeout: 5_000,
  },
});

export const env = { API_BASE_URL, SPA_BASE_URL };
