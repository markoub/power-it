import { test, expect } from '@playwright/test';
import { navigateToTestPresentation, isStepEnabled, getStepStatus } from './utils';

/**
 * Test presentation workflow steps using pre-seeded data
 */

test.describe('Presentation Workflow', () => {
  test('should navigate between presentation steps', async ({ page }) => {
    // Use a fresh presentation that already has AI Research selected
    const freshPresentation = await navigateToTestPresentation(page, 'fresh', 0);
    
    // Verify we're on the edit page
    expect(page.url()).toContain('/edit/');
    
    // Should see the AI research interface
    await expect(page.getByTestId('ai-research-interface')).toBeVisible({ timeout: 5000 });
    
    // Should see the topic input with the pre-seeded topic
    const topicInput = page.getByTestId('topic-input');
    await expect(topicInput).toBeVisible();
    await expect(topicInput).toHaveValue(freshPresentation.topic);
    
    // Should see the start research button
    await expect(page.getByTestId('start-ai-research-button')).toBeVisible();
    
    // Verify step navigation is available
    await expect(page.getByTestId('step-nav-research')).toBeVisible();
    await expect(page.getByTestId('step-nav-slides')).toBeVisible();
    await expect(page.getByTestId('step-nav-illustration')).toBeVisible();
    await expect(page.getByTestId('step-nav-compiled')).toBeVisible();
    await expect(page.getByTestId('step-nav-pptx')).toBeVisible();
    
    // Research step should be active (not completed)
    const researchStatus = await getStepStatus(page, 'research');
    expect(researchStatus).not.toBe('completed');
    
    // Slides step should be disabled (since research is not completed)
    const slidesEnabled = await isStepEnabled(page, 'slides');
    expect(slidesEnabled).toBe(false);
  });
  
  test('should show correct step states for research-complete presentation', async ({ page }) => {
    // Use a presentation with research already completed
    const researchComplete = await navigateToTestPresentation(page, 'research_complete', 1); // Use second one to avoid conflicts
    
    // Verify research step is completed
    const researchStatus = await getStepStatus(page, 'research');
    expect(researchStatus).toBe('completed');
    
    // Check if slides are already generated
    const slidesStatus = await getStepStatus(page, 'slides');
    
    if (slidesStatus === 'completed') {
      // If slides are already generated, verify we can see them
      await page.getByTestId('step-nav-slides').click();
      
      // Should see the slides content
      await expect(page.getByTestId('slide-1')).toBeVisible();
      await expect(page.getByTestId('preview-button')).toBeVisible();
    } else {
      // If slides are not generated, check for generation interface
      const slidesEnabled = await isStepEnabled(page, 'slides');
      expect(slidesEnabled).toBe(true);
      
      // Click on slides step
      await page.getByTestId('step-nav-slides').click();
      
      // Should see slides generation interface
      await expect(page.getByTestId('run-slides-button')).toBeVisible();
    }
  });
  
  test('should show correct step states for complete presentation', async ({ page }) => {
    // Use a fully complete presentation
    const completePresentation = await navigateToTestPresentation(page, 'complete', 0);
    
    // All steps should be completed
    expect(await getStepStatus(page, 'research')).toBe('completed');
    expect(await getStepStatus(page, 'slides')).toBe('completed');
    expect(await getStepStatus(page, 'illustration')).toBe('completed');
    expect(await getStepStatus(page, 'compiled')).toBe('completed');
    expect(await getStepStatus(page, 'pptx')).toBe('completed');
    
    // Should be able to navigate to any step
    await page.getByTestId('step-nav-pptx').click();
    
    // Should see download button for completed presentation
    await expect(page.getByTestId('download-pptx-button')).toBeVisible();
  });
});
