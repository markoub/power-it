import { test, expect } from '@playwright/test';
import { 
  goToPresentationsPage, 
  createPresentation, 
  getStepStatus,
  isStepEnabled,
  getStepDisabledTooltip,
  runStepAndWaitForCompletion,
  verifyStepDependencies,
  waitForNetworkIdle,
  StepType
} from './utils';

// Set longer timeout for these tests as they interact with the real backend
test.setTimeout(120000);

test.describe('Step Dependencies and Order', () => {
  // Make sure both frontend and backend servers are running before tests
  test.beforeEach(async ({ page }) => {
    // Try to navigate to the home page to verify servers are running
    try {
      await page.goto('http://localhost:3000');
      await page.waitForLoadState('networkidle', { timeout: 5000 });
    } catch (error) {
      test.skip('Frontend server not running at http://localhost:3000');
    }

    // Check for backend server
    try {
      await page.goto('http://localhost:8000/healthcheck');
      await page.waitForTimeout(1000);
      // If we get a 404 or 500, the server might be running but without healthcheck endpoint
      const status = await page.evaluate(() => {
        return window.location.href;
      });
      if (!status.includes('localhost:8000')) {
        test.skip('Backend server not running at http://localhost:8000');
      }
    } catch (error) {
      // Still try to proceed as backend might be running but without healthcheck
      console.log('Backend healthcheck failed, but continuing test');
    }

    // Go back to frontend
    await page.goto('http://localhost:3000');
  });

  test('should enforce step dependencies and show tooltips for disabled steps', async ({ page }) => {
    // Set a longer timeout for this test
    test.setTimeout(300000); // 5 minutes
    
    console.log('Starting step dependencies test');
    
    // Go to presentations page
    await goToPresentationsPage(page);
    
    // Generate a unique name and topic
    const timestamp = new Date().getTime();
    const testName = `Dependencies Test ${timestamp}`;
    const testTopic = `Dependencies Topic ${timestamp}`;
    
    try {
      // Create a new presentation
      const presentationId = await createPresentation(page, testName, testTopic);
      console.log(`Created presentation with ID: ${presentationId}`);
      
      // Make sure we're on the detail page
      if (!page.url().includes(`/presentations/${presentationId}`)) {
        await page.goto(`http://localhost:3000/presentations/${presentationId}`);
        await waitForNetworkIdle(page);
      }
      
      // Test initial state - Research should be enabled, other steps disabled
      // Research should be enabled by default
      const researchEnabled = await isStepEnabled(page, 'research');
      expect(researchEnabled).toBeTruthy();
      
      // At the beginning, other steps should be disabled with appropriate tooltips
      const steps: StepType[] = ['slides', 'images', 'compiled', 'pptx'];
      
      // Research step should be pending or processing
      const researchStatus = await getStepStatus(page, 'research');
      expect(['pending', 'processing']).toContain(researchStatus);
      
      // Verify disabled states and tooltips for each step
      for (const step of steps) {
        const enabled = await isStepEnabled(page, step);
        const tooltip = await getStepDisabledTooltip(page, step);
        
        if (step === 'slides') {
          // For the slides step, it depends on the research status
          if (researchStatus === 'completed') {
            expect(enabled).toBeTruthy();
          } else {
            expect(enabled).toBeFalsy();
            expect(tooltip).toContain('Research must be completed');
          }
        } else {
          // Other steps should be disabled
          expect(enabled).toBeFalsy();
          if (step === 'images') {
            expect(tooltip).toContain('Slides must be completed');
          } else if (step === 'compiled') {
            expect(tooltip).toContain('Images must be completed');
          } else if (step === 'pptx') {
            expect(tooltip).toContain('Compilation must be completed');
          }
        }
      }
      
      // Run research step to completion (if not already)
      await runStepAndWaitForCompletion(page, 'research', 300000);
      
      // Refresh to ensure state is updated
      await page.getByTestId('refresh-button').click();
      await waitForNetworkIdle(page);
      
      // After research completes, slides should be enabled
      const slidesEnabled = await isStepEnabled(page, 'slides');
      expect(slidesEnabled).toBeTruthy();
      
      // But images, compiled, and pptx should still be disabled
      expect(await isStepEnabled(page, 'images')).toBeFalsy();
      expect(await isStepEnabled(page, 'compiled')).toBeFalsy();
      expect(await isStepEnabled(page, 'pptx')).toBeFalsy();
      
      // Run slides step
      await runStepAndWaitForCompletion(page, 'slides', 300000);
      
      // Refresh to ensure state is updated
      await page.getByTestId('refresh-button').click();
      await waitForNetworkIdle(page);
      
      // After slides completes, images should be enabled
      const imagesEnabled = await isStepEnabled(page, 'images');
      expect(imagesEnabled).toBeTruthy();
      
      // But compiled and pptx should still be disabled
      expect(await isStepEnabled(page, 'compiled')).toBeFalsy();
      expect(await isStepEnabled(page, 'pptx')).toBeFalsy();
      
      // Verify all dependencies are correctly enforced
      const dependenciesCorrect = await verifyStepDependencies(page);
      expect(dependenciesCorrect).toBeTruthy();
      
    } catch (error) {
      console.error(`Test failed: ${error.message}`);
      await page.screenshot({ path: `step-dependencies-failure-${timestamp}.png` });
      throw error;
    }
  });

  test('should show correct loading states when steps are running', async ({ page }) => {
    // Set a longer timeout for this test
    test.setTimeout(300000); // 5 minutes
    
    console.log('Starting loading states test');
    
    // Go to presentations page
    await goToPresentationsPage(page);
    
    // Generate a unique name and topic
    const timestamp = new Date().getTime();
    const testName = `Loading States Test ${timestamp}`;
    const testTopic = `Loading Topic ${timestamp}`;
    
    try {
      // Create a new presentation
      const presentationId = await createPresentation(page, testName, testTopic);
      console.log(`Created presentation with ID: ${presentationId}`);
      
      // Make sure we're on the detail page
      if (!page.url().includes(`/presentations/${presentationId}`)) {
        await page.goto(`http://localhost:3000/presentations/${presentationId}`);
        await waitForNetworkIdle(page);
      }
      
      // Click on the research step to select it
      await page.getByTestId('step-nav-research').click();
      await waitForNetworkIdle(page);
      
      // Locate the run button and click it
      const runButton = page.getByTestId('run-research-button');
      
      // If run button is visible and not disabled, click it
      if (await runButton.isVisible() && !(await runButton.isDisabled())) {
        // Click the button and verify spinner appears
        await runButton.click();
        
        // Verify the spinner is shown in the button (wait a bit for UI update)
        await page.waitForTimeout(1000);
        
        // Check if the spinner is visible in the button
        const spinner = runButton.locator('svg[class*="animate-spin"]');
        await expect(spinner).toBeVisible();
        
        // Expect "Running..." text inside button
        const buttonText = await runButton.textContent();
        expect(buttonText).toContain('Running');
        
        // Wait for the state to update to processing
        const status = await getStepStatus(page, 'research');
        expect(['processing', 'completed']).toContain(status);
        
        // Click on the step content area to verify the spinner is shown in the main content
        const contentSpinner = page.locator('div[class*="shadow-md"] svg[class*="animate-spin"]');
        if (status === 'processing') {
          await expect(contentSpinner).toBeVisible();
        }
      }
      
    } catch (error) {
      console.error(`Test failed: ${error.message}`);
      await page.screenshot({ path: `loading-states-failure-${timestamp}.png` });
      throw error;
    }
  });
}); 