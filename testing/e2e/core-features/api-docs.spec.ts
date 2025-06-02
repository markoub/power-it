import { test, expect } from '@playwright/test';

test.describe('API Documentation Tests', () => {
  const API_BASE_URL = 'http://localhost:8000';

  test('API root endpoint responds', async ({ request }) => {
    const root = await request.get(`${API_BASE_URL}/`);
    expect(root.status()).toBe(200);
    const data = await root.json();
    expect(data).toHaveProperty('message');
    expect(data.message).toContain('PowerIt');
  });

  test('OpenAPI documentation is available', async ({ request }) => {
    const res = await request.get(`${API_BASE_URL}/api/openapi.json`);
    expect(res.status()).toBe(200);
    const data = await res.json();
    
    expect(data).toHaveProperty('openapi');
    expect(data).toHaveProperty('info');
    expect(data).toHaveProperty('paths');
    expect(data.info.title).toContain('PowerIt');
    
    const paths = Object.keys(data.paths || {});
    expect(paths.length).toBeGreaterThan(5);
    
    // Verify some expected endpoints exist
    expect(paths).toContain('/presentations');
    expect(paths).toContain('/images');
    expect(paths).toContain('/');
  });

  test('Swagger UI documentation is accessible', async ({ request }) => {
    const docs = await request.get(`${API_BASE_URL}/docs`);
    expect(docs.status()).toBe(200);
    
    const contentType = docs.headers()['content-type'];
    expect(contentType).toContain('text/html');
  });

  test('documented routes respond with correct HTTP methods', async ({ request }) => {
    const res = await request.get(`${API_BASE_URL}/api/openapi.json`);
    expect(res.status()).toBe(200);
    const data = await res.json();
    const paths = Object.keys(data.paths || {});
    
    // Test specific endpoints with their expected methods
    const endpointTests = [
      { path: '/presentations', method: 'GET', expectedStatus: 200 },
      { path: '/presentations', method: 'POST', expectedStatus: 422 }, // Missing required body
      { path: '/images', method: 'POST', expectedStatus: [422, 500] }, // Missing body or validation error
      { path: '/', method: 'GET', expectedStatus: 200 }
    ];
    
    for (const test of endpointTests) {
      const response = await request.fetch(`${API_BASE_URL}${test.path}`, { 
        method: test.method 
      });
      
      if (Array.isArray(test.expectedStatus)) {
        expect(test.expectedStatus).toContain(response.status());
      } else {
        expect(response.status()).toBe(test.expectedStatus);
      }
    }
  });

  test('API handles invalid requests gracefully', async ({ request }) => {
    const invalidEndpoint = await request.get(`${API_BASE_URL}/nonexistent-endpoint`);
    expect(invalidEndpoint.status()).toBe(404);
    
    const errorData = await invalidEndpoint.json();
    expect(errorData).toHaveProperty('detail');
  });
}); 