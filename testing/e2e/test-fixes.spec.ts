import { test, expect } from '@playwright/test';
import { createPresentation, getApiUrl } from './utils';

test.describe('Bug Fixes Verification', () => {
  test.setTimeout(120000);

  test('should not call modify endpoint during research step', async ({ page }) => {
    const name = `Fix Test ${Date.now()}`;
    const topic = 'Test topic for fix verification';

    // Track network requests to catch any modify calls
    const modifyRequests: any[] = [];
    page.on('request', request => {
      if (request.url().includes('/modify')) {
        modifyRequests.push({
          url: request.url(),
          method: request.method(),
          timestamp: Date.now()
        });
      }
    });

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);
    console.log(`Created presentation ID: ${presentationId}`);

    // Wait for initial load
    await page.waitForTimeout(3000);

    // Verify we're on research step
    const researchStep = page.getByTestId('step-nav-research');
    await expect(researchStep).toHaveClass(/bg-primary/);

    // Try to interact with wizard during research step (if available)
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    if (await wizardInput.isVisible() && await sendButton.isVisible()) {
      await wizardInput.fill('Can you help improve this presentation?');
      await sendButton.click();
      
      // Wait a moment for any potential API calls
      await page.waitForTimeout(2000);
    } else {
      console.log('Wizard not available during research step - this is expected behavior');
    }

    // Start AI research
    await page.getByTestId('start-ai-research-button').click();

    // Wait for research to complete
    await expect(page.getByTestId('ai-research-content')).toBeVisible({ timeout: 30000 });

    // Verify no modify requests were made during research
    console.log('All modify requests:', modifyRequests);
    expect(modifyRequests.length).toBe(0);
  });

  test('should handle modify endpoint errors gracefully', async ({ page }) => {
    const name = `Error Test ${Date.now()}`;
    const topic = 'Test topic for error handling';

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);

    // Complete research step
    await page.getByTestId('start-ai-research-button').click();
    await expect(page.getByTestId('ai-research-content')).toBeVisible({ timeout: 30000 });

    // Navigate to slides step
    await page.getByTestId('step-nav-slides').click();

    // Try to use wizard before slides are generated
    const wizardInput = page.getByTestId('wizard-input');
    if (await wizardInput.isVisible()) {
      await wizardInput.fill('Improve this slide');
      await page.getByTestId('wizard-send-button').click();
      
      // Should get a helpful error message instead of a 400 error
      await expect(page.getByTestId('wizard-message-assistant').last()).toContainText('Wizard support for this step is coming soon');
    }
  });

  test('should use adaptive polling intervals', async ({ page }) => {
    const name = `Polling Test ${Date.now()}`;
    const topic = 'Test topic for polling optimization';

    // Track API requests to verify polling behavior
    const apiRequests: any[] = [];
    page.on('request', request => {
      if (request.url().includes('/presentations/') && request.method() === 'GET') {
        apiRequests.push({
          url: request.url(),
          timestamp: Date.now()
        });
      }
    });

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);

    // Wait for initial polling to stabilize
    await page.waitForTimeout(10000);

    const initialRequestCount = apiRequests.length;
    console.log(`Initial request count: ${initialRequestCount}`);

    // Start research to trigger active polling
    await page.getByTestId('start-ai-research-button').click();

    // Wait for research to complete and polling to adapt
    await expect(page.getByTestId('ai-research-content')).toBeVisible({ timeout: 30000 });

    // Wait for polling to slow down after completion
    await page.waitForTimeout(15000);

    const finalRequestCount = apiRequests.length;
    console.log(`Final request count: ${finalRequestCount}`);

    // Verify polling adapted (should not be excessive)
    const requestsPerSecond = (finalRequestCount - initialRequestCount) / 25; // 25 seconds total
    console.log(`Requests per second: ${requestsPerSecond}`);
    
    // Should be less than 1 request per second on average (adaptive polling)
    expect(requestsPerSecond).toBeLessThan(1);
  });

  test('should show proper error messages for modify endpoint', async ({ page }) => {
    const apiUrl = getApiUrl();
    
    // Test direct API call to modify endpoint without proper data
    const response = await page.request.post(`${apiUrl}/presentations/999/modify`, {
      data: {
        prompt: 'Test prompt'
      }
    });

    expect(response.status()).toBe(400);
    const responseBody = await response.json();
    expect(responseBody.detail).toContain('Research step not completed');
  });
}); 