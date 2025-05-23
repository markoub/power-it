import { test, expect } from '@playwright/test';

test('all documented routes respond', async ({ request }) => {
  const docs = await request.get('/docs');
  expect(docs.status()).toBe(200);

  const res = await request.get('/api/openapi.json');
  expect(res.status()).toBe(200);
  const data = await res.json();
  const paths = Object.keys(data.paths || {});
  expect(paths.length).toBeGreaterThan(5);

  for (const path of paths) {
    const url = path.replace(/\{[^}]+\}/g, '1');
    const resp = await request.fetch(url, { method: 'OPTIONS' });
    expect(resp.status()).not.toBe(404);
  }
});
