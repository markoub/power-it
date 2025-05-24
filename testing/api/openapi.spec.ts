import { test, expect } from '@playwright/test';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const VALID_METHODS = new Set(['get','post','put','patch','delete','options','head']);

test('all documented endpoints respond with allowed status', async ({ request }) => {
  const specRes = await request.get(`${API_BASE_URL}/api/openapi.json`);
  expect(specRes.status()).toBe(200);
  const spec = await specRes.json();
  const paths = spec.paths || {};

  for (const [path, methods] of Object.entries(paths)) {
    for (const [method, details] of Object.entries(methods as any)) {
      if (!VALID_METHODS.has(method)) continue;
      const urlPath = path.replace(/\{[^}]+\}/g, '1');
      const fetchOptions: any = { method: method.toUpperCase() };
      if ((details as any).requestBody) {
        fetchOptions.headers = { 'Content-Type': 'application/json' };
        fetchOptions.data = {};
      }
      const response = await request.fetch(`${API_BASE_URL}${urlPath}`, fetchOptions);
      const status = response.status();
      if (!/\{[^}]+\}/.test(path)) {
        expect(status).not.toBe(404);
      }
      expect(status).not.toBe(405);
    }
  }
});
