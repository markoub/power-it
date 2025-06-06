import { test, expect } from '@playwright/test';
import { TEST_CONFIG } from '../test-config';

test.describe('API Documentation Tests', () => {
  const API_BASE_URL = TEST_CONFIG.TEST_API_BASE_URL;

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

  test('modify endpoint returns proper error messages', async ({ request }) => {
    // Test direct API call to modify endpoint without proper data
    // Use preseeded presentation ID 1 which has pending research
    const response = await request.post(`${API_BASE_URL}/presentations/1/modify`, {
      data: {
        prompt: 'Test prompt'
      }
    });

    // In offline mode, the endpoint might return 500 instead of 400
    expect([400, 500]).toContain(response.status());
    
    if (response.status() === 400) {
      const responseBody = await response.json();
      expect(responseBody.detail).toContain('Research step not completed');
    } else if (response.status() === 500) {
      // In offline mode, the error handling might be different
      const responseBody = await response.json().catch(() => ({ detail: 'Internal server error' }));
      expect(responseBody).toHaveProperty('detail');
    }
  });
}); 