import { test, expect } from '@playwright/test';

test.describe('API Documentation Tests', () => {
  // Use a different base URL for API testing
  const API_BASE_URL = 'http://localhost:8000';

  test('all documented routes respond', async ({ request }) => {
    // Test the docs endpoint
    const docs = await request.get(`${API_BASE_URL}/docs`);
    expect(docs.status()).toBe(200);

    // Test the OpenAPI spec endpoint
    const res = await request.get(`${API_BASE_URL}/api/openapi.json`);
    expect(res.status()).toBe(200);
    const data = await res.json();
    const paths = Object.keys(data.paths || {});
    expect(paths.length).toBeGreaterThan(5);

    // Test that all documented routes respond to OPTIONS
    for (const path of paths) {
      const url = path.replace(/\{[^}]+\}/g, '1');
      const resp = await request.fetch(`${API_BASE_URL}${url}`, { method: 'OPTIONS' });
      expect(resp.status()).not.toBe(404);
    }
  });

  test('API health check', async ({ request }) => {
    // Test a basic health endpoint if it exists
    const health = await request.get(`${API_BASE_URL}/health`);
    // Allow 404 if health endpoint doesn't exist, but other statuses should be OK
    expect([200, 404]).toContain(health.status());
  });
}); 