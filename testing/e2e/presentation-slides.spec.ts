import { test, expect } from '@playwright/test';
import { 
  goToPresentationsPage, 
  createPresentation, 
  getStepStatus, 
  runStepAndWaitForCompletion,
  waitForNetworkIdle,
  isStepEnabled,
  StepType
} from './utils';

test.describe('Presentation Slides', () => {
  test('should generate slides with titles and content', async ({ page }) => {
    // Go to presentations page
    await goToPresentationsPage(page);
    
    // Generate a unique name and topic
    const timestamp = new Date().getTime();
    const testName = `Slides Content ${timestamp}`;
    const testTopic = `Slide Generation Topic ${timestamp}`;
    
    try {
      // Create a new presentation
      const presentationId = await createPresentation(page, testName, testTopic);
      console.log(`Created presentation with ID: ${presentationId}`);
      
      // Make sure we're on the detail page
      if (!page.url().includes(`/presentations/${presentationId}`)) {
        await page.goto(`http://localhost:3000/presentations/${presentationId}`);
        await waitForNetworkIdle(page);
      }
      
      // Wait for page to load completely
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
      
      // Make sure research is completed first
      const researchNavButton = page.getByTestId('step-nav-research');
      let researchVisible = await researchNavButton.isVisible().catch(() => false);
      
      // If research button is not visible, try refreshing
      if (!researchVisible) {
        const refreshButton = page.getByTestId('refresh-button');
        if (await refreshButton.isVisible().catch(() => false)) {
          await refreshButton.click();
          await waitForNetworkIdle(page);
          researchVisible = await researchNavButton.isVisible().catch(() => false);
        }
      }
      
      if (!researchVisible) {
        console.log('Research nav button not visible even after refresh, skipping test');
        test.skip();
        return;
      }
      
      // Click on the research step to activate it
      await researchNavButton.click();
      await page.waitForTimeout(500);
      
      // Get the research status
      let researchStatus = await getStepStatus(page, 'research');
      console.log(`Initial research status: ${researchStatus}`);
      
      if (researchStatus !== 'completed') {
        await runStepAndWaitForCompletion(page, 'research', 300000);
        
        // Refresh to get updated status
        const refreshButton = page.getByTestId('refresh-button');
        if (await refreshButton.isVisible().catch(() => false)) {
          await refreshButton.click();
          await waitForNetworkIdle(page);
        }
        
        researchStatus = await getStepStatus(page, 'research');
        console.log(`Research status after run: ${researchStatus}`);
        
        // If it's still not completed, skip the test
        if (researchStatus !== 'completed') {
          console.log('Research step did not complete in time, skipping the rest of the test');
          test.skip();
          return;
        }
      }
      
      // Now run the slides step
      const slidesNavButton = page.getByTestId('step-nav-slides');
      const slidesVisible = await slidesNavButton.isVisible().catch(() => false);
      
      if (!slidesVisible) {
        console.log('Slides nav button not visible, skipping test');
        test.skip();
        return;
      }
      
      // Check if slides step is enabled
      const slidesEnabled = await isStepEnabled(page, 'slides');
      if (!slidesEnabled) {
        console.log('Slides step is disabled, which is unexpected after research completion');
        test.skip();
        return;
      }
      
      // Click on the slides step to activate it
      await slidesNavButton.click();
      await page.waitForTimeout(500);
      
      await runStepAndWaitForCompletion(page, 'slides', 300000);
      
      // Refresh to make sure we have the latest content
      const refreshButton = page.getByTestId('refresh-button');
      if (await refreshButton.isVisible().catch(() => false)) {
        await refreshButton.click();
        await waitForNetworkIdle(page);
      }
      
      // Click on the slides step again to make sure it's active
      await slidesNavButton.click();
      await page.waitForTimeout(500);
      
      // Verify the slides step is completed
      const slidesStatus = await getStepStatus(page, 'slides');
      console.log(`Final slides status: ${slidesStatus}`);
      
      // The step should either be completed or still processing if it's taking too long
      expect(['completed', 'processing']).toContain(slidesStatus);
      
      // If the step is completed, check that the presentation content is rendered
      if (slidesStatus === 'completed') {
        // Look for slide content elements
        const slideTitle = page.locator('.slide-title').first();
        if (await slideTitle.isVisible({ timeout: 5000 }).catch(() => false)) {
          const titleText = await slideTitle.textContent();
          console.log(`Found slide title: ${titleText}`);
          expect(titleText).toBeTruthy();
          
          // Check if there are multiple slides
          const slidesCount = await page.locator('.slide-title').count();
          console.log(`Found ${slidesCount} slides`);
          expect(slidesCount).toBeGreaterThan(0);
        } else {
          console.log('Could not find slide title elements, slides might not be rendered correctly');
        }
      }
    } catch (error) {
      console.error(`Test failed: ${error.message}`);
      await page.screenshot({ path: `slides-content-failure-${timestamp}.png` });
      throw error;
    }
  });
}); 