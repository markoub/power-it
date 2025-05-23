import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './',
  workers: 1,
  use: {
    baseURL: process.env.API_BASE_URL || 'http://localhost:8000',
  },
});
