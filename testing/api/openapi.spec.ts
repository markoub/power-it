import { test, expect } from '@playwright/test';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const VALID_METHODS = new Set(['get','post','put','patch','delete','options','head']);

// Endpoints that we can safely test without requiring real data
const SAFE_ENDPOINTS = new Set([
  '/',
  '/presentations',
  '/presentations/slide-types',
]);

// Endpoints that require parameters but we can test with a valid presentation
const PARAMETIZED_ENDPOINTS_TO_SKIP = new Set([
  '/presentations/{presentation_id}',
  '/presentations/{presentation_id}/steps/{step_name}/run',
  '/presentations/{presentation_id}/steps/{step_name}',
  '/presentations/{presentation_id}/save_modified',
  '/presentations/{presentation_id}/modify',
  '/presentations/{presentation_id}/slides/{slide_index}/image',
  '/presentations/{presentation_id}/images/{filename}',
  '/presentations/{presentation_id}/pptx-slides',
  '/presentations/{presentation_id}/pptx-slides/{filename}',
  '/presentations/{presentation_id}/download-pptx',
  '/presentations/{presentation_id}/download-pdf',
  '/presentations/{presentation_id}/update-topic',
  '/logos/{term}',
]);

test('OpenAPI spec is accessible and valid', async ({ request }) => {
  const specRes = await request.get(`${API_BASE_URL}/api/openapi.json`);
  expect(specRes.status()).toBe(200);
  
  const spec = await specRes.json();
  
  // Validate OpenAPI spec structure
  expect(spec).toHaveProperty('openapi');
  expect(spec).toHaveProperty('info');
  expect(spec).toHaveProperty('paths');
  expect(spec.info).toHaveProperty('title');
  expect(spec.info).toHaveProperty('version');
  
  console.log(`OpenAPI spec loaded: ${spec.info.title} v${spec.info.version}`);
  console.log(`Found ${Object.keys(spec.paths).length} API paths`);
});

test('safe endpoints respond correctly', async ({ request }) => {
  const specRes = await request.get(`${API_BASE_URL}/api/openapi.json`);
  expect(specRes.status()).toBe(200);
  const spec = await specRes.json();
  const paths = spec.paths || {};

  for (const [path, methods] of Object.entries(paths)) {
    // Only test safe endpoints that don't require parameters
    if (!SAFE_ENDPOINTS.has(path)) continue;
    
    for (const [method, details] of Object.entries(methods as any)) {
      if (!VALID_METHODS.has(method)) continue;
      
      console.log(`Testing ${method.toUpperCase()} ${path}`);
      
      const fetchOptions: any = { method: method.toUpperCase() };
      if ((details as any).requestBody && method !== 'get') {
        fetchOptions.headers = { 'Content-Type': 'application/json' };
        // Provide minimal valid data for POST endpoints
        if (path === '/presentations' && method === 'post') {
          fetchOptions.data = { name: 'Test Presentation', topic: 'Test Topic' };
        } else if (path === '/logos/search' && method === 'post') {
          fetchOptions.data = { term: 'test' };
        } else {
          fetchOptions.data = {};
        }
      }
      
      try {
        const response = await request.fetch(`${API_BASE_URL}${path}`, fetchOptions);
        const status = response.status();
        
        // Should not return method not allowed
        expect(status).not.toBe(405);
        
        // For safe endpoints without parameters, should not return 404
        expect(status).not.toBe(404);
        
        // Should return a valid HTTP status code
        expect(status).toBeGreaterThanOrEqual(200);
        expect(status).toBeLessThan(600);
        
        console.log(`✓ ${method.toUpperCase()} ${path} → ${status}`);
      } catch (error) {
        console.error(`✗ ${method.toUpperCase()} ${path} → Error: ${error}`);
        throw error;
      }
    }
  }
});

test('parametized endpoints are documented correctly', async ({ request }) => {
  const specRes = await request.get(`${API_BASE_URL}/api/openapi.json`);
  expect(specRes.status()).toBe(200);
  const spec = await specRes.json();
  const paths = spec.paths || {};

  for (const [path, methods] of Object.entries(paths)) {
    // Only check parametized endpoints
    if (!path.includes('{') || !PARAMETIZED_ENDPOINTS_TO_SKIP.has(path)) continue;
    
    for (const [method, details] of Object.entries(methods as any)) {
      if (!VALID_METHODS.has(method)) continue;
      
      const methodDetails = details as any;
      
      // Parametized endpoints should have parameters defined
      if (path.includes('{')) {
        expect(methodDetails).toHaveProperty('parameters');
        expect(Array.isArray(methodDetails.parameters)).toBe(true);
        
        // Extract parameter names from path
        const pathParams = path.match(/\{([^}]+)\}/g)?.map(p => p.slice(1, -1)) || [];
        
        // Check that all path parameters are documented
        const docParams = methodDetails.parameters
          .filter((p: any) => p.in === 'path')
          .map((p: any) => p.name);
        
        for (const pathParam of pathParams) {
          expect(docParams).toContain(pathParam);
        }
        
        console.log(`✓ ${method.toUpperCase()} ${path} has correct parameter documentation`);
      }
    }
  }
});
